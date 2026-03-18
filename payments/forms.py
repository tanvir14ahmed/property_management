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
            # We'll handle apartment filtering via JS or simple queryset if needed
