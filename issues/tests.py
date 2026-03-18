from __future__ import annotations

from django.test import TestCase

from accounts.models import User
from notifications.models import Notification
from issues.models import Issue
from properties.models import Apartment, Building


class IssueWorkflowTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", full_name="Owner", phone_number="123", password="pass")
        self.tenant = User.objects.create_user(email="tenant@example.com", full_name="Tenant", phone_number="456", password="pass")
        self.building = Building.objects.create(
            owner=self.owner,
            building_name="Tower",
            address_line_1="123",
            city="City",
            state="State",
            postal_code="00000",
            country="Country",
            description="",
        )
        self.apartment = Apartment.objects.create(building=self.building, apartment_name="1A")

    def test_issue_creation_creates_notification(self):
        Issue.objects.create(
            apartment=self.apartment,
            building=self.building,
            tenant=self.tenant,
            owner=self.owner,
            title="Leak",
            description="Leak description",
        )
        self.assertTrue(Notification.objects.filter(user=self.owner).exists())
