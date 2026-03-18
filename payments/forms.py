from django import forms
from .models import PaymentConfirmation, PaymentRequest, Expense

class PaymentRequestForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ["building", "apartment", "title", "payment_type", "amount", "billing_period_start", "billing_period_end", "due_date", "description"]
        widgets = {
            "billing_period_start": forms.DateInput(attrs={"type": "date"}),
            "billing_period_end": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["building"].queryset = owner.buildings.all()
            self.fields["apartment"].queryset = owner.buildings.all().first().apartments.all() if owner.buildings.exists() else owner.buildings.none()
            # Note: The initial queryset for apartments is mostly for validation. 
            # Interactive filtering is handled in the template via JS.
            self.fields["apartment"].queryset = owner.buildings.all().first().apartments.none() if not owner.buildings.exists() else owner.buildings.all().first().apartments.all()
            # Actually, let's just allow all apartments for the owner initially for easier JS filtering
            from properties.models import Apartment
            self.fields["apartment"].queryset = Apartment.objects.filter(building__owner=owner)

class PaymentConfirmationForm(forms.ModelForm):
    class Meta:
        model = PaymentConfirmation
        fields = ["payment_method_text", "note", "proof_image"]

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["building", "apartment", "title", "expense_type", "amount", "date", "description", "receipt_image"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["building"].queryset = owner.buildings.all()
            from properties.models import Apartment
            self.fields["apartment"].queryset = Apartment.objects.filter(building__owner=owner)
