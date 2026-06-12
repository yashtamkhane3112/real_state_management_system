# PropVista

PropVista is a portfolio-ready real estate marketplace built with Django, Django REST Framework, Bootstrap 5, GSAP, Three.js, Chart.js, Google Maps hooks, Gemini AI fallback, standard Django session auth for pages, and JWT auth for REST APIs.

## Quick Start

```powershell
cd propvista
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Open `http://localhost:8000`.

Demo users all use password `Pass@12345`:

- `buyer`
- `seller`
- `agent`
- `admin`
- `superadmin`

## Environment

Copy `.env.example` to `.env` if you want custom settings.

`DATABASE_URL` is optional. If it is blank, Django uses local SQLite so the app runs with no extra service. For PostgreSQL, set:

```text
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/propvista
```

`GOOGLE_MAPS_API_KEY` enables live maps. Without it, pages still render.

`GEMINI_API_KEY` enables Gemini AI. Without it, AI endpoints return helpful fallback responses.

## URLs

- Homepage: `/`
- Properties: `/properties/`
- Login: `/accounts/login/`
- Register: `/accounts/register/`
- Dashboard router: `/accounts/dashboard/`
- Swagger docs: `/api/docs/`
- JWT token: `/api/v1/auth/token/`
- Properties API: `/api/v1/properties/`

## Verification

```powershell
venv\Scripts\activate
python manage.py check
python manage.py migrate
python manage.py seed
python -m pytest
```

API smoke checks:

```powershell
python manage.py runserver
```

Then open:

- `http://localhost:8000`
- `http://localhost:8000/api/docs/`
- `http://localhost:8000/api/v1/properties/`

## Scope

Implemented MVP:

- Custom user model with Buyer, Seller, Agent, Admin roles.
- Standard Django session login/logout for templates.
- JWT authentication for REST APIs.
- Role dashboard routing and protected pages.
- Property categories, amenities, CRUD, images, approval workflow, featured listings.
- Public search filters by keyword, city, locality, price, area, bedrooms, bathrooms, type, amenities, and sorting.
- Buyer wishlist, inquiries, visits.
- Seller listing dashboard and inquiry metrics.
- Agent lead CRM dashboard.
- Admin approval queue, analytics charts, user/platform stats.
- Three.js animated homepage skyline.
- GSAP page/card transitions and JavaScript tilt property cards.
- Chart.js dashboard/report charts.
- Google Maps integration hooks for listing/detail maps.
- Gemini AI feature endpoints with graceful fallback.
- Seed data with demo users, 20 properties, inquiries, favorites, visits, and leads.
- Tests for registration, login, property search, and dashboard access.

