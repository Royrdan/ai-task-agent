@echo off
REM Start script for Claude Task Manager on Windows
REM This script creates a virtual environment if it doesn't exist,
REM installs dependencies, and runs the application.

echo Starting Claude Task Manager...

REM Check if Python 3 is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is required but not found.
    echo Please install Python and try again.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if requirements.txt exists
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Ensure necessary directories exist
echo Checking directories...
if not exist tasks mkdir tasks
if not exist static\uploads mkdir static\uploads
if not exist workspaces mkdir workspaces

REM Initialize tasks.json if it doesn't exist
if not exist tasks\tasks.json (
    echo Initializing tasks.json...
    echo [] > tasks\tasks.json
)

REM Initialize config.json if it doesn't exist
if not exist config.json (
    echo Initializing config.json...
    echo {"github_repo": ""} > config.json
)

REM Run the application
echo Starting the application...
echo Open your browser and navigate to http://localhost:9000
python run.py

REM Deactivate virtual environment when the application exits
deactivate
