#!/bin/bash

# Script to promote an existing user to admin in the production Docker container
# Usage: ./docker_make_admin.sh <container_name> <email> [--create-if-not-exists] [--password <password>]

set -e

CONTAINER_NAME=${1:-"parts_website-web-1"}
EMAIL=${2:-"rahil@apesofwrath668.org"}
CREATE_IF_NOT_EXISTS=${3:-""}
PASSWORD=${4:-""}

echo "Promoting user '$EMAIL' to admin in container '$CONTAINER_NAME'..."

# Execute the Django management command in the running container
if [ "$CREATE_IF_NOT_EXISTS" = "--create-if-not-exists" ]; then
    docker exec -it "$CONTAINER_NAME" python manage.py create_admin "$EMAIL" --create-if-not-exists --password "$PASSWORD"
else
    docker exec -it "$CONTAINER_NAME" python manage.py create_admin "$EMAIL"
fi

echo "Done! User '$EMAIL' is now an admin."
echo "They can access the Django admin at: http://your-domain/admin/"
