# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Ensure static directories exist
RUN mkdir -p /app/static /app/parts_site/static

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Create media directory for file uploads
RUN mkdir -p /app/media

# Set a temporary SECRET_KEY for build-time operations
ENV SECRET_KEY=temp-secret-key-for-build
ENV DEBUG=False
ENV DATABASE_URL=sqlite:///db.sqlite3

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/media
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "parts.wsgi:application"]
