# Generated by Django 2.1.7 on 2019-03-08 16:52

from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("invoices", "0005_auto_20190307_0925")]

    operations = [
        migrations.CreateModel(
            name="CreditEntry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reference_number",
                    models.CharField(
                        max_length=40, unique=True, verbose_name="reference number"
                    ),
                ),
                ("value_date", models.DateField(verbose_name="value date")),
                (
                    "total",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="total",
                    ),
                ),
                (
                    "payment_notice",
                    models.CharField(
                        blank=True, max_length=1000, verbose_name="payment notice"
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="notes")),
                (
                    "invoice",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="invoices.Invoice",
                        verbose_name="invoice",
                    ),
                ),
            ],
            options={
                "verbose_name": "credit entry",
                "verbose_name_plural": "credit entries",
                "ordering": ["-value_date", "-pk"],
            },
        )
    ]
