from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase
from django.utils.translation import deactivate_all

from workbench import factories
from workbench.notes.admin import content_object_link
from workbench.notes.models import Note
from workbench.tools.testing import messages


class NotesTest(TestCase):
    def setUp(self):
        deactivate_all()

    def test_for_content_object(self):
        deal = factories.DealFactory.create()
        note = Note.objects.create(
            content_object=deal, created_by=deal.owned_by, title="Test"
        )
        self.assertEqual(Note.objects.for_content_object(deal).get(), note)

    def test_form(self):
        deal = factories.DealFactory.create()
        self.client.force_login(deal.owned_by)

        response = self.client.get(deal.urls["detail"])

        content_type = ContentType.objects.get_for_model(deal)

        self.assertContains(response, 'value="{}"'.format(content_type.pk))
        self.assertContains(response, 'value="{}"'.format(deal.pk))

        response = self.client.post(
            "/notes/add-note/",
            {
                "content_type": content_type.pk,
                "object_id": deal.pk,
                "title": "Test title",
                "description": "Test description",
                "next": deal.urls["detail"],
            },
        )
        self.assertRedirects(response, deal.urls["detail"])
        self.assertEqual(messages(response), [])

        response = self.client.post(
            "/notes/add-note/",
            {
                "content_type": content_type.pk,
                "object_id": deal.pk + 1,
                "title": "Test title",
                "description": "Test description",
                "next": deal.urls["detail"],
            },
        )
        self.assertRedirects(response, deal.urls["detail"])
        self.assertEqual(
            messages(response),
            ["Unable to determine the object this note should be added to."],
        )

        # print(response, response.content.decode("utf-8"))

        note = Note.objects.get()
        response = self.client.post(
            note.urls["update"],
            {"title": "Updated", "description": note.description},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 202)

        note.refresh_from_db()
        self.assertEqual(note.title, "Updated")

    def test_str(self):
        self.assertEqual(str(Note(title="bla")), "bla")

    def test_note_notification(self):
        deal = factories.DealFactory.create()
        self.client.force_login(deal.owned_by)

        content_type = ContentType.objects.get_for_model(deal)

        response = self.client.post(
            "/notes/add-note/",
            {
                "content_type": content_type.pk,
                "object_id": deal.pk,
                "title": "Test title",
                "description": "Test description",
                "next": deal.urls["detail"],
            },
        )
        self.assertRedirects(response, deal.urls["detail"])

        self.assertEqual(len(mail.outbox), 0)

        self.client.force_login(factories.UserFactory.create())
        response = self.client.post(
            "/notes/add-note/",
            {
                "content_type": content_type.pk,
                "object_id": deal.pk,
                "title": "Test title",
                "description": "Test description",
                "next": deal.urls["detail"],
            },
        )
        self.assertRedirects(response, deal.urls["detail"])

        self.assertEqual(len(mail.outbox), 1)

    def test_content_object_link(self):
        # Has URL
        deal = factories.DealFactory.create()
        content_type = ContentType.objects.get_for_model(deal)

        self.assertEqual(
            content_object_link(Note(content_type=content_type, object_id=42)),
            '<a href="/deals/42/">deal</a>',
        )

        # No URL
        types = factories.service_types()
        content_type = ContentType.objects.get_for_model(types.consulting)

        self.assertEqual(
            content_object_link(Note(content_type=content_type, object_id=42)),
            "service type",
        )
