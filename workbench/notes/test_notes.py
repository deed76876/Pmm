from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.translation import deactivate_all

from workbench import factories
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

    def test_str(self):
        self.assertEqual(str(Note(title="bla")), "bla")