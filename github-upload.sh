#!/bin/bash
#
# Upload kfp-trainingjob-demo to GitHub
#

set -e

echo "📤 Uploading to GitHub..."
echo ""

# Configure git user
git config user.email "kriefnoy@gmail.com"
git config user.name "Noy Krief"

# Add remote (replace YOUR-USERNAME with your actual GitHub username)
echo "Adding remote..."
read -p "Enter your GitHub username: " GITHUB_USERNAME

git remote add origin https://github.com/${GITHUB_USERNAME}/kfp-trainingjob-demo.git 2>/dev/null || \
git remote set-url origin https://github.com/${GITHUB_USERNAME}/kfp-trainingjob-demo.git

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
echo "You'll be asked for:"
echo "  - Username: ${GITHUB_USERNAME}"
echo "  - Password: <your-personal-access-token>"
echo ""

git branch -M main
git push -u origin main

echo ""
echo "✅ Done! Your repo is at:"
echo "   https://github.com/${GITHUB_USERNAME}/kfp-trainingjob-demo"
echo ""

