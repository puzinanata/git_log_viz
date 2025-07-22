#!/bin/bash
# Deployment on LFS VM
set -e
set -x

# Come back to root directory
cd

# Step 1: Pull or clone my project
REPO_URL="https://github.com/puzinanata/git_log_viz"
PROJECT_PATH="git_log_viz/"

if [ ! -d "$PROJECT_PATH" ]; then
    git clone "$REPO_URL" "$PROJECT_PATH"
    cd "$PROJECT_PATH"
else
    cd "$PROJECT_PATH"
    git pull
fi

# Step 2: Set up and activation virtual environment
python3 -m venv venv
source venv/bin/activate
echo "Virtual environment activated."

# Step 3:
echo "Creating directory for Git repositories: /var/lib/git_repos"
mkdir -p "/var/lib/git_repos"
chown "$USER":"$USER" "/var/lib/git_repos"
chmod 755 "/var/lib/git_repos"

# Step 4: Install requirements
pip3 -v install -r deployment_vm/requirements.txt
echo "Dependencies installed successfully."

# Step 5: Add venv to .gitignore
echo "venv/" >> myproject/.gitignore

# Step 6: Run Django migrations
echo "Navigating to the project directory..."
cd myproject/
echo "Running migrations and collecting static files..."
python3 manage.py migrate
python3 manage.py collectstatic --noinput
echo "Migrations and static files collection completed."


echo "Starting Django runserver..."
python3 manage.py runserver
