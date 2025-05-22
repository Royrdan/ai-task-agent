import os
import json
import csv
import uuid
import subprocess
import shutil
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Constants
CONFIG_FILE = 'config.json'
TASKS_DIR = 'tasks'
TASKS_FILE = os.path.join(TASKS_DIR, 'tasks.json')
UPLOAD_FOLDER = os.path.join('static', 'uploads')
WORKSPACES_DIR = 'workspaces'
ALLOWED_EXTENSIONS = {'csv'}

# Ensure directories exist
for directory in [TASKS_DIR, UPLOAD_FOLDER, WORKSPACES_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize config if it doesn't exist
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'github_repo': ''}, f)

# Initialize tasks file if it doesn't exist
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'w') as f:
        json.dump([], f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def run_claude_command(prompt, mode, workspace_dir):
    """
    Run Claude CLI command and return the output.
    
    This function assumes Claude is available via command line on a Linux system.
    You may need to modify the commands below to match your specific Claude CLI setup.
    
    Possible modifications:
    1. Change the command format if your Claude CLI uses different syntax
    2. Add authentication parameters if required
    3. Adjust output handling based on your Claude CLI's response format
    """
    # Escape quotes in the prompt to prevent shell injection
    escaped_prompt = prompt.replace('"', '\\"')
    
    if mode == "plan":
        # Command for running Claude in plan mode
        cmd = f'echo "{escaped_prompt}" | claude plan'
    else:  # action mode
        # Command for running Claude in action mode
        cmd = f'echo "{escaped_prompt}" | claude act'
    
    try:
        # Run the command in the workspace directory
        result = subprocess.run(cmd, shell=True, check=True, cwd=workspace_dir,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running Claude: {e.stderr}"

def get_git_diff(workspace_dir):
    """Get git diff for the workspace"""
    try:
        result = subprocess.run('git diff', shell=True, check=True, cwd=workspace_dir,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting git diff: {e.stderr}"

def create_git_branch_and_push(workspace_dir, ticket, task_description):
    """Create a git branch, commit changes, and push"""
    # Create a simplified branch name from the ticket and task
    branch_name = f"{ticket}-{'-'.join(task_description.lower().split()[:3])}"
    commit_message = f"dev: {task_description}"
    
    try:
        # Create and checkout new branch
        subprocess.run(f'git checkout -b {branch_name}', shell=True, check=True, cwd=workspace_dir)
        
        # Add all changes
        subprocess.run('git add .', shell=True, check=True, cwd=workspace_dir)
        
        # Commit changes
        subprocess.run(f'git commit -m "{commit_message}"', shell=True, check=True, cwd=workspace_dir)
        
        # Push branch
        subprocess.run(f'git push -u origin {branch_name}', shell=True, check=True, cwd=workspace_dir)
        
        return True, f"Successfully pushed to branch {branch_name}"
    except subprocess.CalledProcessError as e:
        return False, f"Error in git operations: {e.stderr}"

def get_priority_order(priority):
    """Get a numeric value for sorting priorities"""
    priority = priority.lower()
    if priority == 'high':
        return 0
    elif priority == 'medium':
        return 1
    elif priority == 'low':
        return 2
    else:
        return 3  # For any other priority values

@app.route('/')
def index():
    tasks = load_tasks()
    # Sort tasks by priority (High, Medium, Low)
    tasks = sorted(tasks, key=lambda x: get_priority_order(x.get('priority', 'Medium')))
    config = load_config()
    return render_template('index.html', tasks=tasks, config=config)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        config = load_config()
        config['github_repo'] = request.form['github_repo']
        
        # Handle assignees
        assignees = request.form.getlist('assignees[]')
        # Filter out empty assignee names
        config['assignees'] = [assignee.strip() for assignee in assignees if assignee.strip()]
        
        save_config(config)
        flash('Configuration updated successfully', 'success')
        return redirect(url_for('index'))
    
    config = load_config()
    return render_template('config.html', config=config)

def get_case_insensitive_column(row, column_name):
    """Get a column value regardless of case"""
    # First try direct access (case sensitive)
    if column_name in row:
        return row[column_name]
    
    # Then try case-insensitive match
    for key in row.keys():
        if key.lower() == column_name.lower():
            return row[key]
    
    # If still not found, try with common variations
    variations = [
        column_name.lower(),
        column_name.upper(),
        column_name.capitalize(),
        column_name.title()
    ]
    
    for var in variations:
        if var in row:
            return row[var]
    
    return None

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'csv_file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['csv_file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Load configuration to get assignees
        config = load_config()
        assignees = config.get('assignees', [])
        
        # Process CSV file
        tasks = load_tasks()
        existing_tickets = {task['ticket'] for task in tasks}
        new_tasks_count = 0
        skipped_tasks_count = 0
        error_rows = []
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
                # Try to read the CSV file
                reader = csv.DictReader(csvfile)
                
                # Process each row in the CSV
                for row in reader:
                    # Get values regardless of case
                    ticket = get_case_insensitive_column(row, 'ticket')
                    task_name = get_case_insensitive_column(row, 'task')
                    link = get_case_insensitive_column(row, 'link')
                    priority = get_case_insensitive_column(row, 'priority')
                    assignee = get_case_insensitive_column(row, 'assign')
                    
                    # Set default priority if not provided
                    if not priority:
                        priority = "Medium"
                    
                    # Check if we have the required fields
                    if not ticket:
                        error_rows.append(f"Missing ticket in row: {row}")
                        continue
                        
                    if not task_name:
                        error_rows.append(f"Missing task name in row: {row}")
                        continue
                    
                    # Skip tasks that don't have an assignee in the configuration
                    if assignees and (not assignee or assignee.strip() not in assignees):
                        print(f"Skipping task {ticket} - assignee '{assignee}' not in configured assignees: {assignees}")
                        skipped_tasks_count += 1
                        continue
                    
                    # Process the row
                    ticket = ticket.strip()
                    if ticket not in existing_tickets:
                        task_id = str(uuid.uuid4())
                        tasks.append({
                            'id': task_id,
                            'ticket': ticket,
                            'task': task_name.strip(),
                            'link': link.strip() if link else '',
                            'priority': priority.strip(),
                            'assignee': assignee.strip() if assignee else '',
                            'prompt': '',
                            'status': 'new',  # new, started, actioned, completed
                            'created_at': datetime.now().isoformat(),
                            'claude_output': '',
                            'workspace_dir': os.path.join(WORKSPACES_DIR, task_id)
                        })
                        existing_tickets.add(ticket)
                        new_tasks_count += 1
                    else:
                        print(f"Skipping duplicate ticket: {ticket}")
        except Exception as e:
            flash(f'Error processing CSV: {str(e)}', 'error')
            print(f"CSV processing error: {str(e)}")
            # Clean up the uploaded file
            os.remove(filepath)
            return redirect(url_for('index'))
        
        # Log any errors
        if error_rows:
            print(f"Errors in CSV rows: {error_rows}")
        
        save_tasks(tasks)
        
        # Show appropriate message based on results
        if new_tasks_count > 0:
            if skipped_tasks_count > 0:
                flash(f'Added {new_tasks_count} new tasks from CSV. Skipped {skipped_tasks_count} tasks due to assignee filtering.', 'success')
            else:
                flash(f'Added {new_tasks_count} new tasks from CSV', 'success')
        else:
            if skipped_tasks_count > 0:
                flash(f'No tasks added. Skipped {skipped_tasks_count} tasks due to assignee filtering.', 'warning')
            else:
                flash('No new tasks found in CSV', 'warning')
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a CSV file.', 'error')
    return redirect(url_for('index'))

@app.route('/task/<task_id>', methods=['GET'])
def task_detail(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('task_detail.html', task=task)

@app.route('/task/<task_id>/update_prompt', methods=['POST'])
def update_prompt(task_id):
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    tasks[task_index]['prompt'] = request.form['prompt']
    save_tasks(tasks)
    flash('Prompt updated successfully', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/task/<task_id>/start', methods=['POST'])
def start_task(task_id):
    config = load_config()
    if not config['github_repo']:
        flash('GitHub repository not configured', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    task = tasks[task_index]
    
    if not task['prompt']:
        flash('Please add a prompt before starting the task', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Create workspace directory
    workspace_dir = os.path.join(WORKSPACES_DIR, task_id)
    if os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir)
    os.makedirs(workspace_dir)
    
    # Clone repository
    try:
        subprocess.run(f'git clone {config["github_repo"]} .', shell=True, check=True, cwd=workspace_dir)
    except subprocess.CalledProcessError as e:
        flash(f'Error cloning repository: {e}', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Run Claude in plan mode
    claude_output = run_claude_command(task['prompt'], 'plan', workspace_dir)
    
    # Update task
    tasks[task_index]['status'] = 'started'
    tasks[task_index]['claude_output'] = claude_output
    tasks[task_index]['workspace_dir'] = workspace_dir
    save_tasks(tasks)
    
    flash('Task started successfully', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/task/<task_id>/action', methods=['POST'])
def action_task(task_id):
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    task = tasks[task_index]
    
    if task['status'] != 'started':
        flash('Task must be started before it can be actioned', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Run Claude in action mode
    claude_output = run_claude_command(task['prompt'], 'action', task['workspace_dir'])
    
    # Get git diff
    git_diff = get_git_diff(task['workspace_dir'])
    
    # Update task
    tasks[task_index]['status'] = 'actioned'
    tasks[task_index]['claude_output'] += "\n\n--- ACTION OUTPUT ---\n\n" + claude_output
    tasks[task_index]['git_diff'] = git_diff
    save_tasks(tasks)
    
    flash('Task actioned successfully', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/task/<task_id>/followup', methods=['POST'])
def followup_prompt(task_id):
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    task = tasks[task_index]
    
    if task['status'] != 'actioned':
        flash('Task must be actioned before adding a follow-up prompt', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    followup_prompt = request.form['followup_prompt']
    
    # Run Claude with the follow-up prompt
    claude_output = run_claude_command(followup_prompt, 'action', task['workspace_dir'])
    
    # Get updated git diff
    git_diff = get_git_diff(task['workspace_dir'])
    
    # Update task
    tasks[task_index]['claude_output'] += "\n\n--- FOLLOW-UP OUTPUT ---\n\n" + claude_output
    tasks[task_index]['git_diff'] = git_diff
    save_tasks(tasks)
    
    flash('Follow-up prompt processed successfully', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/task/<task_id>/push', methods=['POST'])
def push_changes(task_id):
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    task = tasks[task_index]
    
    if task['status'] != 'actioned':
        flash('Task must be actioned before pushing changes', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Create branch, commit and push changes
    success, message = create_git_branch_and_push(
        task['workspace_dir'], 
        task['ticket'], 
        task['task']
    )
    
    if success:
        # Update task status
        tasks[task_index]['status'] = 'completed'
        save_tasks(tasks)
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/task/<task_id>/delete', methods=['POST'])
def delete_task(task_id):
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    # Remove workspace directory if it exists
    workspace_dir = tasks[task_index].get('workspace_dir')
    if workspace_dir and os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir)
    
    # Remove task from list
    del tasks[task_index]
    save_tasks(tasks)
    
    flash('Task deleted successfully', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
