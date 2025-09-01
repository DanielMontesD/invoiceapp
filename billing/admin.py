from django.contrib import admin
from .models import Invoice, WorkEntry

# admin.site.site_header = "InvoiceApp Admin"
# admin.site.site_title = "InvoiceApp Admin"
# admin.site.index_title = "Dashboard"


class WorkEntryInline(admin.TabularInline):
    model = WorkEntry
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "client_name",
        "period_start",
        "period_end",
        "total_hours",
        "total_amount",
    )
    search_fields = ("invoice_number", "client_name", "client_email")
    list_filter = ("period_type", "date_issued")
    inlines = [WorkEntryInline]


@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):
    list_display = ("invoice", "work_date", "hours", "description")
    list_filter = ("work_date",)
