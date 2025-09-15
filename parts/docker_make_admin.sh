#!/bin/bash

# Script to make a user an admin in the production Docker container
# Usage: ./docker_make_admin.sh <container_name> <email> [password]

set -e

CONTAINER_NAME=${1:-"parts_website-web-1"}
EMAIL=${2:-"rahil@apesofwrath668.org"}
PASSWORD=${3:-"admin123456"}

echo "Making user '$EMAIL' an admin in container '$CONTAINER_NAME'..."

# Execute the Django management command in the running container
docker exec -it "$CONTAINER_NAME" python manage.py create_admin "$EMAIL" --password "$PASSWORD"

echo "Done! User '$EMAIL' is now an admin."
echo "They can access the Django admin at: http://your-domain/admin/"
