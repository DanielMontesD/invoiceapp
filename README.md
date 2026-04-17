# 🧾 Invoice App

A full-featured Django web application for creating and managing invoices from daily work logs, with dynamic date ranges, PDF export, and multi-user support. Designed for freelancers and small businesses to track billable hours and generate professional invoices.

## ✨ Features

### Client Management
- **CRUD operations** — Create, view, edit, and soft-delete (deactivate) clients
- **Search & filtering** — Search clients by name or email; filter by active/inactive status
- **Per-client invoicing** — Create invoices directly from a client's detail page
- **Revenue tracking** — View total revenue generated per client

### Invoice Management
- **Flexible billing periods** — Weekly, fortnightly, monthly, or custom date ranges
- **Auto-generated invoice numbers** — Unique, sequential numbering per user (`00001`, `00002`, …)
- **Status workflow** — Track invoices through `Draft → Sent → Paid` stages
- **Duplicate invoices** — Clone an existing invoice (and its work entries) with one click
- **PDF export** — Download any invoice as a professionally formatted PDF via `xhtml2pdf`
- **Work entries** — Log daily hours and descriptions tied to each invoice; totals are computed automatically

### Authentication & Multi-User
- **User registration & login** — Built-in sign-up, login, and logout flows
- **Per-user data isolation** — Each user sees only their own clients and invoices
- **Basic Auth middleware** — Optional HTTP Basic Authentication for programmatic access
- **Django Admin** — Full admin interface for superusers to manage all data

## 🏗️ Project Structure

```
Invoice App/
├── billing/                  # Main Django app
│   ├── admin.py              # Admin site registration (Client, Invoice, WorkEntry, UserProfile)
│   ├── forms.py              # ModelForms: InvoiceForm, WorkEntryFormSet, ClientForm, UserProfileForm
│   ├── middleware.py          # BasicAuthMiddleware for HTTP Basic Auth
│   ├── models.py             # Data models: Client, UserProfile, Invoice, WorkEntry
│   ├── urls.py               # App-level URL routes
│   └── views.py              # All view logic (clients, invoices, auth, PDF, health check)
│
├── invoicegen/               # Django project configuration
│   ├── settings.py           # Base settings (development)
│   ├── settings_production.py # Production overrides (PostgreSQL, WhiteNoise, security)
│   ├── settings_healthcheck.py # Healthcheck-specific settings
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py               # WSGI entry point (development)
│   └── wsgi_production.py    # WSGI entry point (production)
│
├── templates/
│   ├── base.html             # Base template with shared layout
│   └── billing/              # App templates
│       ├── client_list.html
│       ├── client_detail.html
│       ├── client_form.html
│       ├── client_confirm_delete.html
│       ├── invoice_list.html
│       ├── invoice_detail.html
│       ├── invoice_form.html
│       ├── invoice_pdf.html
│       ├── login.html
│       ├── register.html
│       └── ...
│
├── manage.py                 # Django management CLI
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version (3.11.9)
├── Procfile                  # Process definition for deployment
├── start.sh                  # Production startup script
├── railway.json              # Railway deployment configuration
└── .env.example              # Example environment variables
```

## 🛠️ Tech Stack

| Layer            | Technology                                     |
| ---------------- | ---------------------------------------------- |
| **Framework**    | Django 4.2                                     |
| **Language**     | Python 3.11                                    |
| **Database**     | SQLite (dev) · PostgreSQL (prod via `dj-database-url`) |
| **PDF Engine**   | xhtml2pdf + ReportLab                          |
| **Static Files** | WhiteNoise                                     |
| **WSGI Server**  | Gunicorn                                       |
| **Deployment**   | Railway (Nixpacks)                             |
| **Config**       | python-decouple (`.env` files)                 |

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip
- (Optional) virtualenv or venv

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/DanielMontesD/invoiceapp.git
   cd invoiceapp
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your values:

   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   ```

5. **Run database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**

   ```bash
   python manage.py runserver
   ```

   Open [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) in your browser.

## 📡 URL Routes

| URL Pattern                          | Name                           | Description                      |
| ------------------------------------ | ------------------------------ | -------------------------------- |
| `/`                                  | `root`                         | Health check endpoint            |
| `/health/`                           | `health_check`                 | Health check (Railway)           |
| `/dashboard/`                        | `dashboard`                    | Dashboard (→ client list)        |
| `/clients/`                          | `client_list`                  | List all clients                 |
| `/clients/new/`                      | `client_create`                | Create a new client              |
| `/clients/<id>/`                     | `client_detail`                | View client details & invoices   |
| `/clients/<id>/edit/`                | `client_edit`                  | Edit client                      |
| `/clients/<id>/delete/`              | `client_delete`                | Deactivate client                |
| `/clients/<id>/invoices/new/`        | `invoice_create_for_client`    | Create invoice for a client      |
| `/invoices/`                         | `invoice_list`                 | List all invoices                |
| `/invoices/new/`                     | `invoice_create`               | Create a new invoice             |
| `/invoices/<id>/`                    | `invoice_detail`               | View invoice details             |
| `/invoices/<id>/pdf/`               | `invoice_pdf`                  | Download invoice as PDF          |
| `/invoices/<id>/mark-sent/`         | `invoice_mark_sent`            | Mark invoice as sent             |
| `/invoices/<id>/mark-paid/`         | `invoice_mark_paid`            | Mark invoice as paid             |
| `/invoices/<id>/duplicate/`         | `invoice_duplicate`            | Duplicate an invoice             |
| `/login/`                            | `login`                        | User login                       |
| `/logout/`                           | `logout`                       | User logout                      |
| `/register/`                         | `register`                     | User registration                |
| `/admin/`                            | —                              | Django admin panel                |

## 📊 Data Models

### Client
Represents a customer or employer. Each client belongs to a user and carries a default hourly rate.

### UserProfile
Extends Django's `User` model with business info (business name, phone, address, default rate).

### Invoice
An invoice tied to a client with a billing period, hourly rate, status tracking, and auto-generated invoice number.

### WorkEntry
Individual work log entries attached to an invoice, recording date, hours, and description. The line-item amount is computed from hours × invoice hourly rate.

## ☁️ Deployment (Railway)

The app is pre-configured for [Railway](https://railway.app/) deployment:

1. Push your code to GitHub.
2. Connect the repository in Railway.
3. Set the following environment variables in Railway:

   | Variable        | Example Value                        |
   | --------------- | ------------------------------------ |
   | `SECRET_KEY`    | `a-long-random-string`               |
   | `DATABASE_URL`  | *(auto-set by Railway PostgreSQL)*    |
   | `ALLOWED_HOSTS` | `*.railway.app`                      |

4. Railway will automatically build via Nixpacks and start with `bash start.sh`, which:
   - Collects static files
   - Runs migrations
   - Starts Gunicorn on the assigned `$PORT`

## 📄 License

This project is for personal/private use.
