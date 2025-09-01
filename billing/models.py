from django.db import models
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse


class Invoice(models.Model):
    PERIOD_CHOICES = [
        ("weekly", "Weekly"),
        ("fortnightly", "Fortnightly"),
        ("monthly", "Monthly"),
        ("custom", "Custom range"),
    ]

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
        # Autogenerate sequential invoice number like 00001, 00002, ...
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
