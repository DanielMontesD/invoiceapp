# Invoice App

A Django web application for freelancers to manage clients, track billable hours, and generate professional invoices with PDF export.

## Features

### Client Management
- Create, view, edit, and deactivate clients
- Search clients by name or email; filter by active/inactive status
- View last 5 invoices per client directly from the client list
- Total Paid stat per client (paid invoices only)

### Invoice Management
- Flexible billing periods: weekly, fortnightly, monthly, or custom date range
- Per-client sequential invoice numbering (00001, 00002, … restarting for each client)
- Status workflow: Draft → Sent → Overdue → Paid with inline dropdown
- Edit invoices after creation
- Duplicate an existing invoice with one click
- PDF export via xhtml2pdf

### Dashboard
- Total earned, pending, invoice counts at a glance
- Filter stats by client and/or date range
- Recent invoices with inline status update

### Authentication
- User registration with email, login, logout
- Forgot password flow (email reset link)
- User profile page (name, business details, contact info)
- Per-user data isolation — each user sees only their own clients and invoices

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 |
| Language | Python 3.11 |
| Database | Supabase (PostgreSQL) via `dj-database-url` |
| PDF Engine | xhtml2pdf + ReportLab |
| Static Files | WhiteNoise |
| WSGI Server | Gunicorn |
| Deployment | Render |
| Config | python-decouple (`.env` files) |

## Local Setup

### Prerequisites
- Python 3.11+
- A [Supabase](https://supabase.com) project (free tier works)

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

   Edit `.env` with your values:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```

   Get your `DATABASE_URL` from: Supabase Dashboard → Project Settings → Database → Connection string → Session pooler (IPv4 compatible).

5. **Run migrations**
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

   Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) — redirects to login.

## Deployment (Render)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repository, branch `main`
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `bash start.sh`
5. Add environment variables:

   | Variable | Value |
   |---|---|
   | `SECRET_KEY` | A long random string |
   | `DATABASE_URL` | Your Supabase session pooler URL |
   | `CSRF_TRUSTED_ORIGINS` | `https://your-app.onrender.com` |
   | `ADMIN_URL` | A secret path for the admin panel e.g. `myadmin123/` |
   | `WEB_CONCURRENCY` | `2` |

The `start.sh` script automatically runs `collectstatic`, `migrate`, and starts Gunicorn on deploy.

## Project Structure

```
invoiceapp/
├── billing/
│   ├── forms.py          # InvoiceForm, ClientForm, RegisterForm, UserProfileForm
│   ├── models.py         # Client, Invoice, WorkEntry, UserProfile
│   ├── urls.py           # App URL routes
│   └── views.py          # All view logic
├── invoicegen/
│   ├── settings.py           # Base/development settings
│   ├── settings_production.py # Production overrides
│   ├── urls.py               # Root URL config
│   └── wsgi_production.py    # Production WSGI entry point
├── templates/
│   ├── base.html
│   └── billing/
├── manage.py
├── requirements.txt
├── Procfile
├── start.sh
└── .env.example
```

## License

Private use only.
