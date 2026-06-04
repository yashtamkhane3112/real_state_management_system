# Real Estate Marketplace - Django Setup Guide

A complete, production-ready real estate marketplace built with Django, Bootstrap 5, and SQLite.

## Project Structure

```
real_estate/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
│
├── real_estate/             # Project settings
│   ├── __init__.py
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI application
│
├── users/                   # User management app
│   ├── models.py            # CustomUser model
│   ├── views.py             # Authentication & profile views
│   ├── forms.py             # Login & registration forms
│   ├── urls.py              # User URLs
│   └── admin.py             # Django admin configuration
│
├── properties/              # Property management app
│   ├── models.py            # Property, PropertyImage, Favorite models
│   ├── views.py             # Property listing & detail views
│   ├── forms.py             # Property forms
│   ├── urls.py              # Property URLs
│   └── admin.py             # Django admin configuration
│
├── inquiries/               # Inquiries & messaging app
│   ├── models.py            # Inquiry, Message, Transaction models
│   ├── views.py             # Inquiry & messaging views
│   ├── forms.py             # Inquiry forms
│   ├── urls.py              # Inquiry URLs
│   └── admin.py             # Django admin configuration
│
├── templates/               # Django templates
│   ├── base.html            # Base template (template inheritance)
│   ├── landing.html         # Landing/home page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── properties_list.html # Property listing with filters
│   ├── property_detail.html # Property details page
│   ├── dashboard_buyer.html # Buyer dashboard
│   ├── dashboard_seller.html# Seller dashboard
│   ├── dashboard_admin.html # Admin dashboard
│   ├── profile.html         # User profile page
│   ├── list_property.html   # Property listing form
│   ├── favorites.html       # Favorite properties
│   ├── messages.html        # Messages page
│   ├── contact.html         # Contact form
│   ├── inquiry_form.html    # Property inquiry form
│   └── partials/
│       ├── navbar.html      # Navigation bar component
│       └── footer.html      # Footer component
│
└── static/                  # Static files
    ├── css/
    │   └── style.css        # Main stylesheet (524 lines)
    └── js/
        └── main.js          # JavaScript functionality
```

## Features

### User Management
- **Three user roles**: Buyer, Seller, Super Admin
- **Authentication**: Email/password login with custom user model
- **Profile Management**: Full profile editing with image upload
- **Session Management**: Persistent login with Django sessions

### Property Management
- **Property Listings**: Create, edit, delete property listings
- **Advanced Search**: Filter by type, price, location, bedrooms/bathrooms
- **Image Gallery**: Upload and manage multiple images per property
- **Featured Properties**: Mark properties as featured on homepage
- **Property Views**: Track number of views per property

### Buyer Features
- **Property Search**: Advanced filtering and search functionality
- **Favorites**: Save properties to favorites
- **Inquiries**: Send inquiries to property owners
- **Dashboard**: View saved properties and inquiries
- **Messages**: Direct messaging with sellers

### Seller Features
- **Property Management**: Full CRUD operations for listings
- **Inquiry Management**: Respond to buyer inquiries
- **Property Analytics**: Track views and inquiries
- **Dashboard**: Overview of all listings and inquiries

### Admin Features
- **User Management**: Manage all users and roles
- **Property Moderation**: Approve/reject property listings
- **System Analytics**: View platform statistics
- **Django Admin Panel**: Full administrative control

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Django

```bash
pip install django==4.2.0
```

### Step 3: Navigate to Project

```bash
cd real_estate
```

### Step 4: Create Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin user
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 7: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Usage

### Access the Application

**Landing Page**: `http://localhost:8000/`

**Authentication**:
- Login: `http://localhost:8000/login/`
- Register: `http://localhost:8000/register/`

**Browse Properties**: `http://localhost:8000/properties/`

**Dashboards** (Authenticated users):
- Buyer Dashboard: `http://localhost:8000/dashboard/`
- Seller Dashboard: `http://localhost:8000/dashboard/` (for sellers)
- Admin Dashboard: `http://localhost:8000/dashboard/` (for admins)

**Admin Panel**: `http://localhost:8000/admin/`
- Username: (your superuser credentials)
- Password: (your superuser password)

