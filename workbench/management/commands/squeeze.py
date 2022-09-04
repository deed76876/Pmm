import datetime as dt
from collections import defaultdict
from itertools import chain

from django.core.management import BaseCommand
from django.db.models import Sum
from django.utils.translation import activate

from workbench.accounts.models import User
from workbench.invoices.models import Invoice, ProjectedInvoice
from workbench.logbook.models import LoggedHours
from workbench.offers.models import Offer
from workbench.projects.models import Project, Service
from workbench.reporting.green_hours import green_hours
from workbench.tools.formats import Z1, Z2, local_date_format
from workbench.tools.xlsx import WorkbenchXLSXDocument


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=dt.date.today().year,
            help="The year (default: %(default)s)",
        )

    def handle(self, **options):
        date_range = [dt.date(options["year"], 1, 1), dt.date(options["year"], 12, 31)]

        activate("de")

        projects = defaultdict(
            lambda: {
                "invoiced": Z2,
                "projected": Z2,
                "offered": Z2,
                "hours_logged": Z1,
                "hours_offered": Z1,
                "hours_in_range_by_user": {},
            }
        )
        users = defaultdict(
            lambda: {
                "margin": Z2,
                "hours_in_range": Z1,
            }
        )
        user_dict = {u.id: u for u in User.objects.all()}

        logged = (
            LoggedHours.objects.filter(rendered_on__range=date_range)
            .order_by()
            .values("rendered_by", "service__project")
            .annotate(Sum("hours"))
        )
        for row in logged:
            p = projects[row["service__project"]]
            u = user_dict[row["rendered_by"]]

            p["hours_in_range_by_user"][u] = row["hours__sum"]
            users[u]["hours_in_range"] += row["hours__sum"]

        total_hours = (
            LoggedHours.objects.order_by()
            .filter(service__project__in=projects.keys())
            .values("service__project")
            .annotate(Sum("hours"))
        )
        for row in total_hours:
            projects[row["service__project"]]["hours_logged"] = row["hours__sum"]

        offered_hours = (
            Service.objects.order_by()
            .budgeted()
            .filter(project__in=projects.keys())
            .values("project")
            .annotate(Sum("service_hours"))
        )
        for row in offered_hours:
            projects[row["project"]]["hours_offered"] = row["service_hours__sum"]

        invoiced_per_project = (
            Invoice.objects.invoiced()
            .filter(project__in=projects.keys())
            .order_by()
            .values("project")
            .annotate(Sum("total_excl_tax"), Sum("third_party_costs"))
        )
        for row in invoiced_per_project:
            projects[row["project"]]["invoiced"] = (
                row["total_excl_tax__sum"] - row["third_party_costs__sum"]
            )

        for pi in ProjectedInvoice.objects.filter(
            project__in=projects.keys(), project__closed_on__isnull=True
        ):
            projects[pi.project_id]["projected"] += pi.gross_margin

        for offer in Offer.objects.accepted().filter(
            project__in=projects.keys(), project__closed_on__isnull=True
        ):
            projects[offer.project_id]["offered"] += offer.total_excl_tax

        for project_id, project in Project.objects.in_bulk(projects.keys()).items():
            projects[project_id]["project"] = project

        all_users = sorted(users.keys())

        header = [
            [
                f"Squeeze {local_date_format(date_range[0])} - {local_date_format(date_range[1])}"
            ]
        ]

        projects_table = [
            [
                "Projekt",
                "Offeriert (nur offene Projekte)",
                "Geplante Rechnungen (nur offene Projekte)",
                "Verrechnet minus Fremdkosten",
                "Massgeblicher Umsatz",
                "Offerierte Stunden",
                "Erfasste Stunden",
                "Massgebliche Stunden",
                "Ansatz",
            ]
            + list(chain.from_iterable((str(u), "") for u in all_users)),
            [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
            + list(chain.from_iterable(("Stunden", "Umsatz") for _u in all_users)),
        ] + sorted(
            (project_row(row, all_users, users=users) for row in projects.values()),
            key=lambda row: row[4],
            reverse=True,
        )

        gh = dict(green_hours(date_range, users=users.keys()))

        users_table = [
            [
                "User",
                "Massgeblicher Umsatz",
                "Massgebliche Stunden",
                "Ansatz",
                "",
                "Grüne Stunden",
                "Rote Stunden",
                "Wartung",
                "Intern",
                "Total",
                "Prozent grün",
                "",
                "Prozent Kundenjobs",
            ],
        ] + sorted(
            (
                [
                    user,
                    row["margin"],
                    row["hours_in_range"],
                    row["margin"] / row["hours_in_range"],
                    "",
                    gh[user]["green"],
                    gh[user]["red"],
                    gh[user]["maintenance"],
                    gh[user]["internal"],
                    gh[user]["total"],
                    gh[user]["percentage"],
                    "",
                    100 - 100 * gh[user]["internal"] / gh[user]["total"],
                ]
                for user, row in users.items()
            ),
            key=lambda row: row[3],
            reverse=True,
        )

        xlsx = WorkbenchXLSXDocument()
        xlsx.add_sheet("Users")
        xlsx.table(None, header + users_table)
        xlsx.add_sheet("Projekte")
        xlsx.table(None, header + projects_table)
        xlsx.workbook.save(f"squeeze-{options['year']}.xlsx")


def project_row(row, all_users, *, users):
    margin = max((row["offered"], row["projected"], row["invoiced"]))
    hours = max(
        (
            row["hours_offered"],
            row["hours_logged"],
        )
    )

    def user_cells(u):
        if by_user := row["hours_in_range_by_user"].get(u):
            user_margin = by_user / hours * margin
            users[u]["margin"] += user_margin
            return (by_user, user_margin)
        return ("", "")

    return [
        row["project"],
        row["offered"],
        row["projected"],
        row["invoiced"],
        margin,
        row["hours_offered"],
        row["hours_logged"],
        hours,
        margin / hours,
    ] + list(chain.from_iterable(user_cells(u) for u in all_users))
