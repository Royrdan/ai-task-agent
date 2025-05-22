#!/usr/bin/env python3
"""
Run script for Claude Task Manager

This script starts the Flask web application for the Claude Task Manager.
On Linux systems, you may need to make this file executable:
    chmod +x run.py

Then you can run it directly:
    ./run.py
"""
from app import app

if __name__ == '__main__':
    print("Starting Claude Task Manager...")
    print("Open your browser and navigate to http://localhost:9000")
    # Using host='0.0.0.0' makes the server accessible from other machines on the network
    # Remove debug=True in production environments
    app.run(debug=True, host='0.0.0.0', port=9000)
