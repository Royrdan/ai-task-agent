#!/usr/bin/env python3
"""
Test script to verify Claude CLI integration for the task manager.
This script tests the Claude CLI commands used by the application.
"""

import subprocess
import os
import sys
import tempfile
import json
import time

def test_claude_cli_availability():
    """Test if Claude CLI is available and working"""
    print("Testing Claude CLI availability...")
    try:
        result = subprocess.run(['claude', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Claude CLI is available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Claude CLI error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Claude CLI not found in PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Claude CLI command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Claude CLI: {e}")
        return False

def test_claude_print_mode():
    """Test Claude CLI print mode"""
    print("\nTesting Claude CLI print mode...")
    try:
        test_prompt = "Hello, this is a test prompt. Please respond with 'Test successful'."
        cmd = f'claude -p "{test_prompt}"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, 
                              text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Claude print mode works")
            print(f"Response: {result.stdout[:100]}...")
            return True
        else:
            print(f"❌ Claude print mode failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Claude print mode timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Claude print mode: {e}")
        return False

def test_claude_streaming_mode():
    """Test Claude CLI streaming mode with JSON output"""
    print("\nTesting Claude CLI streaming mode...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, 'test_output.jsonl')
        
        try:
            test_prompt = "Please count from 1 to 3, one number per response."
            cmd = f'claude -p "{test_prompt}" --output-format stream-json > "{output_file}"'
            
            # Start the process
            process = subprocess.Popen(cmd, shell=True, cwd=temp_dir,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a bit for output to be generated
            time.sleep(5)
            
            # Check if output file exists and has content
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    content = f.read()
                    
                if content.strip():
                    print("✅ Claude streaming mode works")
                    print(f"Output file created with {len(content)} characters")
                    
                    # Try to parse some JSON lines
                    lines = content.strip().split('\n')
                    valid_json_count = 0
                    for line in lines[:3]:  # Check first 3 lines
                        try:
                            json.loads(line)
                            valid_json_count += 1
                        except json.JSONDecodeError:
                            continue
                    
                    if valid_json_count > 0:
                        print(f"✅ Found {valid_json_count} valid JSON lines")
                    else:
                        print("⚠️  No valid JSON lines found in output")
                    
                    return True
                else:
                    print("❌ Output file is empty")
                    return False
            else:
                print("❌ Output file was not created")
                return False
                
        except Exception as e:
            print(f"❌ Error testing Claude streaming mode: {e}")
            return False
        finally:
            # Clean up process
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                pass

def test_git_availability():
    """Test if Git is available"""
    print("\nTesting Git availability...")
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Git is available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Git error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Git not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error testing Git: {e}")
        return False

def test_python_dependencies():
    """Test if required Python packages are available"""
    print("\nTesting Python dependencies...")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print(f"✅ Running in virtual environment: {sys.prefix}")
    else:
        print(f"⚠️  Not running in virtual environment. Current Python: {sys.executable}")
        print("   Consider running: source venv/bin/activate (or activate your virtual environment)")
    
    required_packages = ['flask', 'werkzeug']
    
    all_available = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is not available")
            if not in_venv:
                print(f"   Try: pip install {package} (after activating virtual environment)")
            else:
                print(f"   Try: pip install {package}")
            all_available = False
    
    return all_available

def main():
    """Run all tests"""
    print("Claude Task Manager - CLI Integration Test")
    print("=" * 50)
    
    tests = [
        ("Claude CLI Availability", test_claude_cli_availability),
        ("Claude Print Mode", test_claude_print_mode),
        ("Claude Streaming Mode", test_claude_streaming_mode),
        ("Git Availability", test_git_availability),
        ("Python Dependencies", test_python_dependencies),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The system is ready for Claude Task Manager.")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the requirements.")
        print("\nTroubleshooting tips:")
        print("- Ensure Claude CLI is installed and authenticated")
        print("- Check that all required Python packages are installed")
        print("- Verify Git is installed and configured")

if __name__ == "__main__":
    main()
