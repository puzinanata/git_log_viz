#!/bin/bash

# Define project path
PROJECT_PATH="git_log_viz/myproject/deployment_vm"

# Step 0: Create project folder structure if it doesn't exist
echo "Checking project directory..."
mkdir -p "$PROJECT_PATH"
echo "Directory '$PROJECT_PATH' is ready."

cd "$PROJECT_PATH" || exit 1

# Name of my virtual environment folder
VENV_NAME="venv"

echo "Setting up Python virtual environment..."

# Step 1: Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Installing Python3 on Ubuntu/Debian..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
    echo "Python3 installed successfully!"
fi

# Step 2: Create virtual environment
python3 -m venv $VENV_NAME
echo "Virtual environment '$VENV_NAME' created."

# Step 3: Activate the virtual environment
source $VENV_NAME/bin/activate
echo "Virtual environment activated."

# Step 4: Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Step 5: Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    echo "All requirements installed."
else
    echo "requirements.txt not found!"
fi

# Step 6: Add venv to .gitignore
if ! grep -q "$VENV_NAME/" .gitignore 2>/dev/null; then
    echo "$VENV_NAME/" >> .gitignore
    echo "Added '$VENV_NAME/' to .gitignore."
fi

# Step 7: Apply migrations
if [ -f "manage.py" ]; then
    echo "Running Django migrations..."
    python3 manage.py migrate
fi

# Step 8: Run the development server in background
read -p "Do you want to start the Django development server now? (y/n): " runserver
if [ "$runserver" == "y" ]; then
    echo "Starting Django server in background (logs: runserver.log)..."
    nohup python manage.py runserver > runserver.log 2>&1 &
    echo "Server started."
fi

echo "Setup complete!"
