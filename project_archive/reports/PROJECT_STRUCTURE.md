# Project Structure

PropVista is a premium, SaaS-grade Real Estate Operating System and CRM built using modular Django applications sharing a unified design system.

## 1. Directory Layout

The workspace is structured as follows:

```text
E:\PropVista_Final\
├── accounts/          # Authentication, User Profile models, role-based dashboards (Buyer, Seller, Agent, Admin)
├── analytics/         # Page/Property View tracking, global audit logging models
├── archive/           # Cleaned/Archived components (e.g. decommissioned ai_features, unused templates)
├── favorites/         # Shortlisted properties (wishlist) database models and AJAX endpoints
├── inquiries/         # Contact inquiries submitted on property details
├── leads/             # CRM pipeline stages (New, Contacted, Visit, Negotiation, Won, Lost) for agents
├── notifications/     # Signals-driven inbox notifications triggered by user actions
├── properties/        # Listings management, creation/editing forms, approvals workflow, featured rail
├── propvista/         # Core Django configurations (settings, root urls, context processors)
├── reports/           # Admin system auditing and reports view
├── search/            # Search query logging and saved search alerts
├── static/            # Static assets (fonts, custom variables, css/app.css, js/app.js)
├── templates/         # HTML templates (base.html structure, dashboard controls, partials)
├── tests/             # Pytest unit tests verifying core modules and access controls
├── visits/            # Site visit scheduling and status tracking
├── venv/              # Python virtual environment (ignored in distribution)
├── db.sqlite3         # SQLite3 database file (pre-seeded with demo data)
├── manage.py          # Django management script
├── requirements.txt   # Python dependency list
├── INSTALLATION_GUIDE.md # Standard installation manual
└── README.md          # Project introduction and quickstart instructions
```

## 2. Main Applications Details

- **`accounts`**: Custom `User` model inheriting from `AbstractUser` featuring four roles: `Buyer`, `Seller`, `Agent`, `Admin`. Implements profile configurations (`Profile` model), avatar uploads, and role-based redirect dashboards.
- **`properties`**: The core listing app. Manages `Property`, `Category`, `Amenity`, and `PropertyImage` objects. Implements status state-machines (Active, Inactive, Sold, Rented) and moderation workflow (Draft, Pending, Approved, Rejected).
- **`inquiries`**: Integrates a buyer message pipeline allowing users to contact listing owners. Includes status workflows (New, Contacted, Qualified, Closed).
- **`leads`**: Agent CRM tool that maps client leads into pipeline stages, track lead scores, follow-up times, and feeds into agent dashboard metrics.
- **`favorites`**: Implements dynamic wishlist bookmarks utilizing Django AJAX/JSON endpoints and session persistence.
- **`analytics`**: Logs property details visit views via `PropertyViewEvent` and monitors administrator/user mutations via a centralized `AuditLog`.
- **`notifications`**: Dispatches system events like property approvals, inquiries, and visit schedules to custom inboxes dynamically rendered in the global navigation shell.
- **`reports`**: Evaluates platform indicators (conversion, markets tracked, pipeline values) using real DB records.
- **`visits`**: Coordinates buyer site-visit requests. Includes a state-machine (Requested, Confirmed, Completed, Cancelled).

## 3. Core Frontend Configuration

- **`templates/base.html`**: Root layout file managing standard meta headers, responsive layouts, Leaflet map dependencies, and Three.js canvas integration.
- **`static/css/app.css`**: Comprehensive CSS style sheets containing the CSS variables design system, custom typography (Inter, Playfair Display), responsive grids, dark/glassmorphic components, and dynamic transition classes.
- **`static/js/app.js`**: Core interactive script handling animated counters, GSAP animation hooks, navbar toggles, modal dialogues, AJAX favorites, and dynamic map layers.
