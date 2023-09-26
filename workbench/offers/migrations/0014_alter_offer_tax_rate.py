# Generated by Django 4.2.4 on 2023-09-26 09:00

from decimal import Decimal

import django.core.validators
from django.db import migrations, models

import workbench.tools.models


class Migration(migrations.Migration):
    dependencies = [
        ("offers", "0013_alter_offer_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offer",
            name="tax_rate",
            field=models.DecimalField(
                choices=[
                    (Decimal("8.10"), "8.1% (2024 and onwards)"),
                    (Decimal("7.70"), "7.7% (until the end of 2023)"),
                ],
                decimal_places=2,
                default=workbench.tools.models.default_tax_rate,
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="tax rate",
            ),
        ),
    ]
