from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Invoice, WorkEntry, Client, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class InvoiceForm(forms.ModelForm):
    """
    Form for creating and editing invoices.
    """
    class Meta:
        model = Invoice
        fields = [
            "period_type",
            "period_start",
            "period_end",
            "hourly_rate",
            "status",
            "notes",
        ]
        widgets = {
            "period_start": forms.DateInput(attrs={"type": "date"}),
            "period_end": forms.DateInput(attrs={"type": "date"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For new invoices, only allow Draft status
        if not self.instance.pk:
            self.fields['status'].required = False
            self.fields['status'].initial = 'draft'

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_status(self):
        return self.cleaned_data.get('status') or 'draft'


class WorkEntryForm(forms.ModelForm):
    class Meta:
        model = WorkEntry
        fields = ["work_date", "hours", "description"]
        widgets = {
            "work_date": forms.DateInput(attrs={"type": "date"}),
        }
    
    def clean(self):
        # Don't validate anything - let the view handle the logic
        return super().clean()


WorkEntryFormSet = inlineformset_factory(
    parent_model=Invoice,
    model=WorkEntry,
    form=WorkEntryForm,
    extra=0,  # filas iniciales
    can_delete=False,  # Remove delete option
    min_num=0,  # Allow zero work entries
    validate_min=False,  # Don't validate minimum
    validate_max=False,  # Don't validate maximum
)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "default_hourly_rate", "is_active"]
        widgets = {
            "default_hourly_rate": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'is_active':
                field.widget.attrs.update({"class": "form-check-input", "role": "switch"})
            else:
                field.widget.attrs.update({"class": "form-control"})


class UserProfileForm(forms.ModelForm):
    """
    Form for creating and editing user profiles.
    """
    class Meta:
        model = UserProfile
        fields = [
            "business_name",
            "phone",
            "address",
            "default_hourly_rate",
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "default_hourly_rate": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for better styling
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
