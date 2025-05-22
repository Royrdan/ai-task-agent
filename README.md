# Claude Task Manager

A Flask web application that manages tasks from a CSV file and interacts with Claude via command line to automate code changes.

## Features

- Configure GitHub repository for tasks
- Upload CSV files with ticket, task, and link columns
- Add prompts for Claude to execute
- Run Claude in plan mode to analyze tasks
- Run Claude in action mode to implement changes
- View git diffs of changes made by Claude
- Add follow-up prompts for refinement
- Push changes to GitHub with proper branch naming and commit messages

## Requirements

- Python 3.8+
- Flask and dependencies (see requirements.txt)
- Git installed and configured
- Claude CLI installed and accessible from the command line

## Installation (Linux)

### Docker Deployment

The easiest way to deploy the application is using Docker:

1. Clone this repository:
   ```
   git clone <repository-url>
   cd claude-task-manager
   ```

2. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

3. Access the application at http://localhost:9000

The Docker setup:
- Uses Python 3.9 as the base image
- Installs Git and all required dependencies
- Persists data (tasks, workspaces, and configuration) using volumes
- Exposes the application on port 9000
- Automatically restarts the container if it crashes

To stop the container:
```
docker-compose down
```

### Automatic Setup (Without Docker)

The easiest way to set up the application is to use the provided setup script:

1. Clone this repository:
   ```
   git clone <repository-url>
   cd claude-task-manager
   ```

2. Make the setup script executable:
   ```
   chmod +x setup.sh
   ```

3. Run the setup script:
   ```
   ./setup.sh
   ```

The script will:
- Check if Python 3.8+ and Git are installed
- Create a virtual environment
- Install dependencies
- Set up the necessary directories and files
- Make the run.py script executable

### Manual Setup

If you prefer to set up the application manually:

1. Ensure Python 3.8+ is installed:
   ```
   python3 --version
   ```
   If Python is not installed or is an older version, install it using your distribution's package manager:
   ```
   # For Debian/Ubuntu
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # For Red Hat/Fedora
   sudo dnf install python3 python3-pip
   ```

2. Ensure Git is installed:
   ```
   git --version
   ```
   If Git is not installed, install it:
   ```
   # For Debian/Ubuntu
   sudo apt install git
   
   # For Red Hat/Fedora
   sudo dnf install git
   ```

3. Clone this repository:
   ```
   git clone <repository-url>
   cd claude-task-manager
   ```

4. Create a virtual environment and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Make the run script executable:
   ```
   chmod +x run.py
   ```

## Usage (Linux)

1. Make the run script executable:
   ```
   chmod +x run.py
   ```

2. Start the application using one of these methods:
   ```
   # Method 1: Using the executable run.py
   ./run.py
   
   # Method 2: Using Python directly
   python3 run.py
   
   # Method 3: Using Flask directly
   export FLASK_APP=app.py
   flask run --host=0.0.0.0 --port=9000
   ```

2. Open your browser and navigate to `http://localhost:9000`

3. Configure the GitHub repository URL in the Configuration page

4. Upload a CSV file with the following columns:
   - `ticket`: Ticket identifier (e.g., "FL-123")
   - `task`: Description of the task
   - `link`: URL to the ticket (optional)

5. For each task:
   - Add a prompt for Claude
   - Click START to clone the repository and run Claude in plan mode
   - Review Claude's output
   - Click ACTION to execute the task
   - Review the git diff of changes
   - Add follow-up prompts if needed
   - Click PUSH CHANGES to create a branch, commit, and push the changes

## CSV Format Example

```csv
ticket,task,link
FL-123,Fix transaction handling bug,https://jira.example.com/browse/FL-123
FL-124,Add pagination to user list,https://jira.example.com/browse/FL-124
FL-125,Improve error handling in API,https://jira.example.com/browse/FL-125
```

### Generating Test Data

A script is provided to generate test data for the application:

1. Make the script executable:
   ```
   chmod +x generate_test_data.py
   ```

2. Generate test data:
   ```
   # Generate 10 random tasks (default)
   ./generate_test_data.py
   
   # Generate a specific number of tasks
   ./generate_test_data.py --count 20
   
   # Specify output filename
   ./generate_test_data.py --output my_tasks.csv
   ```

3. Upload the generated CSV file through the web interface

## Project Structure

```
claude-task-manager/
├── app.py                  # Main Flask application
├── config.json             # Configuration storage
├── requirements.txt        # Python dependencies
├── run.py                  # Script to run the application
├── setup.sh                # Setup script for Linux
├── generate_test_data.py   # Script to generate test data
├── update_claude_command.py # Script to update Claude CLI commands
├── sample_tasks.csv        # Sample CSV file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── .gitignore              # Git ignore file
├── tasks/                  # Directory for task storage
│   └── tasks.json          # Task data
├── static/                 # Static assets
│   ├── css/                # CSS files
│   │   └── style.css       # Custom CSS styles
│   ├── js/                 # JavaScript files
│   │   └── main.js         # Custom JavaScript
│   └── uploads/            # Temporary CSV uploads
├── templates/              # Jinja2 templates
│   ├── base.html           # Base template
│   ├── index.html          # Main page
│   ├── config.html         # Configuration page
│   └── task_detail.html    # Task detail page
└── workspaces/             # Directory for cloned repositories
    └── [task_id]/          # Subdirectories for each task
```

## Notes on Claude Integration

The application assumes that Claude is available via command line with the following commands:
- `echo "prompt" | claude plan` - Run Claude in plan mode
- `echo "prompt" | claude act` - Run Claude in action mode

### Customizing Claude Integration

If your Claude CLI setup uses a different command format, you can use the provided script to update the commands:

1. Make the script executable:
   ```
   chmod +x update_claude_command.py
   ```

2. Run the script with your custom command formats:
   ```
   ./update_claude_command.py --plan "echo '{prompt}' | claude plan" --action "echo '{prompt}' | claude act"
   ```

Examples of different command formats:
```
# Using a specific Claude model
./update_claude_command.py --plan "anthropic claude -m claude-3-opus-20240229 '{prompt}'" --action "anthropic claude -m claude-3-opus-20240229 '{prompt}'"

# Using a configuration file
./update_claude_command.py --plan "claude --config ~/.claude/config.json plan '{prompt}'" --action "claude --config ~/.claude/config.json act '{prompt}'"

# Using an API key
./update_claude_command.py --plan "claude --api-key $CLAUDE_API_KEY plan '{prompt}'" --action "claude --api-key $CLAUDE_API_KEY act '{prompt}'"
```

The script will update the `run_claude_command` function in `app.py` to use your specified command formats.

## License

MIT
