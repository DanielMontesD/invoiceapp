from datetime import date, timedelta
from calendar import monthrange

from django.contrib import messages
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import InvoiceForm, WorkEntryForm, WorkEntryFormSet
from .models import Invoice, WorkEntry


def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, "billing/invoice_list.html", {"invoices": invoices})


def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, "billing/invoice_detail.html", {"invoice": invoice})


def daterange(start_d: date, end_d: date):
    """Yield dates from start_d to end_d inclusive."""
    for n in range((end_d - start_d).days + 1):
        yield start_d + timedelta(days=n)


def monday_of(d: date) -> date:
    """Return Monday of the week of date d (Monday=0)."""
    return d - timedelta(days=d.weekday())


def invoice_create(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            formset = WorkEntryFormSet(request.POST, instance=invoice)
            if formset.is_valid():
                invoice.save()
                formset.save()
                messages.success(request, "Invoice created successfully.")
                return redirect("invoice_detail", pk=invoice.pk)
        else:
            formset = WorkEntryFormSet(request.POST)  # re-render with errors
        return render(
            request, "billing/invoice_form.html", {"form": form, "formset": formset}
        )

    # GET: inicializamos solo el formulario de Invoice (sin filas)
    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday

    form = InvoiceForm(
        initial={
            "period_type": "weekly",
            "period_start": start,
            "period_end": end,
            "hourly_rate": 50,
        }
    )
    formset = WorkEntryFormSet()  # 👈 sin filas; JS las generará

    return render(
        request, "billing/invoice_form.html", {"form": form, "formset": formset}
    )
