from __future__ import annotations

from django import forms

from .models import Issue


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["building", "apartment", "title", "description", "priority", "image"]
