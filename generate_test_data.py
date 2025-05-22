#!/usr/bin/env python3
"""
Generate test data for Claude Task Manager

This script generates a sample CSV file with test tasks that can be used
to populate the Claude Task Manager application for testing purposes.
"""
import csv
import random
import os

# Sample data
TICKET_PREFIXES = ['FL', 'BUG', 'FEAT', 'TASK', 'IMP']
TASK_TYPES = [
    'Fix', 'Implement', 'Refactor', 'Optimize', 'Add', 'Update', 'Remove', 'Test'
]
TASK_SUBJECTS = [
    'login functionality', 'user authentication', 'database queries',
    'API endpoints', 'error handling', 'form validation', 'UI components',
    'navigation menu', 'search functionality', 'payment processing',
    'email notifications', 'file uploads', 'data export', 'reporting module',
    'user permissions', 'caching mechanism', 'logging system', 'admin dashboard'
]
PRIORITIES = ['High', 'Medium', 'Low']
LINK_BASE = 'https://jira.example.com/browse/'

def generate_ticket():
    """Generate a random ticket ID"""
    prefix = random.choice(TICKET_PREFIXES)
    number = random.randint(100, 999)
    return f"{prefix}-{number}"

def generate_task():
    """Generate a random task description"""
    task_type = random.choice(TASK_TYPES)
    subject = random.choice(TASK_SUBJECTS)
    return f"{task_type} {subject}"

def generate_link(ticket):
    """Generate a link for a ticket"""
    return f"{LINK_BASE}{ticket}"

def generate_csv(filename, num_tasks=10):
    """Generate a CSV file with random tasks"""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Ticket', 'Task', 'Link', 'Priority'])
        
        # Generate unique tickets
        tickets = set()
        while len(tickets) < num_tasks:
            tickets.add(generate_ticket())
        
        for ticket in tickets:
            task = generate_task()
            link = generate_link(ticket)
            priority = random.choice(PRIORITIES)
            writer.writerow([ticket, task, link, priority])
    
    print(f"Generated {num_tasks} tasks in {filename}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate test data for Claude Task Manager')
    parser.add_argument('--output', '-o', default='test_tasks.csv',
                        help='Output CSV filename (default: test_tasks.csv)')
    parser.add_argument('--count', '-n', type=int, default=10,
                        help='Number of tasks to generate (default: 10)')
    
    args = parser.parse_args()
    
    generate_csv(args.output, args.count)
    
    print("\nTo use this file:")
    print(f"1. Upload {args.output} through the Claude Task Manager web interface")
    print("2. Or place it in the application directory and run:")
    print(f"   python -c \"import os, shutil; shutil.copy('{args.output}', os.path.join('static', 'uploads', '{args.output}'))\"")
