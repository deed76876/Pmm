# Generated by Django 2.1.7 on 2019-03-04 21:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("logbook", "0001_initial"),
        ("projects", "0001_initial"),
        ("invoices", "0002_invoice_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="loggedhours",
            name="service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="loggedhours",
                to="projects.Service",
                verbose_name="service",
            ),
        ),
        migrations.AddField(
            model_name="loggedcost",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
                verbose_name="created by",
            ),
        ),
        migrations.AddField(
            model_name="loggedcost",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="invoices.Invoice",
                verbose_name="invoice",
            ),
        ),
        migrations.AddField(
            model_name="loggedcost",
            name="project",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="loggedcosts",
                to="projects.Project",
                verbose_name="project",
            ),
        ),
        migrations.AddField(
            model_name="loggedcost",
            name="service",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="loggedcosts",
                to="projects.Service",
                verbose_name="service",
            ),
        ),
        migrations.AddIndex(
            model_name="loggedhours",
            index=models.Index(
                fields=["-rendered_on"], name="logbook_log_rendere_ea492e_idx"
            ),
        ),
    ]
