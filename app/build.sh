#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p /opt/render/project/src/app

# Set proper permissions
chmod -R 755 /opt/render/project/src/app

# Initialize the database and create admin user
FLASK_ENV=production python init_db.py

# Ensure the database file has proper permissions
if [ -f "/opt/render/project/src/app/hsqe.db" ]; then
    chmod 644 /opt/render/project/src/app/hsqe.db
fi
