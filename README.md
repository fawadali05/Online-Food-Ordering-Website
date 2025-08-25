# Online Food Ordering Website (Django + SQLite)

A simple restaurant website with menu, cart, order booking, user accounts, order tracking, and an admin panel.

## Features
- Menu with categories & prices
- Session-based cart (add/update/remove)
- Checkout creates an Order + OrderItems
- User login/register and profile (phone, address)
- Order tracking page & "My Orders" list
- Admin panel to manage categories, items, and order statuses
- Email confirmation on successful checkout (console backend by default)
- Bootstrap 5 for responsive UI
- SQLite by default

## Quick Start (Local)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # for admin access
python manage.py runserver
```

Open http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

## Seed Data (Optional)
Log in to admin and add a few Categories (e.g., Burgers, Pizza, Drinks) and MenuItems.

## Email Setup
By default, emails print to the console. To send real emails, set env vars:
```bash
export DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.yourhost.com
export EMAIL_PORT=587
export EMAIL_HOST_USER=your@domain.com
export EMAIL_HOST_PASSWORD=secret
export EMAIL_USE_TLS=1
export DJANGO_DEFAULT_FROM_EMAIL=orders@yourdomain.com
```

## Deployment on PythonAnywhere (Basic)
1. Create a new PythonAnywhere account.
2. Upload this project zip, and unzip it in your home directory.
3. Create a virtualenv and install requirements: `pip install -r requirements.txt`
4. Run `python manage.py migrate` and `python manage.py createsuperuser`.
5. On the **Web** tab, add a new Django app and point the **WSGI file** to `foodorder/wsgi.py` (update the path accordingly).
6. Set `DJANGO_SETTINGS_MODULE=foodorder.settings` in the web app's environment variables.
7. Reload the web app.

## Tech Stack
- Django, SQLite, Bootstrap