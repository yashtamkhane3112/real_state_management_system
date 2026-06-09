# Project Context for AI Assistant

PropVista is a premium, SaaS-grade Real Estate Operating System and CRM built using Python, Django, Vanilla CSS, and JavaScript.

## 1. Tech Stack & Architecture
- **Framework**: Django 5.0.14
- **Database**: SQLite 3 (Django ORM)
- **Frontend Core**: HTML5, Vanilla CSS3 (custom theme, glassmorphism UI variables), Bootstrap 5.3.3
- **Interactive Assets**: JavaScript, Leaflet.js (maps mapping), Swiper.js (sliders), Chart.js (dashboard analytics), Three.js (landing page skyline canvas animation)
- **Testing**: pytest & pytest-django

## 2. Directory Layout & Folder Structure
```text
E:\PropVista_Final\
├── accounts/          # Authentication, Profile models, User roles and dashboard views
├── analytics/         # View counts tracking and global AuditLog database models
├── properties/        # Listings management, creation/edit forms, approvals moderation
├── inquiries/         # Buyer-generated contact inquiries
├── leads/             # CRM pipeline leads for Agent role
├── notifications/     # Signals-driven notifications dropdown in navigation bar
├── visits/            # Site visit schedules
├── search/            # User query histories and saved search alerts
├── reports/           # Admin performance audit logs and PDF/Excel generation routes
├── propvista/         # Django core project configuration (settings, context, urls)
├── static/            # Static assets (css/app.css, js/app.js)
├── templates/         # HTML template files (base.html, layout structures)
└── archive/           # Unused files, dead code, or obsolete apps moved for safety
```

## 3. User Roles & Workspace Matrix
PropVista implements strict role-based workspaces:
1. **Buyer**: Browse listings, save properties to wishlist, submit inquiries, track site visits.
2. **Seller**: Create/edit property listings, upload high-res images, manage inquiries, and track approval statuses.
3. **Agent**: Access CRM pipeline Kanban board, scheduled visits, and manage leads conversion.
4. **Admin**: Executive oversight, approve/reject property listings with reasoning (POST-only moderation), manage users and inquiries.

## 4. Key Security & Safety Hardening
- **POST-Only Moderation**: Property approvals and rejections require a POST request with CSRF protection. Direct URL navigation via GET is prohibited.
- **File Upload Safety**: Character truncation (<50 chars) and sanitization implemented across Cover Images, Gallery Photos, and Profile Avatars to prevent SQL column overflows or filesystem issues.
- **Role Permissions**: Middleware and decorators prevent cross-role workspace access leaks (e.g. buyers cannot access seller/admin endpoints).

## 5. Quick Start Setup
To start the project in a fresh environment, run:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```
Demopassword for all seeded accounts: `Pass@12345`

## 6. Future Roadmap
- **Payment Gateways**: Integrate Stripe or Razorpay for seller subscriptions and listing promotions.
- **Virtual Tours**: Live WebRTC-based remote call tours within the property page.
- **Geo-Proximity Alerts**: Auto-notification alerts based on buyer search radiuses.
