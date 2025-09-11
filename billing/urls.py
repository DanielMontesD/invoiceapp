from django.urls import path
from . import views

urlpatterns = [
    # Root URL shows health check (for Railway)
    path("", views.health_check, name="root"),
    
    # Health check for Railway (moved to /health/)
    path("health/", views.health_check, name="health_check"),
    
    # Dashboard (redirect to client list for now)
    path("dashboard/", views.client_list, name="dashboard"),
    
    # Client management (new)
    path("clients/", views.client_list, name="client_list"),
    path("clients/new/", views.client_create, name="client_create"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
    path("clients/<int:pk>/edit/", views.client_edit, name="client_edit"),
    path("clients/<int:pk>/delete/", views.client_delete, name="client_delete"),
    path("clients/<int:pk>/invoices/new/", views.invoice_create_for_employee, name="invoice_create_for_client"),
    
    # Legacy employee URLs (for backward compatibility)
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:pk>/invoices/new/", views.invoice_create_for_employee, name="invoice_create_for_employee"),
    
    # Invoice management
    path("invoices/", views.invoice_list, name="invoice_list"),
    path("invoices/new/", views.invoice_create, name="invoice_create"),
    path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("invoices/<int:pk>/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("invoices/<int:pk>/mark-sent/", views.invoice_mark_sent, name="invoice_mark_sent"),
    path("invoices/<int:pk>/mark-paid/", views.invoice_mark_paid, name="invoice_mark_paid"),
    path("invoices/<int:pk>/duplicate/", views.invoice_duplicate, name="invoice_duplicate"),
    
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
]
