#!/bin/bash

# Ensure we exit on any error
set -e

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate your virtual environment first"
    exit 1
fi

# Run tests
echo "Running tests..."
python -m pytest tests/ -v

# Check if tests passed
if [ $? -ne 0 ]; then
    echo "Tests failed. Aborting deployment."
    exit 1
fi

# Install/upgrade dependencies
echo "Installing/upgrading dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create/update requirements.txt with exact versions
echo "Updating requirements.txt with exact versions..."
pip freeze > requirements.txt

# Git operations
echo "Committing changes..."
git add .
git commit -m "Update dependencies and prepare for deployment"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin main

echo "Deployment preparation complete!"
echo "Please go to your Render dashboard to trigger the deployment."
echo "Don't forget to set your environment variables in the Render dashboard:"
echo "- CLIENT_ID"
echo "- CLIENT_SECRET"
echo "- TENANT_ID"
echo "- REDIRECT_URI"
echo "- OPENAI_API_KEY" 