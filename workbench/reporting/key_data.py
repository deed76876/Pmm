from collections import defaultdict

from django.db import connections
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear

from workbench.invoices.models import Invoice
from workbench.logbook.models import LoggedCost, LoggedHours
from workbench.projects.models import Project, Service
from workbench.tools.models import Z


def projects_with_service_hours(project_ids):
    projects = Project.objects.filter(id__in=project_ids)
    service_hours = defaultdict(lambda: Z)

    service_hours.update(
        (row["project"], row["service_hours__sum"])
        for row in Service.objects.order_by()
        .filter(project__in=project_ids)
        .values("project")
        .annotate(Sum("service_hours"))
    )

    return projects, service_hours


def logged_hours_by_project_month(project_ids):
    hours = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: Z)))
    for row in (
        LoggedHours.objects.order_by()
        .values("service__project")
        .annotate(
            year=ExtractYear("rendered_on"),
            month=ExtractMonth("rendered_on"),
            hours=Sum("hours"),
        )
    ):
        hours[row["service__project"]][row["year"]][row["month"]] = row["hours"]
    return hours


class GreenHours:
    def __init__(self, **kwargs):
        self.profitable = kwargs.get("profitable", Z)
        self.overdrawn = kwargs.get("overdrawn", Z)
        self.maintenance = kwargs.get("maintenance", Z)
        self.internal = kwargs.get("internal", Z)

    def __repr__(self):
        return (
            "<GreenHours profitable=%s overdrawn=%s maintenance=%s internal=%s"
            " total=%s green=%d%%>"
            % (
                self.profitable,
                self.overdrawn,
                self.maintenance,
                self.internal,
                self.total,
                self.green,
            )
        )

    def __iadd__(self, other):
        self.profitable += other.profitable
        self.overdrawn += other.overdrawn
        self.maintenance += other.maintenance
        self.internal += other.internal
        return self

    @property
    def total(self):
        return self.profitable + self.overdrawn + self.maintenance + self.internal

    @property
    def green(self):
        return (
            100 * (self.profitable + self.maintenance) // self.total
            if self.total
            else None
        )


def green_hours(date_range):
    project_ids = set(
        LoggedHours.objects.order_by()
        .filter(rendered_on__range=date_range)
        .values_list("service__project", flat=True)
        .distinct()
    )

    projects, service_hours = projects_with_service_hours(project_ids)
    logged_hours = logged_hours_by_project_month(project_ids)

    data = defaultdict(
        lambda: {"year": GreenHours(), "months": defaultdict(GreenHours)}
    )

    until = (date_range[1].year, date_range[1].month)

    for project in projects:
        for year, month_data in sorted(logged_hours[project.id].items()):
            for month, hours in sorted(month_data.items()):
                if year < date_range[0].year:
                    service_hours[project.id] -= hours
                    continue
                elif (year, month) > until:
                    continue

                remaining = service_hours[project.id] - hours
                if project.type == project.INTERNAL:
                    gh = GreenHours(internal=hours)
                elif project.type == project.MAINTENANCE:
                    gh = GreenHours(maintenance=hours)
                elif service_hours[project.id] < 0:
                    gh = GreenHours(overdrawn=hours)
                elif remaining >= 0:
                    gh = GreenHours(profitable=hours)
                else:
                    gh = GreenHours(
                        profitable=service_hours[project.id],
                        overdrawn=hours - service_hours[project.id],
                    )

                data[year]["year"] += gh
                data[year]["months"][month] += gh

                service_hours[project.id] -= hours

    return data


def invoiced_by_month(date_range):
    invoiced = defaultdict(lambda: defaultdict(lambda: Z))
    for row in (
        Invoice.objects.valid()
        .order_by()
        .filter(invoiced_on__range=date_range)
        .annotate(year=ExtractYear("invoiced_on"), month=ExtractMonth("invoiced_on"))
        .values("year", "month")
        .annotate(subtotal_sum=Sum("subtotal"), discount_sum=Sum("discount"))
    ):
        invoiced[row["year"]][row["month"]] += row["subtotal_sum"] - row["discount_sum"]

    for row in (
        LoggedCost.objects.order_by()
        .filter(rendered_on__range=date_range)
        .filter(third_party_costs__isnull=False)
        .annotate(year=ExtractYear("rendered_on"), month=ExtractMonth("rendered_on"))
        .values("year", "month")
        .annotate(Sum("third_party_costs"))
    ):
        invoiced[row["year"]][row["month"]] -= row["third_party_costs__sum"]

    return invoiced


def accruals_by_date():
    accruals = {}
    with connections["default"].cursor() as cursor:
        cursor.execute(
            """\
SELECT
    cutoff_date,
    SUM((i.subtotal - i.discount) * (100 - a.work_progress) / 100)
FROM accruals_accrual a
LEFT JOIN invoices_invoice i ON i.id=a.invoice_id
GROUP BY cutoff_date
ORDER BY cutoff_date
"""
        )

        for row in cursor:
            # Overwrite earlier accruals if a month has more than one cutoff date
            accruals[(row[0].year, row[0].month)] = {"accrual": row[1], "delta": None}

    dates = list(sorted(accruals))
    for this, next in zip(dates, dates[1:]):
        accruals[next]["delta"] = accruals[next]["accrual"] - accruals[this]["accrual"]

    return accruals


def invoiced_corrected(date_range):
    accruals = accruals_by_date()
    margin = invoiced_by_month(date_range)
    for year in margin:
        for month in margin[year]:
            accrual = accruals.get((year, month))
            if accrual and accrual["delta"]:
                margin[year][month] -= accrual["delta"]

    # from pprint import pprint

    # pprint(accruals)
    # pprint(margin)

    return margin