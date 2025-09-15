#!/bin/bash

# Script to promote an existing user to admin on the production server
# Usage: ./make_admin.sh <email> [--create-if-not-exists] [--password <password>]

set -e

EMAIL=${1:-"rahil@apesofwrath668.org"}
CREATE_IF_NOT_EXISTS=${2:-""}
PASSWORD=${3:-""}

echo "Promoting user '$EMAIL' to admin..."

# Check if we're running in Docker
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container..."
    if [ "$CREATE_IF_NOT_EXISTS" = "--create-if-not-exists" ]; then
        python manage.py create_admin "$EMAIL" --create-if-not-exists --password "$PASSWORD"
    else
        python manage.py create_admin "$EMAIL"
    fi
else
    echo "Running on host system..."
    # If running on host, you might need to activate virtual environment
    # source venv/bin/activate  # Uncomment if using virtual environment
    
    # Run the management command
    if [ "$CREATE_IF_NOT_EXISTS" = "--create-if-not-exists" ]; then
        python manage.py create_admin "$EMAIL" --create-if-not-exists --password "$PASSWORD"
    else
        python manage.py create_admin "$EMAIL"
    fi
fi

echo "Done! User '$EMAIL' is now an admin."
echo "They can access the Django admin at: http://your-domain/admin/"
