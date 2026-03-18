from __future__ import annotations

from django import forms

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["message_text"]
        widgets = {"message_text": forms.Textarea(attrs={"rows": 3})}
