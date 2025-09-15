# WSGI configuration for Django application
# This file is used by Gunicorn to serve the Django application

from parts.wsgi import application

# Gunicorn looks for a WSGI-compatible object called 'application'
app = application