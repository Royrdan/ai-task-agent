import os
import json
import shutil
import subprocess
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from werkzeug.utils import secure_filename

# Import our modules
from config import (
    CONFIG_FILE, UPLOAD_FOLDER, WORKSPACES_DIR, 
    load_config, save_config, load_tasks, save_tasks
)
from claude_cli import (
    run_claude_command, run_claude_command_streaming, 
    get_output_file_path, read_streaming_output
)
from git_utils import get_git_diff, create_git_branch_and_push
from utils import allowed_file, get_priority_order, process_csv_file

app = Flask(__name__)
app.secret_key = os.urandom(24)

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
        
        # Handle skip permissions setting
        config['skip_permissions'] = 'skip_permissions' in request.form
        
        save_config(config)
        flash('Configuration updated successfully', 'success')
        return redirect(url_for('index'))
    
    config = load_config()
    return render_template('config.html', config=config)

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
        
        # Load configuration and existing tasks
        config = load_config()
        tasks = load_tasks()
        existing_tickets = {task['ticket'] for task in tasks}
        
        try:
            new_tasks, new_tasks_count, skipped_tasks_count, error_rows = process_csv_file(
                filepath, config, existing_tickets
            )
            
            # Add new tasks to existing tasks
            tasks.extend(new_tasks)
            save_tasks(tasks)
            
            # Log any errors
            if error_rows:
                print(f"Errors in CSV rows: {error_rows}")
            
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
            
        except Exception as e:
            flash(f'Error processing CSV: {str(e)}', 'error')
            print(f"CSV processing error: {str(e)}")
        finally:
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

