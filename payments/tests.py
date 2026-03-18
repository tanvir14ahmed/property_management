from __future__ import annotations

import shutil
import tempfile

from django.test import TestCase, override_settings

from accounts.models import User
from payments.models import Invoice, PaymentConfirmation, PaymentRequest
from properties.models import Apartment, Building


class PaymentFlowTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", full_name="Owner", phone_number="123", password="pass")
        self.tenant = User.objects.create_user(email="tenant@example.com", full_name="Tenant", phone_number="456", password="pass")
        self.building = Building.objects.create(
            owner=self.owner,
            building_name="Test Tower",
            address_line_1="123 Main",
            city="City",
            state="State",
            postal_code="00000",
            country="Country",
            description="",
        )
        self.apartment = Apartment.objects.create(building=self.building, apartment_name="1A")

    def test_invoice_created_when_confirmation_approved(self):
        tmpdir = tempfile.mkdtemp()
        try:
            with override_settings(MEDIA_ROOT=tmpdir):
                payment_request = PaymentRequest.objects.create(
                    building=self.building,
                    apartment=self.apartment,
                    owner=self.owner,
                    tenant=self.tenant,
                    title="Rent",
                    payment_type="rent",
                    amount=1000,
                    billing_period_start="2026-03-01",
                    billing_period_end="2026-03-31",
                    due_date="2026-03-05",
                )
                confirmation = PaymentConfirmation.objects.create(
                    payment_request=payment_request,
                    submitted_by=self.tenant,
                    payment_method_text="Cash",
                    status="approved",
                )
                self.assertTrue(hasattr(confirmation, "invoice"))
                invoice = Invoice.objects.get(payment_request=payment_request)
                self.assertTrue(invoice.owner_copy_pdf)
                self.assertTrue(invoice.tenant_copy_pdf)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
