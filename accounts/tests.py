from __future__ import annotations

from django.test import TestCase

from .models import IncompleteRegistration, User


class UserModelTest(TestCase):
    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", full_name="Test", phone_number="123", password="pass")

    def test_roles_property(self):
        user = User.objects.create_user(email="owner@example.com", full_name="Owner", phone_number="123", password="pass")
        user.is_owner = True
        user.is_tenant = True
        user.save()
        self.assertListEqual(sorted(user.roles), ["owner", "tenant"])


class IncompleteRegistrationTest(TestCase):
    def test_mark_completed_updates_flag(self):
        record = IncompleteRegistration.objects.create(full_name="Test", email="test@example.com", phone_number="123", selected_role_intent=1)
        self.assertFalse(record.is_completed)
        record.mark_completed()
        self.assertTrue(record.is_completed)
