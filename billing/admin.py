from django.contrib import admin
from .models import Invoice, WorkEntry, Client, UserProfile


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "user", "default_hourly_rate", "is_active", "created_at")
    search_fields = ("name", "email", "user__username")
    list_filter = ("is_active", "created_at", "user")
    readonly_fields = ("created_at", "updated_at")


# Employee model removed - use Client instead


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "business_name", "phone", "default_hourly_rate", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "business_name")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


class WorkEntryInline(admin.TabularInline):
    model = WorkEntry
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "client",
        "client_name",
        "period_start",
        "period_end",
        "total_hours",
        "total_amount",
    )
    search_fields = ("invoice_number", "client_name", "client_email")
    list_filter = ("client", "period_type", "date_issued", "status")
    inlines = [WorkEntryInline]


@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):
    list_display = ("invoice", "work_date", "hours", "description")
    list_filter = ("work_date",)
