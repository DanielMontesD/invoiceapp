from django.urls import path
from . import views

urlpatterns = [
    # Empleados
    path("", views.employee_list, name="employee_list"),  # Home = empleados
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path(
        "employees/<int:pk>/invoices/new/",
        views.invoice_create_for_employee,
        name="invoice_create_for_employee",
    ),
    # Invoices (genéricas, siguen funcionando)
    path("invoices/new/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("invoices/<int:pk>/mark-sent/", views.invoice_mark_sent, name="invoice_mark_sent"),
    path("invoices/<int:pk>/mark-paid/", views.invoice_mark_paid, name="invoice_mark_paid"),
    path("invoices/<int:pk>/duplicate/", views.invoice_duplicate, name="invoice_duplicate"),
    path("invoices/", views.invoice_list, name="invoice_list"),
]
