import subprocess

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
