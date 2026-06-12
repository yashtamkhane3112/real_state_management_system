# EstateSphere - Real Estate Sales and Purchase Management System

A Django mini-project for property selling and purchasing.

## Features
- Buyer, Seller, and Super Admin roles
- Seller property listing
- Super Admin approval/rejection
- Buyer property search and favorites
- Inquiry with console email notification
- Sale and purchase transaction record
- Reports with PDF export
- Google Maps placeholder, image gallery, recommendation section
- Bootstrap 5, custom CSS, JS, SQLite

## Setup
```bash
cd estate_sales_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Demo users:
- admin / admin12345
- seller / seller12345
- buyer / buyer12345
