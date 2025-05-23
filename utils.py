import csv
import uuid
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, WORKSPACES_DIR

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def process_csv_file(filepath, config, existing_tickets):
    """Process CSV file and return new tasks"""
    assignees = config.get('assignees', [])
    new_tasks = []
    new_tasks_count = 0
    skipped_tasks_count = 0
    error_rows = []
    
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # Get values regardless of case
                ticket = get_case_insensitive_column(row, 'ticket')
                task_name = get_case_insensitive_column(row, 'task')
                link = get_case_insensitive_column(row, 'link')
                priority = get_case_insensitive_column(row, 'priority')
                assignee = get_case_insensitive_column(row, 'assign')
                state = get_case_insensitive_column(row, 'state')
                
                # Set default values if not provided
                if not priority:
                    priority = "Medium"
                
                if not state:
                    state = "Ready"
                
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
                    new_tasks.append({
                        'id': task_id,
                        'ticket': ticket,
                        'task': task_name.strip(),
                        'link': link.strip() if link else '',
                        'priority': priority.strip(),
                        'assignee': assignee.strip() if assignee else '',
                        'state': state.strip() if state else 'Ready',
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
        raise Exception(f"CSV processing error: {str(e)}")
    
    return new_tasks, new_tasks_count, skipped_tasks_count, error_rows
