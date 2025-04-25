#!/bin/bash

# Define project path
PROJECT_PATH="git_log_viz/myproject/deployment_vm"
VENV_NAME="venv"
GUNICORN_SOCKET="/run/gunicorn.sock"
GITREPORT_CONF="gitreport.conf"

# Step 0: Create project folder
echo "Checking project directory..."
mkdir -p "$PROJECT_PATH"
echo "Directory '$PROJECT_PATH' is ready."

cd "$PROJECT_PATH" || exit 1

# Step 1: Install Python if needed
if ! command -v python3 &> /dev/null; then
    echo "Installing Python3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Step 2: Set up virtual environment
if [ ! -d "$VENV_NAME" ]; then
    python3 -m venv "$VENV_NAME"
    echo "Virtual environment '$VENV_NAME' created."
fi

source "$VENV_NAME/bin/activate"
echo "Virtual environment activated."

# Step 3: Upgrade pip and install requirements
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found!"
fi

# Step 4: Add venv to .gitignore
if ! grep -q "$VENV_NAME/" .gitignore 2>/dev/null; then
    echo "$VENV_NAME/" >> .gitignore
fi

# Step 5: Run Django migrations
if [ -f "manage.py" ]; then
    python manage.py migrate
fi

# Step 6: Install and configure Nginx
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    sudo apt install -y nginx
fi

# Step 7: Link your custom nginx conf
NGINX_CONF_SRC="$(pwd)/$GITREPORT_CONF"
NGINX_CONF_DEST="/etc/nginx/sites-available/gitreport"
NGINX_ENABLED="/etc/nginx/sites-enabled/gitreport"

if [ -f "$NGINX_CONF_SRC" ]; then
    sudo cp "$NGINX_CONF_SRC" "$NGINX_CONF_DEST"
    sudo ln -sf "$NGINX_CONF_DEST" "$NGINX_ENABLED"
    sudo nginx -t && sudo systemctl reload nginx
    echo "Nginx configured with $GITREPORT_CONF"
else
    echo "nginx config $GITREPORT_CONF not found!"
fi

# Step 8: (Optional) SSL setup with Certbot – run manually if needed
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d gitreport.duckdns.org

# Step 9: Run Gunicorn as a background service
read -p "Do you want to start Gunicorn instead of runserver? (y/n): " start_gunicorn
if [ "$start_gunicorn" == "y" ]; then
    echo "Starting Gunicorn using socket $GUNICORN_SOCKET..."
    gunicorn myproject.wsgi:application \
        --bind unix:$GUNICORN_SOCKET \
        --workers 3 \
        --daemon
    echo "Gunicorn started."
fi

echo "Deployment complete"
