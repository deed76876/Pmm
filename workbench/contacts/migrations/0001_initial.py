# Generated by Django 2.1.7 on 2019-03-04 21:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="EmailAddress",
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
                    "type",
                    models.CharField(
                        max_length=40, verbose_name="type", default="work"
                    ),
                ),
                (
                    "weight",
                    models.SmallIntegerField(
                        default=0, editable=False, verbose_name="weight"
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="email")),
            ],
            options={
                "verbose_name": "email address",
                "verbose_name_plural": "email addresses",
                "ordering": ("-weight", "id"),
            },
        ),
        migrations.CreateModel(
            name="Group",
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
                ("title", models.CharField(max_length=100, verbose_name="title")),
            ],
            options={
                "verbose_name": "group",
                "verbose_name_plural": "groups",
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="Organization",
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
                ("name", models.TextField(verbose_name="name")),
                ("notes", models.TextField(blank=True, verbose_name="notes")),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        related_name="_organization_groups_+",
                        to="contacts.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "primary_contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="primary contact",
                    ),
                ),
            ],
            options={
                "verbose_name": "organization",
                "verbose_name_plural": "organizations",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="Person",
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
                    "given_name",
                    models.CharField(max_length=100, verbose_name="given name"),
                ),
                (
                    "family_name",
                    models.CharField(max_length=100, verbose_name="family name"),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True,
                        help_text="E.g. Sir/Madam",
                        max_length=100,
                        verbose_name="address",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="notes")),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        related_name="_person_groups_+",
                        to="contacts.Group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="people",
                        to="contacts.Organization",
                        verbose_name="organization",
                    ),
                ),
                (
                    "primary_contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="primary contact",
                    ),
                ),
            ],
            options={
                "verbose_name": "person",
                "verbose_name_plural": "people",
                "ordering": ["given_name", "family_name"],
            },
        ),
        migrations.CreateModel(
            name="PhoneNumber",
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
                    "type",
                    models.CharField(
                        max_length=40, verbose_name="type", default="work"
                    ),
                ),
                (
                    "weight",
                    models.SmallIntegerField(
                        default=0, editable=False, verbose_name="weight"
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(max_length=100, verbose_name="phone number"),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="phonenumbers",
                        to="contacts.Person",
                        verbose_name="person",
                    ),
                ),
            ],
            options={
                "verbose_name": "phone number",
                "verbose_name_plural": "phone numbers",
                "ordering": ("-weight", "id"),
            },
        ),
        migrations.CreateModel(
            name="PostalAddress",
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
                    "type",
                    models.CharField(
                        max_length=40, verbose_name="type", default="work"
                    ),
                ),
                (
                    "weight",
                    models.SmallIntegerField(
                        default=0, editable=False, verbose_name="weight"
                    ),
                ),
                ("street", models.CharField(max_length=100, verbose_name="street")),
                (
                    "house_number",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="house number"
                    ),
                ),
                (
                    "address_suffix",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="address suffix"
                    ),
                ),
                (
                    "postal_code",
                    models.CharField(max_length=20, verbose_name="postal code"),
                ),
                ("city", models.CharField(max_length=100, verbose_name="city")),
                (
                    "country",
                    django_countries.fields.CountryField(
                        default="CH", max_length=2, verbose_name="country"
                    ),
                ),
                (
                    "postal_address_override",
                    models.TextField(
                        blank=True,
                        help_text="Completely overrides the postal address if set.",
                        verbose_name="override",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="postaladdresses",
                        to="contacts.Person",
                        verbose_name="person",
                    ),
                ),
            ],
            options={
                "verbose_name": "postal address",
                "verbose_name_plural": "postal addresses",
                "ordering": ("-weight", "id"),
            },
        ),
        migrations.AddField(
            model_name="emailaddress",
            name="person",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="emailaddresses",
                to="contacts.Person",
                verbose_name="person",
            ),
        ),
    ]
