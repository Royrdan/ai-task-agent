#!/bin/bash
# Setup script for Claude Task Manager

# Exit on error
set -e

echo "Setting up Claude Task Manager..."

# Check if Python 3.8+ is installed
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version | cut -d' ' -f2)
    echo "Found Python $python_version"
    
    # Check Python version
    major=$(echo $python_version | cut -d. -f1)
    minor=$(echo $python_version | cut -d. -f2)
    
    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 8 ]); then
        echo "Error: Python 3.8 or higher is required."
        echo "Your version: $python_version"
        exit 1
    fi
else
    echo "Error: Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Git is installed
if command -v git &>/dev/null; then
    git_version=$(git --version | cut -d' ' -f3)
    echo "Found Git $git_version"
else
    echo "Error: Git not found. Please install Git."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make run.py executable
echo "Making run.py executable..."
chmod +x run.py

# Create necessary directories
echo "Creating necessary directories..."
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

echo "Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment (if not already activated):"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the application:"
echo "   ./run.py"
echo ""
echo "3. Open your browser and navigate to http://localhost:9000"
