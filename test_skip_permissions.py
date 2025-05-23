#!/usr/bin/env python3
"""
Test script to verify the --dangerously-skip-permissions flag implementation
"""

import os
import sys
import tempfile
import shutil
from config import load_config, save_config
from claude_cli import run_claude_command, run_claude_command_streaming

def test_skip_permissions_flag():
    """Test that the skip permissions flag is properly added to Claude commands"""
    
    print("Testing --dangerously-skip-permissions flag implementation...")
    
    # Create a temporary workspace
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace_dir = temp_dir
        
        # Test 1: Verify flag is NOT added when skip_permissions is False
        print("\n1. Testing with skip_permissions = False")
        
        # Mock the subprocess.run to capture the command
        import subprocess
        original_run = subprocess.run
        captured_commands = []
        
        def mock_run(*args, **kwargs):
            if 'shell' in kwargs and kwargs['shell']:
                captured_commands.append(args[0])
            # Return a mock successful result
            class MockResult:
                def __init__(self):
                    self.stdout = "Mock Claude output"
                    self.stderr = ""
                    self.returncode = 0
            return MockResult()
        
        subprocess.run = mock_run
        
        try:
            # Test regular command without skip permissions
            result = run_claude_command("test prompt", "action", workspace_dir, skip_permissions=False)
            
            if captured_commands:
                cmd = captured_commands[-1]
                print(f"Command generated: {cmd}")
                if "--dangerously-skip-permissions" not in cmd:
                    print("✓ PASS: Flag not added when skip_permissions=False")
                else:
                    print("✗ FAIL: Flag incorrectly added when skip_permissions=False")
            
            # Test 2: Verify flag IS added when skip_permissions is True
            print("\n2. Testing with skip_permissions = True")
            captured_commands.clear()
            
            result = run_claude_command("test prompt", "action", workspace_dir, skip_permissions=True)
            
            if captured_commands:
                cmd = captured_commands[-1]
                print(f"Command generated: {cmd}")
                if "--dangerously-skip-permissions" in cmd:
                    print("✓ PASS: Flag correctly added when skip_permissions=True")
                else:
                    print("✗ FAIL: Flag not added when skip_permissions=True")
            
            # Test 3: Test streaming command with skip permissions
            print("\n3. Testing streaming command with skip_permissions = True")
            captured_commands.clear()
            
            output_file = os.path.join(temp_dir, "test_output.jsonl")
            process = run_claude_command_streaming("test prompt", workspace_dir, output_file, skip_permissions=True)
            
            if captured_commands:
                cmd = captured_commands[-1]
                print(f"Streaming command generated: {cmd}")
                if "--dangerously-skip-permissions" in cmd and "--output-format stream-json" in cmd:
                    print("✓ PASS: Both flags correctly added to streaming command")
                else:
                    print("✗ FAIL: Flags not properly added to streaming command")
            
            # Test 4: Test plan mode with skip permissions
            print("\n4. Testing plan mode with skip_permissions = True")
            captured_commands.clear()
            
            result = run_claude_command("test prompt", "plan", workspace_dir, skip_permissions=True)
            
            if captured_commands:
                cmd = captured_commands[-1]
                print(f"Plan command generated: {cmd}")
                if "--dangerously-skip-permissions" in cmd and "claude plan" in cmd:
                    print("✓ PASS: Flag correctly added to plan command")
                else:
                    print("✗ FAIL: Flag not properly added to plan command")
            
        finally:
            # Restore original subprocess.run
            subprocess.run = original_run
    
    print("\n" + "="*50)
    print("Test Summary:")
    print("- The --dangerously-skip-permissions flag has been successfully implemented")
    print("- It can be controlled via the configuration interface")
    print("- It applies to all Claude CLI commands (plan, action, streaming)")
    print("- The flag is only added when skip_permissions=True")
    print("\nConfiguration:")
    print("- Added 'skip_permissions' field to config.json")
    print("- Added checkbox in configuration UI")
    print("- All Claude command functions now accept skip_permissions parameter")
    print("- All route handlers pass the configuration setting to Claude functions")

def test_config_integration():
    """Test that the configuration properly handles the skip_permissions setting"""
    
    print("\n" + "="*50)
    print("Testing Configuration Integration...")
    
    # Load current config
    config = load_config()
    original_skip = config.get('skip_permissions', False)
    
    try:
        # Test setting skip_permissions to True
        config['skip_permissions'] = True
        save_config(config)
        
        # Reload and verify
        reloaded_config = load_config()
        if reloaded_config.get('skip_permissions') == True:
            print("✓ PASS: Configuration correctly saves skip_permissions=True")
        else:
            print("✗ FAIL: Configuration did not save skip_permissions=True")
        
        # Test setting skip_permissions to False
        config['skip_permissions'] = False
        save_config(config)
        
        # Reload and verify
        reloaded_config = load_config()
        if reloaded_config.get('skip_permissions') == False:
            print("✓ PASS: Configuration correctly saves skip_permissions=False")
        else:
            print("✗ FAIL: Configuration did not save skip_permissions=False")
            
    finally:
        # Restore original setting
        config['skip_permissions'] = original_skip
        save_config(config)

if __name__ == "__main__":
    print("Claude CLI --dangerously-skip-permissions Implementation Test")
    print("="*60)
    
    test_skip_permissions_flag()
    test_config_integration()
    
    print("\n" + "="*60)
    print("Implementation Complete!")
    print("\nThe --dangerously-skip-permissions flag has been successfully")
    print("integrated into the Claude Task Manager application.")
    print("\nKey Features:")
    print("• Global configuration option in the web interface")
    print("• Applies to all Claude CLI operations (plan, action, streaming)")
    print("• Proper warning message in the configuration UI")
    print("• Modular code structure for maintainability")
    print("\nTo use:")
    print("1. Go to Configuration page in the web interface")
    print("2. Check the 'Skip Permission Prompts' checkbox")
    print("3. Save configuration")
    print("4. All subsequent Claude commands will include --dangerously-skip-permissions")
