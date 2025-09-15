# Admin User Setup

## Quick Setup for rahil@apesofwrath668.org

### Option 1: Promote Existing User (Recommended)
```bash
# Promote an existing user to admin (no password needed)
docker-compose exec web python manage.py create_admin rahil@apesofwrath668.org

# Or if using docker compose (newer syntax)
docker compose exec web python manage.py create_admin rahil@apesofwrath668.org
```

### Option 2: Create New User and Make Admin
```bash
# Create a new user and make them admin
docker-compose exec web python manage.py create_admin rahil@apesofwrath668.org --create-if-not-exists --password "your-secure-password"
```

### Option 3: Using Docker Exec
```bash
# Find the container name first
docker ps

# Promote existing user (replace 'container_name' with actual container name)
docker exec -it <container_name> python manage.py create_admin rahil@apesofwrath668.org

# Or create new user
docker exec -it <container_name> python manage.py create_admin rahil@apesofwrath668.org --create-if-not-exists --password "your-secure-password"
```

### Option 4: Using the provided script
```bash
# Make the script executable (if not already)
chmod +x docker_make_admin.sh

# Promote existing user
./docker_make_admin.sh <container_name> rahil@apesofwrath668.org

# Or create new user
./docker_make_admin.sh <container_name> rahil@apesofwrath668.org --create-if-not-exists --password "your-secure-password"
```

## What the script does:
1. **For existing users**: Promotes them to admin (no password needed)
2. **For new users**: Creates them and makes them admin (password required)
3. Makes them a staff user (can access admin)
4. Makes them a superuser (full admin privileges)
5. Activates the user account
6. Adds them to admin group (if it exists)
7. **Safety check**: Won't create users unless explicitly requested

## Key Features:
- ✅ **Safe by default**: Won't create users unless you use `--create-if-not-exists`
- ✅ **Idempotent**: Can be run multiple times safely
- ✅ **Checks existing status**: Won't duplicate admin privileges
- ✅ **Clear feedback**: Shows what action was taken

## After running:
- The user can access Django admin at: `http://your-domain/admin/`
- They can log in with their email and password
- They have full admin privileges

## Security Note:
- The script is safe to run on existing users
- Only creates new users when explicitly requested
- Use strong passwords for new users
- The user will have full access to the Django admin interface
