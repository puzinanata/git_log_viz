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

# Define global variables
VENV_NAME="venv"

# Function to activate virtual environment
activate_venv() {
    if [ ! -d "$VENV_NAME" ]; then
        python3 -m venv "$VENV_NAME"
        if [ ! -d "$VENV_NAME" ]; then
            echo "Error: Virtual environment not created successfully."
            exit 1
        fi
        echo "Virtual environment '$VENV_NAME' created."
    fi

    # Activate the virtual environment
    source "$VENV_NAME/bin/activate"
    echo "Virtual environment activated."
}

# Step 0: Install required packages
set +e
REQUIRED_PACKAGES=(
    git
    nginx
    python3
    python3-pip
    python3-venv
)

sudo apt update

for package in "${REQUIRED_PACKAGES[@]}"; do
    echo "Installing $package..."
    if sudo apt install -y "$package"; then
        echo "$package installed successfully"
    else
        echo "Failed to install $package"
    fi
done

echo "All required packages installed!"
set -e


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
activate_venv

# Step 3:
echo "Creating directory for Git repositories: /var/lib/git_repos"
sudo mkdir -p "/var/lib/git_repos"
sudo chown "$USER":"$USER" "/var/lib/git_repos"
sudo chmod 755 "/var/lib/git_repos"

# Step 4: Install requirements
if [ -f "deployment_vm/requirements.txt" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install -r deployment_vm/requirements.txt
    echo "Dependencies installed successfully."
else
    echo "requirements.txt not found in deployment_vm/!"
fi

# Step 5: Add venv to .gitignore
if ! grep -q "$VENV_NAME/" myproject/.gitignore 2>/dev/null; then
    echo "$VENV_NAME/" >> myproject/.gitignore
fi

# Step 6: Run Django migrations
echo "Navigating to the project directory..."
cd myproject/

if [ -f "manage.py" ]; then
    echo "Running migrations and collecting static files..."
    python3 manage.py migrate
    python3 manage.py collectstatic --noinput
    echo "Migrations and static files collection completed."
else
    echo "manage.py not found, ensure you're in the correct project directory."
fi

# Step 7: Run nginx
GITREPORT_CONF="../deployment_vm/testgitreport.conf"
NGINX_CONF_SRC="$(realpath "$GITREPORT_CONF")"
NGINX_CONF_DEST="/etc/nginx/sites-available/testgitreport"
NGINX_ENABLED="/etc/nginx/sites-enabled/testgitreport"

if [ -f "$NGINX_CONF_SRC" ]; then
    sudo cp "$NGINX_CONF_SRC" "$NGINX_CONF_DEST"
    sudo ln -sf "$NGINX_CONF_DEST" "$NGINX_ENABLED"
    sudo nginx -t && sudo systemctl reload nginx
    echo "Nginx configured with $GITREPORT_CONF"
else
    echo "nginx config $GITREPORT_CONF not found!"
fi

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx

## Now install certbot and request HTTPS certificate
#sudo apt install -y certbot python3-certbot-nginx
#
## Launch certbot to configure SSL automatically
#sudo certbot --nginx -d testgitreport.duckdns.org

# Step 9: Kill previous Gunicorn and runserver processes if they exist
#echo "Stopping any previous Gunicorn or Django runserver processes..."
#pkill -f "gunicorn myproject.wsgi"
#pkill -f "manage.py runserver"
#sleep 2
# Step 10: Choose to start Gunicorn or runserver
#GUNICORN_SOCKET="/home/lechatdoux1987/git_log_viz/myproject/gunicorn.sock"
#
#read -p "Do you want to start Gunicorn instead of runserver? (y/n): " start_gunicorn
#if [ "$start_gunicorn" == "y" ]; then
#    echo "Starting Gunicorn using socket $GUNICORN_SOCKET..."
#    gunicorn myproject.wsgi:application \
#        --bind unix:$GUNICORN_SOCKET \
#        --workers 3 \
#        --daemon
#    echo "Gunicorn started."
#else
echo "Starting Django runserver in daemon mode..."
nohup python3 manage.py runserver &> /dev/null &
echo "Runserver started."
#fi

echo "Deployment complete"
