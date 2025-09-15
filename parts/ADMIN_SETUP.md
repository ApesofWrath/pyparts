# Admin User Setup

## Quick Setup for rahil@apesofwrath668.org

### Option 1: Using Docker Compose (Recommended)
```bash
# Make the user an admin
docker-compose exec web python manage.py create_admin rahil@apesofwrath668.org --password "your-secure-password"

# Or if using docker compose (newer syntax)
docker compose exec web python manage.py create_admin rahil@apesofwrath668.org --password "your-secure-password"
```

### Option 2: Using Docker Exec
```bash
# Find the container name first
docker ps

# Then run the command (replace 'container_name' with actual container name)
docker exec -it <container_name> python manage.py create_admin rahil@apesofwrath668.org --password "your-secure-password"
```

### Option 3: Using the provided script
```bash
# Make the script executable (if not already)
chmod +x docker_make_admin.sh

# Run the script
./docker_make_admin.sh <container_name> rahil@apesofwrath668.org "your-secure-password"
```

## What the script does:
1. Creates the user if they don't exist
2. Makes them a staff user (can access admin)
3. Makes them a superuser (full admin privileges)
4. Activates the user account
5. Adds them to admin group (if it exists)

## After running:
- The user can access Django admin at: `http://your-domain/admin/`
- They can log in with their email and password
- They have full admin privileges

## Security Note:
- Use a strong password
- Consider changing the password after first login
- The user will have full access to the Django admin interface
