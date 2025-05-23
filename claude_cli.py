import os
import json
import subprocess
import threading
import time

def run_claude_command(prompt, mode, workspace_dir, skip_permissions=False):
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
    
    # Add skip permissions flag if requested
    skip_flag = " --dangerously-skip-permissions" if skip_permissions else ""
    
    if mode == "plan":
        # Command for running Claude in plan mode
        cmd = f'echo "{escaped_prompt}" | claude plan{skip_flag}'
    else:  # action mode
        # Command for running Claude in action mode
        cmd = f'echo "{escaped_prompt}" | claude act{skip_flag}'
    
    try:
        # Run the command in the workspace directory
        result = subprocess.run(cmd, shell=True, check=True, cwd=workspace_dir,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running Claude: {e.stderr}"

def run_claude_command_streaming(prompt, workspace_dir, output_file_path, skip_permissions=False):
    """
    Run Claude CLI command in print mode with streaming output to a file.
    Uses the claude -p command with --output-format stream-json for live updates.
    """
    # Escape quotes in the prompt to prevent shell injection
    escaped_prompt = prompt.replace('"', '\\"')
    
    # Add skip permissions flag if requested
    skip_flag = " --dangerously-skip-permissions" if skip_permissions else ""
    
    # Use claude -p with streaming JSON output - Linux compatible
    cmd = f'claude -p "{escaped_prompt}" --output-format stream-json{skip_flag}'
    
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        print(f"DEBUG: Starting Claude command: {cmd}")
        print(f"DEBUG: Output file path: {output_file_path}")
        print(f"DEBUG: Working directory: {workspace_dir}")
        
        # Open the output file for writing and run the command with stdout redirected to it
        output_file = open(output_file_path, 'w')
        process = subprocess.Popen(cmd, shell=True, cwd=workspace_dir,
                                 stdout=output_file, stderr=subprocess.PIPE, text=True)
        
        # Store the file handle with the process so we can close it later
        process.output_file = output_file
        
        print(f"DEBUG: Claude process started with PID: {process.pid}")
        
        # Start a thread to monitor the process and close the file when done
        threading.Thread(target=monitor_process, args=(process, output_file), daemon=True).start()
        
        return process
    except Exception as e:
        print(f"DEBUG: Error in run_claude_command_streaming: {e}")
        return None

def monitor_process(process, output_file):
    """Monitor a process and close the output file when it completes"""
    try:
        # Wait for the process to complete
        process.wait()
        print(f"DEBUG: Process {process.pid} completed with return code {process.returncode}")
        
        # Close the output file
        if output_file and not output_file.closed:
            output_file.close()
            print(f"DEBUG: Output file closed for process {process.pid}")
            
        # Check for any stderr output
        if process.stderr:
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"DEBUG: Process stderr: {stderr_output}")
                
    except Exception as e:
        print(f"DEBUG: Error monitoring process: {e}")
        if output_file and not output_file.closed:
            output_file.close()

def get_output_file_path(task_id):
    """Get the path for the Claude output file for a specific task"""
    # Store output files in a separate directory to avoid committing them with code changes
    output_dir = os.path.join('outputs', task_id)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, 'claude_output.jsonl')

def read_streaming_output(output_file_path):
    """Generator function to read streaming output from Claude"""
    if not os.path.exists(output_file_path):
        return
    
    with open(output_file_path, 'r') as f:
        # Start from the beginning of the file
        f.seek(0)
        while True:
            line = f.readline()
            if line:
                try:
                    # Parse JSON line
                    data = json.loads(line.strip())
                    yield data
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue
            else:
                # No new data, wait a bit
                time.sleep(0.1)
