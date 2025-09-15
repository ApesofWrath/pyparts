# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated CI/CD of the Django Parts Website.

## Workflows Overview

### 🔄 CI Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**What it does:**
1. **Testing Phase:**
   - Sets up Python 3.12 environment
   - Installs dependencies from `requirements.txt`
   - Runs Django system checks
   - Executes database migrations
   - Collects static files
   - Runs Django test suite

2. **Building Phase** (only on main branch):
   - Builds Docker image using Docker Buildx
   - Pushes image to GitHub Container Registry (GHCR)
   - Uses multi-platform caching for faster builds

### 🚀 CD Pipeline (`cd.yml`)

**Triggers:**
- Git tags (e.g., `v1.0.0`, `v2.1.3`)
- Manual workflow dispatch with environment selection

**What it does:**
1. **Image Building:**
   - Builds Docker image with metadata
   - Tags images appropriately (version, environment, latest)
   - Pushes to GHCR

2. **Deployment Summary:**
   - Generates deployment summary in GitHub Actions
   - Provides usage instructions
   - Shows image tags and registry information

### 🔒 Security Scan (`security.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Weekly schedule (Mondays at 2 AM)

**What it does:**
1. **Code Scanning:**
   - Scans filesystem for vulnerabilities using Trivy
   - Uploads results to GitHub Security tab

2. **Docker Image Scanning:**
   - Builds Docker image
   - Scans image for vulnerabilities
   - Uploads results to GitHub Security tab

## Container Registry

Images are automatically pushed to GitHub Container Registry:

- **Registry:** `ghcr.io`
- **Repository:** `ghcr.io/your-username/your-repo`
- **Tags:**
  - `latest` - Latest from main branch
  - `main` - Latest from main branch
  - `v1.0.0` - Version tags
  - `staging` - Staging environment
  - `production` - Production environment

## Usage Examples

### Pull and Run Latest Image
```bash
# Pull the latest image
docker pull ghcr.io/your-username/your-repo:latest

# Run the container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgres://user:pass@host:5432/db \
  ghcr.io/your-username/your-repo:latest
```

### Use with Docker Compose
```yaml
version: '3.8'
services:
  web:
    image: ghcr.io/your-username/your-repo:latest
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-secret-key
      - DATABASE_URL=postgres://user:pass@db:5432/parts_db
```

### Deploy Specific Version
```bash
# Pull specific version
docker pull ghcr.io/your-username/your-repo:v1.2.3

# Run specific version
docker run -p 8000:8000 ghcr.io/your-username/your-repo:v1.2.3
```

## Manual Deployment

To manually trigger a deployment:

1. Go to **Actions** tab in GitHub
2. Select **CD** workflow
3. Click **Run workflow**
4. Choose environment (staging/production)
5. Click **Run workflow**

## Security

- All images are scanned for vulnerabilities
- Security reports are available in the **Security** tab
- Dependencies are cached for faster builds
- Multi-platform builds are supported

## Troubleshooting

### Common Issues

1. **Build Failures:**
   - Check the Actions tab for detailed logs
   - Ensure all dependencies are in `requirements.txt`
   - Verify Dockerfile syntax

2. **Permission Issues:**
   - Ensure `GITHUB_TOKEN` has proper permissions
   - Check repository settings for Actions permissions

3. **Registry Access:**
   - Images are public by default
   - For private images, configure package permissions

### Getting Help

- Check workflow logs in the Actions tab
- Review security scan results in the Security tab
- Check container registry in the Packages section
