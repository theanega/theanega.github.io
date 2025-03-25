#!/bin/bash

# Configuration
OBSIDIAN_SCRIPT="obsidian_to_jekyll.py"
WEBSITE_DIR="/mnt/c/Users/oprio/Documents/_website"
COMMIT_MESSAGE="Add new post from Obsidian"

# Print header
echo "====================================="
echo "  Obsidian to Jekyll Publisher"
echo "====================================="
echo ""

# Check if a specific file was provided
if [ "$1" != "" ]; then
    echo "Processing specific file: $1"
    python "$OBSIDIAN_SCRIPT" --file "$1"
else
    echo "Processing all publishable files"
    python "$OBSIDIAN_SCRIPT"
fi

# Check if the script was successful
if [ $? -ne 0 ]; then
    echo "Error: Python script failed!"
    exit 1
fi

echo ""
echo "====================================="
echo "  Deploying to website repository"
echo "====================================="
echo ""

# Navigate to website directory
cd "$WEBSITE_DIR" || { echo "Error: Could not navigate to website directory!"; exit 1; }

# Check if there are any changes
if git status --porcelain | grep -q "_posts/"; then
    echo "Changes detected in _posts directory."
    
    # Add changes to git
    echo "Adding files to git..."
    git add _posts/
    
    # Commit changes
    echo "Committing changes..."
    git commit -m "$COMMIT_MESSAGE"
    
    # Push changes
    echo "Pushing to remote repository..."
    git push
    
    echo ""
    echo "✅ Successfully published and deployed to website!"
else
    echo "No changes detected in _posts directory."
    echo "⚠️ Nothing to commit."
fi

echo ""
echo "Done!"