@app.route('/task/<task_id>/streaming', methods=['GET'])
def task_detail_streaming(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('task_detail_streaming.html', task=task)

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
    """Start a task with live streaming output"""
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
    
    # Get output file path
    output_file_path = get_output_file_path(task_id)
    
    # Start Claude streaming process with skip permissions setting
    skip_permissions = config.get('skip_permissions', False)
    process = run_claude_command_streaming(task['prompt'], workspace_dir, output_file_path, skip_permissions)
    
    if process is None:
        flash('Failed to start Claude process', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Update task status
    tasks[task_index]['status'] = 'streaming'
    tasks[task_index]['workspace_dir'] = workspace_dir
    save_tasks(tasks)
    
    flash('Task started successfully', 'success')
    return redirect(url_for('task_detail', task_id=task_id))

@app.route('/task/<task_id>/action', methods=['POST'])
def action_task(task_id):
    config = load_config()
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        flash('Task not found', 'error')
        return redirect(url_for('index'))
    
    task = tasks[task_index]
    
    if task['status'] != 'started':
        flash('Task must be started before it can be actioned', 'error')
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Run Claude in action mode with skip permissions setting
    skip_permissions = config.get('skip_permissions', False)
    claude_output = run_claude_command(task['prompt'], 'action', task['workspace_dir'], skip_permissions)
    
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
    config = load_config()
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
    
    # Run Claude with the follow-up prompt with skip permissions setting
    skip_permissions = config.get('skip_permissions', False)
    claude_output = run_claude_command(followup_prompt, 'action', task['workspace_dir'], skip_permissions)
    
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

@app.route('/task/<task_id>/start_streaming', methods=['POST'])
def start_task_streaming(task_id):
    """Start a task with live streaming output"""
    config = load_config()
    if not config['github_repo']:
        return jsonify({'error': 'GitHub repository not configured'}), 400
    
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasks[task_index]
    
    if not task['prompt']:
        return jsonify({'error': 'Please add a prompt before starting the task'}), 400
    
    # Create workspace directory
    workspace_dir = os.path.join(WORKSPACES_DIR, task_id)
    if os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir)
    os.makedirs(workspace_dir)
    
    # Clone repository
    try:
        subprocess.run(f'git clone {config["github_repo"]} .', shell=True, check=True, cwd=workspace_dir)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error cloning repository: {e}'}), 500
    
    # Get output file path
    output_file_path = get_output_file_path(task_id)
    
    # Start Claude streaming process with skip permissions setting
    skip_permissions = config.get('skip_permissions', False)
    process = run_claude_command_streaming(task['prompt'], workspace_dir, output_file_path, skip_permissions)
    
    if process is None:
        return jsonify({'error': 'Failed to start Claude process'}), 500
    
    # Update task status
    tasks[task_index]['status'] = 'streaming'
    tasks[task_index]['workspace_dir'] = workspace_dir
    save_tasks(tasks)
    
    return jsonify({'success': True, 'message': 'Task started with streaming output'})

@app.route('/task/<task_id>/action_streaming', methods=['POST'])
def action_task_streaming(task_id):
    """Run action mode with live streaming output"""
    config = load_config()
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasks[task_index]
    
    if task['status'] not in ['started', 'streaming']:
        return jsonify({'error': 'Task must be started before it can be actioned'}), 400
    
    # Get output file path
    output_file_path = get_output_file_path(task_id)
    
    # Start Claude streaming process for action mode with skip permissions setting
    skip_permissions = config.get('skip_permissions', False)
    process = run_claude_command_streaming(task['prompt'], task['workspace_dir'], output_file_path, skip_permissions)
    
    if process is None:
        return jsonify({'error': 'Failed to start Claude process'}), 500
    
    # Update task status
    tasks[task_index]['status'] = 'actioning'
    save_tasks(tasks)
    
    return jsonify({'success': True, 'message': 'Action started with streaming output'})

@app.route('/task/<task_id>/stream')
def stream_task_output(task_id):
    """Stream live output from Claude for a specific task"""
    def generate():
        output_file_path = get_output_file_path(task_id)
        
        # Wait for file to be created
        timeout = 30  # 30 seconds timeout
        start_time = time.time()
        while not os.path.exists(output_file_path) and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if not os.path.exists(output_file_path):
            yield f"data: {json.dumps({'error': 'Output file not found'})}\n\n"
            return
        
        # Stream the output
        last_position = 0
        with open(output_file_path, 'r') as f:
            f.seek(0)  # Start from beginning of file
            while True:
                f.seek(last_position)
                lines = f.readlines()
                
                if lines:
                    for line in lines:
                        if line.strip():
                            try:
                                # Parse JSON line and send as SSE
                                data = json.loads(line.strip())
                                yield f"data: {json.dumps(data)}\n\n"
                            except json.JSONDecodeError:
                                # If not JSON, send as plain text
                                yield f"data: {json.dumps({'text': line})}\n\n"
                    
                    last_position = f.tell()
                else:
                    # No new data, wait a bit
                    time.sleep(0.1)
                    
                    # Check if process is still running
                    tasks = load_tasks()
                    task = next((t for t in tasks if t['id'] == task_id), None)
                    if task and task['status'] not in ['streaming', 'actioning']:
                        break
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/task/<task_id>/complete_streaming', methods=['POST'])
def complete_streaming_task(task_id):
    """Mark a streaming task as completed and get final output"""
    tasks = load_tasks()
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasks[task_index]
    output_file_path = get_output_file_path(task_id)
    
    # Read final output from file
    final_output = ""
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    
                    # Handle Claude CLI message format
                    if data.get('type') == 'message' and 'content' in data:
                        # Extract text from content array
                        for content_item in data['content']:
                            if content_item.get('type') == 'text' and 'text' in content_item:
                                final_output += content_item['text'] + '\n'
                    
                    # Handle streaming delta format (if used)
                    elif data.get('type') == 'content_block_delta' and 'delta' in data:
                        if 'text' in data['delta']:
                            final_output += data['delta']['text']
                    
                    # Handle system messages with result
                    elif 'result' in data:
                        final_output += data['result'] + '\n'
                    
                    # Fallback for other formats
                    elif 'content' in data and isinstance(data['content'], str):
                        final_output += data['content']
                    elif 'text' in data:
                        final_output += data['text']
                        
                except json.JSONDecodeError:
                    continue
    
    # Get git diff
    git_diff = get_git_diff(task['workspace_dir'])
    
    # Update task
    tasks[task_index]['status'] = 'actioned'
    tasks[task_index]['claude_output'] = final_output
    tasks[task_index]['git_diff'] = git_diff
    save_tasks(tasks)
    
    return jsonify({'success': True, 'output': final_output, 'git_diff': git_diff})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
