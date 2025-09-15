#!/usr/bin/env python
"""
Temporary script to disable CSRF for testing purposes.
WARNING: This should only be used for testing, not in production!
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts.settings')
django.setup()

from django.conf import settings

print("Current CSRF_TRUSTED_ORIGINS:")
for origin in settings.CSRF_TRUSTED_ORIGINS:
    print(f"  - {origin}")

print("\nTo fix CSRF issues, add your domain to CSRF_TRUSTED_ORIGINS:")
print("1. Set environment variable: CSRF_TRUSTED_ORIGINS=https://yourdomain.com")
print("2. Or update the settings.py file directly")
print("3. Restart your Django application")

print("\nFor immediate testing, you can temporarily disable CSRF by adding this to settings.py:")
print("CSRF_COOKIE_SECURE = False")
print("CSRF_TRUSTED_ORIGINS = ['*']")
print("(WARNING: Only for testing, not production!)")
