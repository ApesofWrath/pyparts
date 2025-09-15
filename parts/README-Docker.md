# Docker Deployment Guide

This Django application has been containerized for easy deployment in production environments with automated CI/CD pipelines using GitHub Actions.

## Quick Start

1. **Copy environment variables:**
   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file with your actual values:**
   - Set a strong `SECRET_KEY`
   - Configure your Google OAuth credentials
   - Set your Slack token if using Slack integration

3. **Run with pre-built image:**
   ```bash
   docker-compose up
   ```

   **Or for development (builds locally):**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

4. **Access the application:**
   - Web application: http://localhost:8000

## Services

The Docker Compose setup includes:

- **web**: Django application server (Gunicorn)
- **db**: PostgreSQL database

**Note**: Nginx is not included in the Docker setup and should be configured externally.

## GitHub Actions CI/CD

This project includes automated CI/CD pipelines that:

### Continuous Integration (CI)
- **Triggers**: Push to `main`/`develop` branches, pull requests
- **Testing**: Runs Django tests with PostgreSQL database
- **Building**: Builds Docker image and pushes to GHCR on main branch
- **Security**: Scans for vulnerabilities using Trivy

### Continuous Deployment (CD)
- **Triggers**: Git tags (e.g., `v1.0.0`), manual workflow dispatch
- **Building**: Builds and pushes Docker images to GitHub Container Registry
- **Tagging**: Automatically tags images with version, environment, and `latest`

### Available Workflows

1. **CI Pipeline** (`.github/workflows/ci.yml`)
   - Runs tests and builds images on every push/PR
   - Pushes to GHCR only on main branch

2. **CD Pipeline** (`.github/workflows/cd.yml`)
   - Deploys on version tags and manual triggers
   - Supports staging/production environments

3. **Security Scan** (`.github/workflows/security.yml`)
   - Scans code and Docker images for vulnerabilities
   - Runs weekly and on every push/PR

### Using Pre-built Images

Images are automatically built and available at:
```
ghcr.io/apesofwrath/pyparts:latest
ghcr.io/apesofwrath/pyparts:main
ghcr.io/apesofwrath/pyparts:v1.0.0
```

The Docker Compose files are already configured to use the pre-built image:
```bash
# Run with pre-built image (default)
docker-compose up

# Run with specific version
docker-compose up --pull always
```

For development with local builds:
```bash
# Use development compose file
docker-compose -f docker-compose.dev.yml up --build
```

## Production Deployment

### Environment Variables

Make sure to set these environment variables in production:

- `SECRET_KEY`: Django secret key (generate a new one)
- `DEBUG`: Set to `False` in production
- `DATABASE_URL`: PostgreSQL connection string
- `G_CLIENT_ID`: Google OAuth client ID
- `G_SECRET`: Google OAuth client secret
- `SLACK_TOKEN`: Slack bot token (optional)

### External Nginx Configuration

The application is designed to work with an external nginx installation. Use the provided nginx configuration files:

- `nginx.conf` - Basic configuration for development/testing
- `nginx.prod.conf` - Production configuration with SSL support

**To configure nginx:**

1. Copy the appropriate nginx config to your nginx sites directory
2. Update the following paths in the config:
   - `server_name` - Replace with your actual domain
   - `upstream django_parts` - Point to your Docker container IP/port
   - Static files path - Point to your static files location
   - Media files path - Point to your media files location
   - SSL certificate paths (for production)

3. Test and reload nginx configuration

### Security Considerations

1. **Change the default database credentials** in `docker-compose.yml`
2. **Use a strong SECRET_KEY** for Django
3. **Set up proper SSL/TLS** termination with your external nginx
4. **Configure proper ALLOWED_HOSTS** for your domain
5. **Use environment-specific settings** for different deployments
6. **Configure nginx security headers** (included in provided configs)

### Scaling

To scale the web service:

```bash
docker-compose up --scale web=3
```

**Note**: When scaling, update your nginx upstream configuration to include all web service instances.

### Database Migrations

Run migrations manually if needed:

```bash
docker-compose exec web python manage.py migrate
```

### Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

**Note**: After collecting static files, ensure your nginx configuration points to the correct static files directory.

### Create Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

## File Storage

The application uses local file storage by default. For production, consider:

- AWS S3
- Azure Blob Storage
- Google Cloud Storage
- MinIO

Update the `DEFAULT_FILE_STORAGE` setting in `settings.py` accordingly.

## Nginx Integration

### Static Files Setup

1. **Collect static files** from your Django container:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

2. **Copy static files** to your nginx server:
   ```bash
   # Copy from Docker volume to nginx server
   docker cp $(docker-compose ps -q web):/app/static /path/to/nginx/static/
   ```

3. **Update nginx configuration** to point to the correct static files path.

### Media Files Setup

1. **Create media directory** on your nginx server
2. **Update nginx configuration** to point to the media files location
3. **Ensure proper permissions** for nginx to serve media files

## Monitoring

Consider adding monitoring solutions like:

- Prometheus + Grafana
- ELK Stack
- DataDog
- New Relic

## Backup Strategy

Set up regular backups for:

- PostgreSQL database
- Media files
- Static files

Example backup command:
```bash
docker-compose exec db pg_dump -U parts_user parts_db > backup.sql
```
