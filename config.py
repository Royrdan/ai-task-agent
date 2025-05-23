import os
import json

# Constants
CONFIG_FILE = 'config.json'
TASKS_DIR = 'tasks'
TASKS_FILE = os.path.join(TASKS_DIR, 'tasks.json')
UPLOAD_FOLDER = os.path.join('static', 'uploads')
WORKSPACES_DIR = 'workspaces'
OUTPUTS_DIR = 'outputs'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure directories exist
for directory in [TASKS_DIR, UPLOAD_FOLDER, WORKSPACES_DIR, OUTPUTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize config if it doesn't exist
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'github_repo': '', 'skip_permissions': False}, f)

# Initialize tasks file if it doesn't exist
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'w') as f:
        json.dump([], f)

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_tasks():
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f)
