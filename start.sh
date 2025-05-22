#!/bin/bash
# Start script for Claude Task Manager
# This script creates a virtual environment if it doesn't exist,
# installs dependencies, and runs the application.

# Exit on error
set -e

echo "Starting Claude Task Manager..."

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Ensure necessary directories exist
echo "Checking directories..."
mkdir -p tasks static/uploads workspaces

# Initialize tasks.json if it doesn't exist
if [ ! -f "tasks/tasks.json" ]; then
    echo "Initializing tasks.json..."
    echo "[]" > tasks/tasks.json
fi

# Initialize config.json if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "Initializing config.json..."
    echo '{"github_repo": ""}' > config.json
fi

# Make run.py executable
chmod +x run.py

# Run the application
echo "Starting the application..."
echo "Open your browser and navigate to http://localhost:9000"
python3 run.py

# Deactivate virtual environment when the application exits
deactivate
