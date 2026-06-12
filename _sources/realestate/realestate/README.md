# Real Estate Property Management & Marketplace (Django)

A full-featured real estate marketplace built with Django + Bootstrap 5 + SQLite.

## Features

- **Buyer**: Register/Login, search & filter properties, save favorites, send inquiries, manage profile.
- **Seller**: Register/Login, add/edit/delete listings, upload images, manage inquiries, mark as sold.
- **Super Admin**: Manage users, approve/reject listings, view analytics.

## Tech Stack

- Python Django (MVT)
- SQLite
- HTML5, CSS3, Bootstrap 5, JavaScript
- Django Authentication + custom role-based access control

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser (Super Admin)
python manage.py createsuperuser

# 5. Run the server
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Project Structure

```
realestate/
├── manage.py
├── requirements.txt
├── realestate/         # Project settings
├── accounts/           # User registration, login, profile, roles
├── properties/         # Property CRUD, search, inquiries, favorites
├── dashboard/          # Buyer / Seller / Admin dashboards
├── templates/          # Bootstrap 5 templates
├── static/css/         # Custom styling
└── media/              # Uploaded property images
```

## Default Roles

- `buyer`  – browse, favorite, inquire
- `seller` – create and manage listings
- `admin`  – created via `createsuperuser`, full platform access

## Notes for Students

- Code is intentionally beginner-friendly and well-commented.
- Designed for a team of 4 students over ~15 days.
- Suggested split: Auth (1), Property CRUD (1), Dashboards/Admin (1), UI/UX + templates (1).
