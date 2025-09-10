from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class Client(models.Model):
    """
    Client model representing customers/employers for whom invoices are generated.
    Each client belongs to a user and has a default hourly rate.
    """
    user = models.ForeignKey(
        User,
        related_name="clients",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="User who owns this client"
    )
    name = models.CharField(
        max_length=120,
        help_text="Client's full name or company name"
    )
    email = models.EmailField(
        blank=True,
        help_text="Client's email address for invoice delivery"
    )
    default_hourly_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=50,
        help_text="Default hourly rate for this client"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this client is currently active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this client was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this client was last updated"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# Employee model removed - use Client instead


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    default_hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=50
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.business_name}"


class Invoice(models.Model):
    PERIOD_CHOICES = [
        ("weekly", "Weekly"),
        ("fortnightly", "Fortnightly"),
        ("monthly", "Monthly"),
        ("custom", "Custom range"),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]

    # User who owns this invoice
    user = models.ForeignKey(
        User,
        related_name="invoices",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    
    # Client (formerly employee) - nullable for backward compatibility
    client = models.ForeignKey(
        Client,
        related_name="invoices",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    
    # Legacy employee field removed - use client instead

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
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
