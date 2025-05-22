FROM python:3.9-slim

WORKDIR /app

# Install git
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p tasks static/uploads workspaces

# Initialize tasks.json if it doesn't exist
RUN if [ ! -f "tasks/tasks.json" ]; then echo "[]" > tasks/tasks.json; fi

# Initialize config.json if it doesn't exist
RUN if [ ! -f "config.json" ]; then echo '{"github_repo": ""}' > config.json; fi

# Expose port
EXPOSE 9000

# Run the application
CMD ["python", "run.py"]
