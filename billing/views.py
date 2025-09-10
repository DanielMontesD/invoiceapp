from datetime import date, timedelta
from calendar import monthrange

from django.contrib import messages
from django.db.models import Q
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string

from .forms import InvoiceForm, WorkEntryFormSet, ClientForm, UserProfileForm
from .models import Invoice, Client, WorkEntry, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from io import BytesIO
from xhtml2pdf import pisa


# --- Client management views ---

def client_list(request):
    """
    Display list of all clients with search and filtering capabilities.
    """
    clients = Client.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        clients = clients.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query)
        )
    
    # Filter by active status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        clients = clients.filter(is_active=True)
    elif status_filter == 'inactive':
        clients = clients.filter(is_active=False)
    
    return render(request, "billing/client_list.html", {
        "clients": clients,
        "search_query": search_query,
        "status_filter": status_filter,
    })


def client_detail(request, pk):
    """
    Display client details and their associated invoices.
    """
    client = get_object_or_404(Client, pk=pk)
    invoices = client.invoices.all().order_by("-id")
    
    return render(request, "billing/client_detail.html", {
        "client": client,
        "invoices": invoices,
    })


def client_create(request):
    """
    Create a new client.
    """
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Client '{client.name}' created successfully.")
            return redirect("client_detail", pk=client.pk)
    else:
        form = ClientForm()
    
    return render(request, "billing/client_form.html", {
        "form": form,
        "title": "Create New Client",
        "submit_text": "Create Client",
    })


def client_edit(request, pk):
    """
    Edit an existing client.
    """
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client = form.save()
            messages.success(request, f"Client '{client.name}' updated successfully.")
            return redirect("client_detail", pk=client.pk)
    else:
        form = ClientForm(instance=client)
    
    return render(request, "billing/client_form.html", {
        "form": form,
        "client": client,
        "title": f"Edit Client: {client.name}",
        "submit_text": "Update Client",
    })


def client_delete(request, pk):
    """
    Delete a client (with confirmation).
    """
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == "POST":
        client_name = client.name
        client.delete()
        messages.success(request, f"Client '{client_name}' deleted successfully.")
        return redirect("client_list")
    
    return render(request, "billing/client_confirm_delete.html", {
        "client": client,
    })


# --- Legacy employee list view (for backward compatibility) ---
def employee_list(request):
    """
    Legacy view - redirects to client_list for backward compatibility.
    """
    return redirect("client_list")


# --- Client detail view ---
def employee_detail(request, pk):
    """
    Display client details and their associated invoices.
    """
    client = get_object_or_404(Client, pk=pk)
    invoices = client.invoices.all().order_by("-id")
    return render(
        request,
        "billing/employee_detail.html",
        {"employee": client, "invoices": invoices},  # Keep 'employee' for template compatibility
    )


