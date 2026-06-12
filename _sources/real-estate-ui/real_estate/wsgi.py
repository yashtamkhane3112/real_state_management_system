"""
WSGI config for real_estate project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate.settings')

application = get_wsgi_application()
