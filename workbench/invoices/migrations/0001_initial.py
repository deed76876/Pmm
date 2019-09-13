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
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
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
                    "subtotal",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="subtotal",
                    ),
                ),
                (
                    "discount",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="discount",
                    ),
                ),
                (
                    "liable_to_vat",
                    models.BooleanField(
                        default=True,
                        help_text="For example invoices to foreign institutions are not liable to VAT.",
                        verbose_name="liable to VAT",
                    ),
                ),
                (
                    "tax_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("7.7"),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="tax rate",
                    ),
                ),
                (
                    "total",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="total",
                    ),
                ),
                (
                    "invoiced_on",
                    models.DateField(blank=True, null=True, verbose_name="invoiced on"),
                ),
                (
                    "due_on",
                    models.DateField(blank=True, null=True, verbose_name="due on"),
                ),
                (
                    "closed_on",
                    models.DateField(
                        blank=True,
                        help_text="Payment date for paid invoices, date of replacement or cancellation otherwise.",
                        null=True,
                        verbose_name="closed on",
                    ),
                ),
                ("title", models.CharField(max_length=200, verbose_name="title")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="created at"
                    ),
                ),
                (
                    "status",
                    models.PositiveIntegerField(
                        choices=[
                            (10, "In preparation"),
                            (20, "Sent"),
                            (30, "Reminded"),
                            (40, "Paid"),
                            (50, "Canceled"),
                            (60, "Replaced"),
                        ],
                        default=10,
                        verbose_name="status",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("fixed", "Fixed amount"),
                            ("down-payment", "Down payment"),
                            ("services", "Services"),
                        ],
                        max_length=20,
                        verbose_name="type",
                    ),
                ),
                (
                    "down_payment_total",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="down payment total",
                    ),
                ),
                ("postal_address", models.TextField(verbose_name="postal address")),
                ("_code", models.IntegerField(verbose_name="code")),
                (
                    "payment_notice",
                    models.TextField(blank=True, verbose_name="payment notice"),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contacts.Person",
                        verbose_name="contact",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contacts.Organization",
                        verbose_name="customer",
                    ),
                ),
                (
                    "down_payment_applied_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="down_payment_invoices",
                        to="invoices.Invoice",
                        verbose_name="down payment applied to",
                    ),
                ),
                (
                    "owned_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="responsible",
                    ),
                ),
            ],
            options={
                "verbose_name": "invoice",
                "verbose_name_plural": "invoices",
                "ordering": ("-id",),
            },
        )
    ]
