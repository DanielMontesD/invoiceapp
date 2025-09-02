from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.urls import reverse


class Employee(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    default_hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=50
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Invoice(models.Model):
    PERIOD_CHOICES = [
        ("weekly", "Weekly"),
        ("fortnightly", "Fortnightly"),
        ("monthly", "Monthly"),
        ("custom", "Custom range"),
    ]

    # NUEVO: relación con empleado (nullable por compatibilidad con invoices existentes)
    employee = models.ForeignKey(
        Employee,
        related_name="invoices",
        on_delete=models.PROTECT,  # evita borrar un empleado con invoices
        null=True,
        blank=True,
    )

    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    client_name = models.CharField(max_length=120)
    client_email = models.EmailField(blank=True)
    period_type = models.CharField(
        max_length=12, choices=PERIOD_CHOICES, default="weekly"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    date_issued = models.DateField(default=timezone.localdate)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Invoice {self.invoice_number or '(draft)'} - {self.client_name}"

    def get_absolute_url(self):
        return reverse("invoice_detail", args=[self.pk])

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by("-id").first()
            next_num = 1
            if last and (last.invoice_number or "").isdigit():
                next_num = int(last.invoice_number) + 1
            self.invoice_number = f"{next_num:05d}"
        super().save(*args, **kwargs)

    @property
    def total_hours(self):
        agg = self.work_entries.aggregate(s=models.Sum("hours"))
        return agg["s"] or Decimal("0.00")

    @property
    def total_amount(self):
        return self.total_hours * self.hourly_rate


class WorkEntry(models.Model):
    invoice = models.ForeignKey(
        Invoice, related_name="work_entries", on_delete=models.CASCADE
    )
    work_date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["work_date"]

    def __str__(self):
        return f"{self.work_date} - {self.hours} h"

    @property
    def amount(self):
        "Daily amoutn made"
        h = self.hours or Decimal("0")
        r = (
            (self.invoice.hourly_rate or Decimal("0"))
            if self.invoice_id
            else Decimal("0")
        )
        return h * r
