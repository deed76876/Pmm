# Generated by Django 2.1.7 on 2019-03-04 21:39


import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ServiceType",
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
                ("title", models.CharField(max_length=40, verbose_name="title")),
                (
                    "billing_per_hour",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="billing per hour",
                    ),
                ),
                (
                    "position",
                    models.PositiveIntegerField(default=0, verbose_name="position"),
                ),
            ],
            options={
                "verbose_name": "service type",
                "verbose_name_plural": "service types",
                "ordering": ("position", "id"),
            },
        )
    ]
