from django.contrib import admin
from .models import Invoice, WorkEntry, Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "default_hourly_rate", "is_active")
    search_fields = ("name", "email")
    list_filter = ("is_active",)


class WorkEntryInline(admin.TabularInline):
    model = WorkEntry
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "employee",
        "client_name",
        "period_start",
        "period_end",
        "total_hours",
        "total_amount",
    )
    search_fields = ("invoice_number", "client_name", "client_email")
    list_filter = ("employee", "period_type", "date_issued")
    inlines = [WorkEntryInline]


@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):
    list_display = ("invoice", "work_date", "hours", "description")
    list_filter = ("work_date",)
