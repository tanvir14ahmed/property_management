from __future__ import annotations

from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User
from .models import Apartment, Building, TenantJoinRequest


class BuildingModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", full_name="Owner", phone_number="123", password="pass")

    def test_building_code_generated(self):
        building = Building.objects.create(
            owner=self.owner,
            building_name="Test Tower",
            address_line_1="123 Main",
            city="City",
            state="State",
            postal_code="00000",
            country="Country",
            description="",
        )
        self.assertTrue(building.building_code.startswith("B"))
        self.assertEqual(len(building.building_code), 8)


class TenantJoinRequestTest(TestCase):
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
        self.apartment = Apartment.objects.create(
            building=self.building,
            apartment_name="1A",
        )

    def test_duplicate_pending_request_raises(self):
        TenantJoinRequest.objects.create(
            tenant=self.tenant,
            building=self.building,
            apartment=self.apartment,
        )
        with self.assertRaises(IntegrityError):
            TenantJoinRequest.objects.create(
                tenant=self.tenant,
                building=self.building,
                apartment=self.apartment,
            )
