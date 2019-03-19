import factory
import types
from datetime import date
from faker import Factory

from workbench.accounts.models import User
from workbench.awt.models import Year
from workbench.contacts.models import Organization, Person
from workbench.invoices.models import Invoice
from workbench.logbook.models import LoggedCost, LoggedHours
from workbench.offers.models import Offer
from workbench.projects.models import Project, Service
from workbench.services.models import ServiceType


faker = Factory.create("de")


# ACCOUNTS ####################################################################
class UserFactory(factory.DjangoModelFactory):
    is_active = True
    _full_name = factory.LazyFunction(faker.name)
    _short_name = factory.Sequence(lambda n: "user%d" % n)
    email = factory.LazyAttribute(lambda obj: "%s@example.com" % obj._short_name)

    class Meta:
        model = User


# CONTACTS ####################################################################
class PersonFactory(factory.DjangoModelFactory):
    given_name = "Vorname"
    family_name = "Nachname"
    primary_contact = factory.SubFactory(UserFactory)

    class Meta:
        model = Person


class OrganizationFactory(factory.DjangoModelFactory):
    primary_contact = factory.SubFactory(UserFactory)

    class Meta:
        model = Organization


# PROJECTS ####################################################################
class ProjectFactory(factory.DjangoModelFactory):
    customer = factory.SubFactory(OrganizationFactory)
    contact = factory.LazyAttribute(
        lambda obj: PersonFactory.create(organization=obj.customer)
    )
    owned_by = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: "Project %d" % n)
    type = Project.ORDER

    class Meta:
        model = Project


class ServiceFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    service_hours = 0

    class Meta:
        model = Service


# OFFERS ######################################################################
class OfferFactory(factory.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)
    owned_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Offer


# INVOICES ####################################################################
class InvoiceFactory(factory.DjangoModelFactory):
    customer = factory.SubFactory(OrganizationFactory)
    owned_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Invoice


# SERVICES ####################################################################
def service_types():
    SERVICE_TYPES = [("consulting", 250), ("production", 180), ("administration", 130)]

    return types.SimpleNamespace(
        **{
            row[0]: ServiceType.objects.create(
                title=row[0], hourly_rate=row[1], position=idx
            )
            for idx, row in enumerate(SERVICE_TYPES)
        }
    )


# LOGBOOK #####################################################################
class LoggedHoursFactory(factory.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    created_by = factory.SubFactory(UserFactory)
    rendered_by = factory.SubFactory(UserFactory)

    class Meta:
        model = LoggedHours


class LoggedCostFactory(factory.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    created_by = factory.SubFactory(UserFactory)

    class Meta:
        model = LoggedCost


# AWT #########################################################################
class YearFactory(factory.DjangoModelFactory):
    year = date.today().year
    january = 30
    february = 30
    march = 30
    april = 30
    may = 30
    june = 30
    july = 30
    august = 30
    september = 30
    october = 30
    november = 30
    december = 30
    working_time_per_day = 8

    class Meta:
        model = Year