# --- Create invoice for specific client ---
def invoice_create_for_employee(request, pk):
    """
    Create a new invoice for a specific client.
    """
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        
        # Debug: print form data
        print(f"Form data: {request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        if form.is_valid():
            # Create invoice with client data
            invoice = form.save(commit=False)
            invoice.client = client
            invoice.client_name = client.name
            invoice.client_email = client.email
            if not invoice.hourly_rate:
                invoice.hourly_rate = client.default_hourly_rate
            
            # Save invoice first
            invoice.save()
            print(f"Invoice saved with ID: {invoice.pk}")
            
            # Handle work entries
            formset = WorkEntryFormSet(request.POST, instance=invoice)
            
            # Handle work entries manually without formset validation
            saved_entries = 0
            for i in range(int(request.POST.get('work_entries-TOTAL_FORMS', 0))):
                work_date = request.POST.get(f'work_entries-{i}-work_date')
                hours = request.POST.get(f'work_entries-{i}-hours')
                description = request.POST.get(f'work_entries-{i}-description')
                
                # Only save if there's meaningful data
                if work_date and (hours or description):
                    work_entry = WorkEntry(
                        invoice=invoice,
                        work_date=work_date,
                        hours=float(hours) if hours else 0.0,
                        description=description or ''
                    )
                    work_entry.save()
                    saved_entries += 1
            
            if saved_entries > 0:
                messages.success(request, f"Invoice created successfully with {saved_entries} work entries.")
            else:
                messages.success(request, "Invoice created successfully. You can add work entries later.")
            return redirect("invoice_detail", pk=invoice.pk)
        else:
            formset = WorkEntryFormSet()

        return render(
            request,
            "billing/invoice_form.html",
            {"form": form, "formset": formset, "fixed_employee": client},
        )

    # GET: inicializamos con weekly y el hourly del empleado
    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    form = InvoiceForm(
        initial={
            "client": client.pk,  # Pre-selected in the form
            "client_name": client.name,
            "client_email": client.email,
            "period_type": "weekly",
            "period_start": start,
            "period_end": end,
            "hourly_rate": client.default_hourly_rate,  # Client's default rate
        }
    )
    # Disable the client selector to prevent changing clients
    if "client" in form.fields:
        form.fields["client"].disabled = True

    formset = WorkEntryFormSet()  # filas las genera el JS del template

    return render(
        request,
        "billing/invoice_form.html",
        {"form": form, "formset": formset, "fixed_employee": client},
    )


def invoice_list(request):
    # Show all invoices for now (will add user filtering later)
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
            # Create invoice without saving yet
            invoice = form.save(commit=False)

            # If there's a client selected, copy snapshot of name/email
            if invoice.client_id:
                client = invoice.client
                invoice.client_name = client.name
                invoice.client_email = client.email
                # If no hourly rate specified, use client's default
                if not invoice.hourly_rate:
                    invoice.hourly_rate = client.default_hourly_rate

            # Save invoice first to get an ID
            invoice.save()
            
            # Formset linked to the invoice
            formset = WorkEntryFormSet(request.POST, instance=invoice)

            # Handle work entries manually without formset validation
            saved_entries = 0
            for i in range(int(request.POST.get('work_entries-TOTAL_FORMS', 0))):
                work_date = request.POST.get(f'work_entries-{i}-work_date')
                hours = request.POST.get(f'work_entries-{i}-hours')
                description = request.POST.get(f'work_entries-{i}-description')
                
                # Only save if there's meaningful data
                if work_date and (hours or description):
                    work_entry = WorkEntry(
                        invoice=invoice,
                        work_date=work_date,
                        hours=float(hours) if hours else 0.0,
                        description=description or ''
                    )
                    work_entry.save()
                    saved_entries += 1
            
            if saved_entries > 0:
                messages.success(request, f"Invoice created successfully with {saved_entries} work entries.")
            else:
                messages.success(request, "Invoice created successfully. You can add work entries later.")
            return redirect("invoice_detail", pk=invoice.pk)

        else:
            # Si el form principal NO es válido, construimos el formset para no perder filas
            formset = WorkEntryFormSet(request.POST)

        return render(
            request, "billing/invoice_form.html", {"form": form, "formset": formset}
        )

    # GET: inicializamos solo el formulario de Invoice (sin filas; JS las generará)
    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday

    form = InvoiceForm(
        initial={
            "period_type": "weekly",
            "period_start": start,
            "period_end": end,
            "hourly_rate": 50,  # genérico; si eliges empleado, se aplicará su rate al guardar
        }
    )
    formset = (
        WorkEntryFormSet()
    )  # sin filas; el JS del template las crea según el periodo

    return render(
        request, "billing/invoice_form.html", {"form": form, "formset": formset}
    )


# Creacion de invoices como PDF para poder ser enviados
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    html = render_to_string("billing/invoice_pdf.html", {"invoice": invoice})

    result = BytesIO()
    pdf = pisa.CreatePDF(html, dest=result, encoding="UTF-8")

    if pdf.err:
        return HttpResponse("PDF generation error", status=500)

    filename = f"Invoice_{invoice.invoice_number or invoice.pk}.pdf"
    resp = HttpResponse(result.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


def invoice_mark_sent(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status == 'draft':
        invoice.status = 'sent'
        invoice.save()
        messages.success(request, f"Invoice {invoice.invoice_number} marked as sent.")
    return redirect('invoice_detail', pk=pk)


def invoice_mark_paid(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if invoice.status == 'sent':
        invoice.status = 'paid'
        invoice.save()
        messages.success(request, f"Invoice {invoice.invoice_number} marked as paid.")
    return redirect('invoice_detail', pk=pk)


def invoice_duplicate(request, pk):
    original_invoice = get_object_or_404(Invoice, pk=pk)
    
    # Create a copy of the invoice
    new_invoice = Invoice.objects.create(
        employee=original_invoice.employee,
        client_name=original_invoice.client_name,
        client_email=original_invoice.client_email,
        period_type=original_invoice.period_type,
        period_start=original_invoice.period_start,
        period_end=original_invoice.period_end,
        hourly_rate=original_invoice.hourly_rate,
        status='draft',
        notes=original_invoice.notes,
    )
    
    # Copy work entries
    for work_entry in original_invoice.work_entries.all():
        WorkEntry.objects.create(
            invoice=new_invoice,
            work_date=work_entry.work_date,
            hours=work_entry.hours,
            description=work_entry.description,
        )
    
    messages.success(request, f"Invoice duplicated. New invoice: {new_invoice.invoice_number}")
    return redirect('invoice_detail', pk=new_invoice.pk)