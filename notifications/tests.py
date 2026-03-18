from __future__ import annotations

from django.test import TestCase

from accounts.models import User
from notifications.models import Notification


class NotificationTest(TestCase):
    def test_mark_read_sets_flag(self):
        user = User.objects.create_user(email="user@example.com", full_name="Name", phone_number="123", password="pass")
        note = Notification.objects.create(user=user, notification_type="test", title="Hello", message="World")
        self.assertFalse(note.is_read)
        note.mark_read()
        self.assertTrue(note.is_read)