### Create Test Data

1. Register a new account
2. Create property listings from the dashboard
3. Switch user roles in Django admin to test different features

## Database Models

### CustomUser
```
- username, email, password (Django auth)
- first_name, last_name
- role (buyer/seller/admin)
- phone, profile_picture
- bio, address, city, state, pincode
- is_verified, created_at, updated_at
```

### Property
```
- owner (FK to CustomUser)
- title, description, slug
- property_type, status
- address, city, state, pincode
- price, bedrooms, bathrooms, area
- thumbnail, images
- amenities, parking, balcony, garden, gym, pool, security
- is_featured, views, created_at, updated_at
```

### PropertyImage
```
- property (FK)
- image, alt_text, is_primary
- uploaded_at
```

### Favorite
```
- user (FK to CustomUser)
- property (FK to Property)
- created_at
```

### Inquiry
```
- property (FK)
- buyer (FK to CustomUser)
- subject, message
- phone, email
- status (pending/responded/closed)
- created_at, updated_at
```

### Message
```
- sender (FK to CustomUser)
- receiver (FK to CustomUser)
- subject, message
- is_read
- created_at
```

## URL Routes

```
/                           - Landing page
/login/                     - Login
/register/                  - Registration
/logout/                    - Logout
/profile/                   - User profile
/profile/<id>/              - Public profile
/dashboard/                 - Role-based dashboard
/properties/                - Property list with filters
/properties/<slug>/         - Property detail
/properties/create/         - Create property (seller only)
/properties/<slug>/edit/    - Edit property (seller only)
/properties/<slug>/delete/  - Delete property (seller only)
/properties/<slug>/favorite/- Toggle favorite
/properties/favorites/      - View favorites
/properties/my-properties/  - My properties (seller)
/inquiries/<slug>/inquiry/  - Submit inquiry
/inquiries/my-inquiries/    - My inquiries (buyer)
/inquiries/property-inquiries/ - Property inquiries (seller)
/inquiries/messages/        - Messages list
/inquiries/conversation/<id>/  - Conversation with user
/contact/                   - Contact form
/admin/                     - Django admin panel
```

## Customization

### Change Theme Colors
Edit `/static/css/style.css` - Look for `:root` CSS variables at the top:

```css
:root {
    --primary-color: #003d82;      /* Main color */
    --secondary-color: #0056b3;    /* Secondary color */
    --accent-color: #28a745;       /* Accent color */
    --danger-color: #dc3545;       /* Error/danger color */
}
```

### Add Custom Fields to Models
Edit the model in `/models.py`, then:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Extend Functionality
All code follows Django best practices:
- Models in `/models.py`
- Views in `/views.py`
- URL routing in `/urls.py`
- Forms in `/forms.py`
- Templates in `/templates/`

## Best Practices Implemented

✓ **Security**
- CSRF protection on all forms
- Password hashing with Django's authentication
- SQL injection prevention with ORM
- XSS protection in templates

✓ **Performance**
- Database query optimization with select_related/prefetch_related
- Static file optimization
- Caching-ready structure

✓ **Scalability**
- Modular app architecture
- Reusable components
- Template inheritance
- Flexible model structure

✓ **Maintainability**
- Clear code organization
- Comprehensive comments
- Bootstrap 5 for responsive design
- Consistent naming conventions

## Troubleshooting

**ModuleNotFoundError**: Make sure you've installed Django:
```bash
pip install django==4.2.0
```

**Database errors**: Run migrations:
```bash
python manage.py migrate
```

**Static files not loading**: Run:
```bash
python manage.py collectstatic
```

**Image uploads not working**: Ensure `/media/` directory exists and has write permissions.

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS` with your domain
3. Use a production database (PostgreSQL recommended)
4. Use a production web server (Gunicorn + Nginx)
5. Set up HTTPS with SSL certificate
6. Configure environment variables

## License

This is a college project - feel free to use and modify as needed.

## Support

For issues or questions, refer to:
- Django Documentation: https://docs.djangoproject.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/
- Project structure follows Django best practices

---

**Version**: 1.0
**Last Updated**: 2024
**Tested on**: Django 4.2, Python 3.8+, Bootstrap 5.3
