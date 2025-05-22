#!/usr/bin/env python3
"""
Update Claude Command Script

This script updates the Claude command in app.py to match your specific Claude CLI setup.
It modifies the run_claude_command function to use the command format you specify.
"""
import re
import sys
import argparse

def update_claude_command(plan_command, action_command):
    """Update the Claude command in app.py"""
    # Read the app.py file
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Escape special characters for regex
    plan_command_escaped = re.escape(plan_command).replace('\\"', '"')
    action_command_escaped = re.escape(action_command).replace('\\"', '"')
    
    # Replace the command patterns
    # First, find the run_claude_command function
    pattern = r'(def run_claude_command.*?if mode == "plan":\s+)cmd = f\'.*?\'(\s+else:.*?cmd = f\').*?(\'.*?return result\.stdout)'
    replacement = r'\1cmd = f\'' + plan_command_escaped + r'\'\2' + action_command_escaped + r'\3'
    
    # Use re.DOTALL to make . match newlines
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        print("Could not find the command patterns to replace. Make sure app.py has not been modified.")
        return False
    
    # Write the updated content back to app.py
    with open('app.py', 'w') as f:
        f.write(new_content)
    
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Claude command in app.py')
    parser.add_argument('--plan', required=True, 
                        help='Command format for plan mode. Use {prompt} as a placeholder for the prompt.')
    parser.add_argument('--action', required=True, 
                        help='Command format for action mode. Use {prompt} as a placeholder for the prompt.')
    
    args = parser.parse_args()
    
    # Replace {prompt} with the actual prompt variable used in the code
    plan_command = args.plan.replace('{prompt}', '{escaped_prompt}')
    action_command = args.action.replace('{prompt}', '{escaped_prompt}')
    
    if update_claude_command(plan_command, action_command):
        print("Successfully updated Claude commands in app.py")
        print(f"Plan mode command: {args.plan}")
        print(f"Action mode command: {args.action}")
    else:
        print("Failed to update Claude commands")
        sys.exit(1)
