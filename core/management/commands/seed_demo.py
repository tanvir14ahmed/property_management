from __future__ import annotations

from datetime import date

from django.core.management.base import BaseCommand

from accounts.models import User
from issues.models import Issue
from payments.models import PaymentConfirmation, PaymentRequest
from properties.models import Apartment, ApartmentOccupancy, Building, TenantJoinRequest


class Command(BaseCommand):
    help = "Populate demo data for property management app."

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(
            email="owner@example.com",
            defaults={"full_name": "Owner Demo", "phone_number": "100"},
        )
        owner.is_owner = True
        owner.set_password("password")
        owner.save()
        tenant, _ = User.objects.get_or_create(
            email="tenant@example.com",
            defaults={"full_name": "Tenant Demo", "phone_number": "200"},
        )
        tenant.is_tenant = True
        tenant.set_password("password")
        tenant.save()
        dual, _ = User.objects.get_or_create(
            email="mixed@example.com",
            defaults={"full_name": "Both Roles", "phone_number": "300"},
        )
        dual.is_owner = True
        dual.is_tenant = True
        dual.set_password("password")
        dual.save()

        building, _ = Building.objects.get_or_create(
            owner=owner,
            building_name="Demo Tower",
            defaults={
                "address_line_1": "1 Demo Street",
                "city": "Demo City",
                "state": "Demo State",
                "postal_code": "11111",
                "country": "Demo Land",
                "description": "Sample building",
            },
        )

        apartment, _ = Apartment.objects.get_or_create(
            building=building,
            apartment_name="Unit 101",
        )

        TenantJoinRequest.objects.get_or_create(
            tenant=tenant,
            building=building,
            apartment=apartment,
        )

        occupancy, _ = ApartmentOccupancy.objects.get_or_create(
            apartment=apartment,
            tenant=tenant,
            defaults={"approved_by": owner, "approved_at": date.today()},
        )

        payment_request, _ = PaymentRequest.objects.get_or_create(
            building=building,
            apartment=apartment,
            owner=owner,
            tenant=tenant,
            title="Demo Rent",
            payment_type="rent",
            amount=1000,
            billing_period_start=date.today(),
            billing_period_end=date.today(),
            due_date=date.today(),
        )

        PaymentConfirmation.objects.get_or_create(
            payment_request=payment_request,
            submitted_by=tenant,
            payment_method_text="Cash",
            status="pending",
        )

        Issue.objects.get_or_create(
            apartment=apartment,
            building=building,
            tenant=tenant,
            owner=owner,
            title="Demo Issue",
            description="Sample issue description",
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
