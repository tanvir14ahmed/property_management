from __future__ import annotations

from django.test import TestCase

from accounts.models import User
from chatapp.models import Conversation, Message
from properties.models import Apartment, Building


class ChatModelsTest(TestCase):
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

    def test_conversation_and_message(self):
        conversation, _ = Conversation.objects.get_or_create(apartment=self.apartment)
        Message.objects.create(conversation=conversation, sender=self.owner, message_text="Hi")
        self.assertEqual(conversation.messages.count(), 1)
