from __future__ import annotations

from django import forms

from .models import Apartment, Building


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ["building_name", "address_line_1", "address_line_2", "city", "state", "postal_code", "country", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ["apartment_name", "floor_number", "bedrooms", "bathrooms", "square_feet", "rent_amount", "is_active"]
