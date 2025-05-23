# Claude Task Manager with Live Streaming

A Flask-based task management system that integrates with Claude CLI to provide live streaming output for AI-powered task execution.

## Features

### Core Features
- **Task Management**: Upload tasks via CSV, manage priorities, assignees, and states
- **Claude CLI Integration**: Execute tasks using Claude's command-line interface
- **Git Integration**: Automatic repository cloning, branching, and pushing
- **Live Streaming**: Real-time output from Claude CLI using Server-Sent Events (SSE)

### Live Streaming Features
- **Real-time Output**: Watch Claude's responses appear in real-time as they're generated
- **Auto-scroll**: Automatically scroll to follow the latest output
- **Streaming Controls**: Start, action, and complete tasks with live feedback
- **Error Handling**: Graceful handling of connection issues with auto-reconnect

## Claude CLI Integration

This application uses the Claude CLI's print mode with streaming JSON output:

```bash
claude -p "your prompt here" --output-format stream-json
```

### Supported Claude CLI Commands

The application supports different modes based on the Claude CLI documentation:

1. **Plan Mode**: `claude plan` (for initial task planning)
2. **Action Mode**: `claude act` (for task execution)
3. **Print Mode with Streaming**: `claude -p "prompt" --output-format stream-json`

## Setup Instructions

### Prerequisites

1. **Linux System**: This application is designed to run on Linux systems and uses Linux-compatible shell commands for Claude CLI integration.

2. **Claude CLI**: Install and configure the Claude CLI tool
   ```bash
   # Install Claude CLI (follow official documentation)
   # Ensure it's available in your PATH
   claude --version
   ```

3. **Python Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

4. **Git**: Ensure Git is installed and configured for your repositories

### Configuration

1. **GitHub Repository**: Configure your GitHub repository URL in the application settings
2. **Assignees**: Set up assignee names to filter imported tasks
3. **Claude CLI**: Ensure Claude CLI is authenticated and working

### Testing the Setup

Before running the application, test your environment:

```bash
# Activate your virtual environment first
source venv/bin/activate  # or your virtual environment activation command

# Run the test script
python test_claude_cli.py
```

This will verify:
- Claude CLI availability and authentication
- Python dependencies (Flask, Werkzeug)
- Git installation
- Claude streaming mode functionality

### Running the Application

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Start the application
python app.py
```

The application will be available at `http://localhost:9000`

## Usage Guide

### Standard Workflow

1. **Upload Tasks**: Use CSV upload to import tasks
2. **Configure Prompts**: Add prompts for Claude to execute
3. **Execute Tasks**: Use START → ACTION → PUSH workflow

### Live Streaming Workflow

1. **Start Task**: Click "START" button (automatically redirects to live streaming view)
2. **Begin Streaming**: Click "START (Live Streaming)" to begin execution
3. **Watch Real-time Output**: Monitor Claude's responses as they appear in real-time
4. **Action Mode**: Click "ACTION (Live Streaming)" to execute the task
5. **Complete**: Click "COMPLETE & FINALIZE" to finish and get git diff

### CSV Format

Your CSV file should include these columns:
- `Ticket`: Unique identifier for the task
- `Task`: Description of the task
- `Link`: Optional link to ticket/issue
- `Priority`: High/Medium/Low
- `Assign`: Assignee name (must match configured assignees)
- `State`: Current state of the task

## Technical Implementation

### Live Streaming Architecture

1. **Backend**: Flask with Server-Sent Events (SSE)
2. **Claude Integration**: Subprocess execution with file-based output streaming
3. **Frontend**: JavaScript EventSource for real-time updates
4. **File Monitoring**: Real-time file reading for streaming output

### Key Components

- **Streaming Routes**: `/task/<id>/start_streaming`, `/task/<id>/action_streaming`
- **SSE Endpoint**: `/task/<id>/stream` for real-time output
- **Output Files**: JSON Lines format for structured streaming data
- **Auto-scroll**: JavaScript-based automatic scrolling with toggle

### Error Handling

- Connection timeouts with automatic retry
- Graceful handling of Claude CLI errors
- File system error recovery
- Process management for long-running tasks

## File Structure

```
├── app.py                          # Main Flask application
├── templates/
│   ├── base.html                   # Base template
│   ├── index.html                  # Task list with filters
│   ├── task_detail.html            # Standard task view
│   ├── task_detail_streaming.html  # Live streaming task view
│   └── config.html                 # Configuration page
├── static/
│   ├── css/style.css              # Styling
│   └── js/main.js                 # JavaScript functionality
├── tasks/
│   └── tasks.json                 # Task storage
├── workspaces/                    # Git workspaces for tasks (excluded from git)
├── outputs/                       # Claude CLI output files (excluded from git)
│   └── <task-id>/
│       ├── claude_output.jsonl    # Streaming output from Claude
│       └── claude_output_test.jsonl # Test output for debugging
└── requirements.txt               # Python dependencies
```

## Troubleshooting

### Claude CLI Issues

1. **Command Not Found**: Ensure Claude CLI is installed and in PATH
2. **Authentication**: Verify Claude CLI is properly authenticated
3. **Permissions**: Check file system permissions for workspace directories

### Streaming Issues

1. **No Output**: Check if Claude CLI is producing stream-json format
2. **Connection Drops**: Browser may timeout; page refresh will reconnect
3. **File Access**: Ensure application has read/write access to workspace directories

### Git Integration

1. **Clone Failures**: Verify repository URL and access permissions
2. **Push Failures**: Check Git authentication and branch permissions
3. **Workspace Conflicts**: Application cleans workspaces automatically

## Development Notes

### Extending the Application

- **New Claude Modes**: Add support for additional Claude CLI flags
- **Custom Streaming**: Implement custom streaming formats
- **Enhanced UI**: Add more interactive features for task management
- **API Integration**: Connect to external task management systems

### Security Considerations

- Input sanitization for Claude prompts
- File system access controls
- Git repository access validation
- Process isolation for Claude execution

## License

This project is provided as-is for demonstration purposes. Ensure compliance with Claude CLI terms of service and your organization's policies.
