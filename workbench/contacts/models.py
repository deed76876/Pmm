import itertools
import re

from django.db import models
from django.utils.translation import gettext_lazy as _

import phonenumbers
from django_countries.fields import CountryField

from workbench.accounts.models import User
from workbench.tools.models import Model, SearchQuerySet
from workbench.tools.urls import model_urls
from workbench.tools.validation import raise_if_errors


@model_urls
class Group(Model):
    title = models.CharField(_("title"), max_length=100)

    class Meta:
        ordering = ("title",)
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        return self.title


@model_urls
class Organization(Model):
    name = models.TextField(_("name"))
    is_private_person = models.BooleanField(_("is private person"), default=False)
    notes = models.TextField(_("notes"), blank=True)
    primary_contact = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("primary contact")
    )
    default_billing_address = models.TextField(
        _("default billing address"),
        blank=True,
        help_text=_(
            "Mainly useful for organizations with a centralized"
            " accounts payable departement."
        ),
    )
    groups = models.ManyToManyField(Group, verbose_name=_("groups"), blank=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    def __str__(self):
        return self.name

    @classmethod
    def allow_delete(cls, instance, request):
        return None


class PersonQuerySet(SearchQuerySet):
    def active(self):
        return self.filter(is_archived=False)


@model_urls
class Person(Model):
    is_archived = models.BooleanField(
        _("is archived"),
        default=False,
        help_text=_("It is preferrable to archive records instead of deleting them."),
    )
    given_name = models.CharField(_("given name"), max_length=100)
    family_name = models.CharField(_("family name"), max_length=100)
    address = models.CharField(
        _("address"), max_length=100, blank=True, help_text=_("Mr./Ms./...")
    )
    address_on_first_name_terms = models.BooleanField(
        _("address on first-name terms"), default=False
    )
    salutation = models.CharField(
        _("complete salutation"),
        max_length=100,
        blank=True,
        help_text=_("Dear John/Dear Ms Smith"),
    )
    notes = models.TextField(_("notes"), blank=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_("organization"),
        related_name="people",
    )
    primary_contact = models.ForeignKey(
        User, on_delete=models.PROTECT, verbose_name=_("primary contact")
    )
    groups = models.ManyToManyField(Group, verbose_name=_("groups"), blank=True)
    _fts = models.TextField(editable=False, blank=True)

    objects = PersonQuerySet.as_manager()

    class Meta:
        ordering = ["given_name", "family_name"]
        verbose_name = _("person")
        verbose_name_plural = _("people")

    def __str__(self):
        if self.organization_id and not self.organization.is_private_person:
            return "%s / %s" % (self.full_name, self.organization)
        return self.full_name

    @property
    def full_name(self):
        return " ".join(filter(None, (self.given_name, self.family_name)))

    def save(self, *args, **kwargs):
        self._fts = " ".join(
            itertools.chain(
                [self.organization.name if self.organization else ""],
                (detail.phone_number for detail in self.phonenumbers.all()),
                (detail.email for detail in self.emailaddresses.all()),
                (detail.postal_address for detail in self.postaladdresses.all()),
            )
        )
        super().save(*args, **kwargs)

    save.alters_data = True


class PersonDetail(Model):
    WEIGHTS = (
        (re.compile(r"mobil", re.I), 30),
        (re.compile(r"(work|arbeit)", re.I), 20),
        (re.compile(r"(home|hause)", re.I), 10),
        (re.compile(r"(organization|firm)", re.I), -100),
    )

    type = models.CharField(_("type"), max_length=40, default=_("work"))
    weight = models.SmallIntegerField(_("weight"), default=0, editable=False)

    class Meta:
        abstract = True

    @property
    def urls(self):
        return self.person.urls

    def get_absolute_url(self):
        return self.person.urls["detail"]

    def save(self, *args, **kwargs):
        self.weight = sum(
            (weight for regex, weight in self.WEIGHTS if regex.search(str(self.type))),
            0,
        )
        super().save(*args, **kwargs)

    save.alters_data = True


class PhoneNumber(PersonDetail):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_("person"),
        related_name="phonenumbers",
    )
    phone_number = models.CharField(_("phone number"), max_length=100)

    class Meta:
        ordering = ("-weight", "id")
        verbose_name = _("phone number")
        verbose_name_plural = _("phone numbers")

    def __str__(self):
        return self.phone_number

    def clean_fields(self, exclude):
        super().clean_fields(exclude)
        errors = {}
        try:
            number = phonenumbers.parse(self.phone_number, "CH")
        except phonenumbers.NumberParseException as exc:
            errors["phone_number"] = str(exc)
        else:
            if phonenumbers.is_valid_number(number):
                self.phone_number = phonenumbers.format_number(
                    number, phonenumbers.PhoneNumberFormat.E164
                )
            else:
                errors["phone_number"] = _("Phone number invalid.")
        raise_if_errors(errors, exclude)

    @property
    def pretty_number(self):
        try:
            return phonenumbers.format_number(
                phonenumbers.parse(self.phone_number),
                phonenumbers.PhoneNumberFormat.INTERNATIONAL,
            )
        except Exception:
            return self.phone_number


class EmailAddress(PersonDetail):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_("person"),
        related_name="emailaddresses",
    )
    email = models.EmailField(_("email"), max_length=254)

    class Meta:
        ordering = ("-weight", "id")
        verbose_name = _("email address")
        verbose_name_plural = _("email addresses")

    def __str__(self):
        return self.email


class PostalAddress(PersonDetail):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_("person"),
        related_name="postaladdresses",
    )
    street = models.CharField(_("street"), max_length=100)
    house_number = models.CharField(_("house number"), max_length=20, blank=True)
    address_suffix = models.CharField(_("address suffix"), max_length=100, blank=True)
    postal_code = models.CharField(_("postal code"), max_length=20)
    city = models.CharField(_("city"), max_length=100)
    country = CountryField(_("country"), default="CH")
    postal_address_override = models.TextField(
        _("override"),
        blank=True,
        help_text=_("Completely overrides the postal address if set."),
    )

    class Meta:
        ordering = ("-weight", "id")
        verbose_name = _("postal address")
        verbose_name_plural = _("postal addresses")

    def __str__(self):
        return self.postal_address

    @property
    def postal_address(self):
        if self.postal_address_override:
            return self.postal_address_override
        lines = [
            self.person.organization.name
            if self.person.organization
            and not self.person.organization.is_private_person
            and not any(type in self.type.lower() for type in ["home"])
            else "",
            self.person.full_name,
            " ".join(filter(None, (self.street, self.house_number))),
            self.address_suffix,
            " ".join(filter(None, (self.postal_code, self.city))),
            self.country.name if self.country.code != "CH" else "",
        ]
        return "\n".join(filter(None, lines))
