from __future__ import annotations

from django import forms

from .models import Issue


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["building", "apartment", "title", "description", "priority", "image"]


class VendorForm(forms.ModelForm):
    class Meta:
        from .models import Vendor
        model = Vendor
        fields = ["name", "specialty", "phone_number", "email"]


class IssueAssignVendorForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ["vendor"]

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner:
            from .models import Vendor
            self.fields["vendor"].queryset = Vendor.objects.filter(owner=owner)
