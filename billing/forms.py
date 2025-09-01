from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, WorkEntry


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "employee",
            "period_type",
            "period_start",
            "period_end",
            "hourly_rate",
            "notes",
        ]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
        }


class WorkEntryForm(forms.ModelForm):
    class Meta:
        model = WorkEntry
        fields = ["work_date", "hours", "description"]
        widgets = {
            "work_date": forms.DateInput(attrs={"type": "date"}),
        }


WorkEntryFormSet = inlineformset_factory(
    parent_model=Invoice,
    model=WorkEntry,
    form=WorkEntryForm,
    extra=0,  # filas iniciales
    can_delete=True,
)
