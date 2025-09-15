#!/bin/bash

# Script to make a user an admin on the production server
# Usage: ./make_admin.sh <email> [password]

set -e

EMAIL=${1:-"rahil@apesofwrath668.org"}
PASSWORD=${2:-""}

echo "Making user '$EMAIL' an admin..."

# Check if we're running in Docker
if [ -f /.dockerenv ]; then
    echo "Running inside Docker container..."
    python manage.py create_admin "$EMAIL" --password "$PASSWORD"
else
    echo "Running on host system..."
    # If running on host, you might need to activate virtual environment
    # source venv/bin/activate  # Uncomment if using virtual environment
    
    # Run the management command
    python manage.py create_admin "$EMAIL" --password "$PASSWORD"
fi

echo "Done! User '$EMAIL' is now an admin."
echo "They can access the Django admin at: http://your-domain/admin/"
