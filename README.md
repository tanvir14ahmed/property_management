# Property Management

This Django 5.2 web app is focused on property/tenant workflows, custom authentication, chat, payments, and notifications while staying cPanel-friendly.

## Local setup

1. Install Python 3.12 and run `python -m venv .venv`.
2. Activate the virtualenv:
   ```powershell
   .venv\\Scripts\\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and adjust credentials (especially MySQL/SMTP).
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser, seed demo data, and run the development server:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_demo
   python manage.py runserver
   ```

## cPanel deployment notes

- Use the bundled `wsgi.py` entry point and point your cPanel application to `property_management.wsgi`.
- Populate `.env` with real secrets, especially `DJANGO_SECRET_KEY` and production `ALLOWED_HOSTS`.
- Ensure `STATIC_ROOT` and `MEDIA_ROOT` directories are writable and configure Apache/NGINX to serve them.
- Use environment-managed MySQL credentials and configure `MYSQL_*` variables accordingly.
- Set `DJANGO_DEBUG=False` and secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`).

## Next steps

- Fine-tune the remaining templates and dashboards (role-aware navigation, search filters, user onboarding).
- Expand PDF invoice styling and email/notification templates.
- Extend the test suite if you add more business rules or APIs.
