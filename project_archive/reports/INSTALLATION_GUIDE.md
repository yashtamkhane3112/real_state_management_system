# PropVista Installation Guide

Follow these steps to set up and run PropVista locally in a fresh python environment:

## Prerequisites
- **Python**: Version 3.12 or higher recommended.
- **pip**: Python package manager.

## Setup Instructions

1. **Create a Python Virtual Environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**:
   - **Windows**:
     ```powershell
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Seed the Database with Premium Demo Data**:
   This seeds the database with demo users, 20 properties, active inquiries, favorites, visits, and leads.
   ```bash
   python manage.py seed
   ```

6. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/`.
