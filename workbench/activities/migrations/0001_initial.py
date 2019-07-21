# Generated by Django 2.1.7 on 2019-03-04 21:39

from decimal import Decimal

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contacts", "0001_initial"),
        ("deals", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Activity",
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
                ("title", models.CharField(max_length=200, verbose_name="title")),
                (
                    "due_on",
                    models.DateField(blank=True, null=True, verbose_name="due on"),
                ),
                ("time", models.TimeField(blank=True, null=True, verbose_name="time")),
                (
                    "duration",
                    models.DecimalField(
                        blank=True,
                        decimal_places=1,
                        help_text="Duration in hours (if applicable).",
                        max_digits=4,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="duration",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="created at"
                    ),
                ),
                (
                    "completed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="completed at"
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="activities",
                        to="contacts.Person",
                        verbose_name="contact",
                    ),
                ),
                (
                    "deal",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="activities",
                        to="deals.Deal",
                        verbose_name="deal",
                    ),
                ),
                (
                    "owned_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="activities",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="responsible",
                    ),
                ),
            ],
            options={
                "verbose_name": "activity",
                "verbose_name_plural": "activities",
                "ordering": ("due_on",),
            },
        )
    ]
