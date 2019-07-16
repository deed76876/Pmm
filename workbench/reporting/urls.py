from django.conf.urls import url

from workbench.awt.views import ReportView
from workbench.reporting.views import (
    hours_per_customer_view,
    key_data_view,
    logged_hours_by_circle_view,
    monthly_invoicing_view,
    open_items_list,
    overdrawn_projects_view,
)


urlpatterns = [
    url(r"^annual-working-time/$", ReportView.as_view(), name="awt_year_report"),
    url(
        r"^monthly-invoicing/$", monthly_invoicing_view, name="report_monthly_invoicing"
    ),
    url(
        r"^overdrawn-projects/$",
        overdrawn_projects_view,
        name="report_overdrawn_projects",
    ),
    url(r"^open-items-list/$", open_items_list, name="report_open_items_list"),
    url(
        r"^logged-hours-by-circle/$",
        logged_hours_by_circle_view,
        name="report_logged_hours_by_circle",
    ),
    url(r"^key-data/$", key_data_view, name="report_key_data"),
    url(
        r"^hours-per-customer/$",
        hours_per_customer_view,
        name="report_hours_per_customer",
    ),
]