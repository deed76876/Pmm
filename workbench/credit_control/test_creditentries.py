import io
import os
from decimal import Decimal

from django.conf import settings
from django.test import TestCase

from workbench import factories
from workbench.credit_control.models import CreditEntry
from workbench.tools.testing import messages


class CreditEntriesTest(TestCase):
    def test_assignment(self):
        for i in range(10):
            invoice = factories.InvoiceFactory.create(
                subtotal=10 + i, liable_to_vat=False
            )

        entry_0 = factories.CreditEntryFactory.create(total=12)
        entry_1 = factories.CreditEntryFactory.create(total=14)
        entry_2 = factories.CreditEntryFactory.create(total=19)

        self.client.force_login(factories.UserFactory.create())
        response = self.client.get("/credit-control/assign/")
        # print(response, response.content.decode("utf-8"))

        self.assertContains(response, "widget--radioselect", 3)
        response = self.client.post(
            "/credit-control/assign/",
            {
                "entry_{}_invoice".format(entry_2.pk): invoice.pk,
                "entry_{}_notes".format(entry_1.pk): "Stuff",
            },
        )
        self.assertRedirects(response, "/credit-control/assign/")

        response = self.client.get("/credit-control/assign/")
        self.assertContains(response, "widget--radioselect", 1)

        response = self.client.post(
            "/credit-control/assign/",
            {"entry_{}_notes".format(entry_0.pk): "Stuff"},
            follow=True,
        )
        self.assertRedirects(response, "/credit-control/")
        self.assertEqual(
            messages(response),
            [
                "Gutschriften wurden erfolgreich geändert.",
                "Alle Gutschriften wurden zugewiesen.",
            ],
        )

    def test_account_statement_upload(self):
        self.client.force_login(factories.UserFactory.create())
        ledger = factories.LedgerFactory.create()

        with io.open(
            os.path.join(
                settings.BASE_DIR, "workbench", "test", "account-statement.csv"
            )
        ) as f:
            response = self.client.post(
                "/credit-control/upload/", {"statement": f, "ledger": ledger.pk}
            )

        self.assertContains(response, "reference_number")
        statement_data = response.context_data["form"].data["statement_data"]

        response = self.client.post(
            "/credit-control/upload/",
            {"statement_data": statement_data, "ledger": ledger.pk},
        )

        self.assertRedirects(response, "/credit-control/")

        invoice = factories.InvoiceFactory.create(
            subtotal=Decimal("4000"), _code="00001"
        )
        self.assertAlmostEqual(invoice.total, Decimal("4308.00"))
        response = self.client.get("/credit-control/assign/")
        self.assertContains(response, "<strong><small>00001</small>")

        entry = CreditEntry.objects.get(reference_number="xxxx03130CF54579")
        response = self.client.post(
            entry.urls["update"],
            {
                "ledger": entry.ledger_id,
                "reference_number": entry.reference_number,
                "value_date": entry.value_date,
                "total": entry.total,
                "payment_notice": entry.payment_notice,
                "invoice": invoice.id,
                "notes": "",
            },
        )
        self.assertRedirects(response, entry.urls["detail"])

        invoice.refresh_from_db()
        self.assertEqual(invoice.status, invoice.PAID)
        self.assertEqual(invoice.closed_on, entry.value_date)
