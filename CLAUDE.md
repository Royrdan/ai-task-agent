# Claude Task Manager - Development Context

## Project Overview

This is a Flask-based task management system that integrates with Claude CLI to provide live streaming output for AI-powered task execution. The application allows users to upload tasks via CSV, manage them through a web interface, and execute them using Claude's command-line interface with real-time output streaming.

## Key Features Implemented

### 1. Live Streaming Integration
- **Real-time Output**: Uses Server-Sent Events (SSE) to stream Claude CLI output in real-time
- **Streaming Commands**: Implements `claude -p "prompt" --output-format stream-json` for live updates
- **Auto-scroll**: JavaScript-based automatic scrolling with user toggle
- **Error Handling**: Graceful connection handling with auto-reconnect

### 2. Claude CLI Integration
- **Multiple Modes**: Supports plan mode, action mode, and streaming print mode
- **Linux Compatibility**: Designed for Linux systems with proper shell command handling
- **Process Management**: Subprocess execution with proper cleanup and monitoring
- **File-based Streaming**: Uses temporary files to capture and stream Claude output

### 3. Task Management
- **CSV Import**: Upload tasks with filtering by assignee
- **Priority Management**: High/Medium/Low priority with visual indicators
- **Status Tracking**: New → Started → Actioned → Completed workflow
- **Git Integration**: Automatic repository cloning, branching, and pushing

### 4. User Interface
- **Dual Views**: Standard task view and live streaming view
- **Filtering**: Advanced column-based filtering with auto-save
- **Responsive Design**: Bootstrap-based responsive interface
- **Real-time Updates**: Live status indicators and streaming output

## Technical Architecture

### Backend (Flask)
- **Streaming Routes**: `/task/<id>/start_streaming`, `/task/<id>/action_streaming`
- **SSE Endpoint**: `/task/<id>/stream` for real-time output
- **File Management**: JSON Lines format for structured streaming data
- **Process Control**: Subprocess management for Claude CLI execution

### Frontend (JavaScript)
- **EventSource**: Real-time streaming using Server-Sent Events
- **Auto-scroll**: Configurable automatic scrolling
- **Error Recovery**: Connection timeout handling with retry logic
- **Interactive Controls**: Start, action, and complete buttons with live feedback

### Data Flow
1. User initiates streaming task
2. Flask creates workspace and clones repository
3. Claude CLI process starts with streaming output to file
4. SSE endpoint monitors file and streams to frontend
5. JavaScript displays real-time output with auto-scroll
6. User completes task to finalize and get git diff

## File Structure

```
├── app.py                          # Main Flask application with streaming routes
├── test_claude_cli.py             # Test script for Claude CLI integration
├── templates/
│   ├── task_detail_streaming.html # Live streaming interface
│   ├── task_detail.html           # Standard task interface
│   ├── index.html                 # Task list with "Live" buttons
│   └── ...
├── workspaces/                    # Git workspaces for task execution
└── README.md                      # Comprehensive documentation
```

## Claude CLI Commands Used

### Standard Commands
- `echo "prompt" | claude plan` - For task planning
- `echo "prompt" | claude act` - For task execution

### Streaming Commands
- `claude -p "prompt" --output-format stream-json > output.jsonl` - For live streaming

## Development Notes

### Linux System Requirements
- The application is specifically designed for Linux systems
- Uses Linux-compatible shell commands and file operations
- Proper quote escaping for shell injection prevention

### Security Considerations
- Input sanitization for Claude prompts using proper escaping
- File system access controls for workspace directories
- Process isolation for Claude CLI execution
- Git repository access validation

### Error Handling
- Connection timeouts with automatic retry mechanisms
- Graceful handling of Claude CLI errors and failures
- File system error recovery for workspace management
- Process cleanup for long-running tasks

### Performance Optimizations
- File-based streaming to handle large outputs efficiently
- Debounced auto-save for filter settings
- Efficient JSON parsing for streaming data
- Proper resource cleanup for subprocess management

## Testing

The `test_claude_cli.py` script verifies:
- Claude CLI availability and authentication
- Print mode functionality
- Streaming mode with JSON output
- Git availability and configuration
- Python dependencies

## Future Enhancements

### Potential Improvements
- **Enhanced Streaming**: Support for additional Claude CLI output formats
- **Real-time Collaboration**: Multiple users watching same task stream
- **Advanced Filtering**: More sophisticated task filtering and search
- **API Integration**: REST API for external task management systems
- **Custom Prompts**: Template system for reusable prompts
- **Audit Logging**: Comprehensive logging of all task activities

### Scalability Considerations
- **Database Backend**: Replace JSON file storage with proper database
- **Queue System**: Background task processing with job queues
- **Load Balancing**: Support for multiple application instances
- **Caching**: Redis-based caching for improved performance

## Integration Points

### Claude CLI
- Requires Claude CLI to be installed and authenticated
- Uses specific command-line flags for streaming output
- Handles various output formats and error conditions

### Git Integration
- Automatic repository cloning for each task
- Branch creation with standardized naming
- Commit and push operations with proper error handling

### Web Interface
- Server-Sent Events for real-time communication
- Bootstrap for responsive design
- JavaScript for interactive features and real-time updates

This project demonstrates advanced integration between web applications and command-line AI tools, providing a practical example of real-time streaming interfaces for AI-powered task execution.
