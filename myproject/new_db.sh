#!/bin/bash

# Remove existing database file if it exists
if [ -f "db.sqlite3" ]; then
    echo "Removing old database..."
    rm db.sqlite3
fi

# Run migrations to create a fresh database
echo "Running migrations..."
python3 manage.py migrate

# Prompt for the superuser password securely
echo -n "Enter password for the superuser: "
read -s superuser_password
echo

echo "Creating superuser..."

python3 manage.py shell <<EOF
from django.contrib.auth.models import User

username = "natalapuzina"
email = "puzinanata@gmail.com"
password = "$superuser_password"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser {username} created successfully.")
else:
    print(f"Superuser {username} already exists.")
EOF

echo " Database update complete."
