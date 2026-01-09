#!/bin/bash
# Script to connect local repository to GitHub and push code

REPO_NAME="Philosophy_Social_Media_Agent"
GITHUB_USER="tenzinngodup"
GITHUB_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

echo "Setting up GitHub remote..."
echo "Repository URL: ${GITHUB_URL}"
echo ""

# Add remote
git remote add origin ${GITHUB_URL} 2>/dev/null || git remote set-url origin ${GITHUB_URL}

# Verify remote
echo "Remote configured:"
git remote -v
echo ""

echo "Ready to push! Run the following command after creating the repo on GitHub:"
echo "  git push -u origin main"
echo ""
echo "Or if your default branch is 'master':"
echo "  git branch -M main"
echo "  git push -u origin main"
