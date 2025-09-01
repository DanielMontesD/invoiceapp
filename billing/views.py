from datetime import date, timedelta
from calendar import monthrange

from django.contrib import messages
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import InvoiceForm, WorkEntryFormSet
from .models import Invoice, Employee


# --- NUEVA: lista de empleados ---
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "billing/employee_list.html", {"employees": employees})


# --- NUEVA: detalle del empleado + sus invoices ---
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    invoices = employee.invoices.all().order_by("-id")
    return render(
        request,
        "billing/employee_detail.html",
        {"employee": employee, "invoices": invoices},
    )


# --- NUEVA: crear invoice para un empleado concreto ---
def invoice_create_for_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        # fuerzo el empleado en servidor aunque el select no se envíe (lo desactivamos en GET)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.employee = employee
            invoice.client_name = employee.name
            invoice.client_email = employee.email
            if not invoice.hourly_rate:
                invoice.hourly_rate = employee.default_hourly_rate
            formset = WorkEntryFormSet(request.POST, instance=invoice)
            if formset.is_valid():
                invoice.save()
                formset.save()
                messages.success(request, "Invoice created successfully.")
                return redirect("invoice_detail", pk=invoice.pk)
        else:
            formset = WorkEntryFormSet(request.POST)

        return render(
            request,
            "billing/invoice_form.html",
            {"form": form, "formset": formset, "fixed_employee": employee},
        )

    # GET: inicializamos con weekly y el hourly del empleado
    today = timezone.localdate()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    form = InvoiceForm(
        initial={
            "employee": employee.pk,  # preseleccionado en el form
            "period_type": "weekly",
            "period_start": start,
            "period_end": end,
            "hourly_rate": employee.default_hourly_rate,  # 👈 default del empleado
        }
    )
    # desactivar visualmente el selector para evitar que cambien de empleado
    if "employee" in form.fields:
        form.fields["employee"].disabled = True

    formset = WorkEntryFormSet()  # filas las genera el JS del template

    return render(
        request,
        "billing/invoice_form.html",
        {"form": form, "formset": formset, "fixed_employee": employee},
    )


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
            # Creamos el invoice sin guardar aún
            invoice = form.save(commit=False)

            # Si hay empleado seleccionado, copiamos snapshot de name/email
            if invoice.employee_id:
                emp = invoice.employee
                invoice.client_name = emp.name
                invoice.client_email = emp.email
                # Si no se indicó tarifa, usar la del empleado
                if not invoice.hourly_rate:
                    invoice.hourly_rate = emp.default_hourly_rate

            # Formset ligado al invoice (aún no guardado)
            formset = WorkEntryFormSet(request.POST, instance=invoice)

            if formset.is_valid():
                invoice.save()
                formset.save()
                messages.success(request, "Invoice created successfully.")
                return redirect("invoice_detail", pk=invoice.pk)
            # Si el formset NO es válido, caemos al render de abajo con form y formset ligados

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
