#!/bin/bash
# Deployment on Ubuntu/Debian VM

# Come back to root directory
cd
# Stop script if any command fails
set -e
# Turn off exit mode
#set +e

# Turn on debugging mode
set -x
# Turn off debugging mode
#set +x

# Step 0: Install required packages
REQUIRED_PACKAGES="git
    nginx
    python3
    python3-pip
    python3-venv"

apt update

DEBIAN_FRONTEND=noninteractive apt install -y $REQUIRED_PACKAGES
echo "All required packages installed!"

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
pip install -r deployment_vm/requirements.txt
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

# Step 7: Configure Nginx
GITREPORT_CONF="../deployment_vm/gitreport.conf"
NGINX_CONF_DEST="/etc/nginx/sites-available/gitreport"
NGINX_ENABLED="/etc/nginx/sites-enabled/gitreport"


cp "$GITREPORT_CONF" "$NGINX_CONF_DEST"
ln -sf "$NGINX_CONF_DEST" "$NGINX_ENABLED"
rm -f /etc/nginx/sites-enabled/default
nginx

echo "Starting Django runserver..."
python3 manage.py runserver
