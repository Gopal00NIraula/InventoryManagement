# GitHub Actions Build Guide

This project is configured to automatically build executables for **Windows, Linux, and macOS** using GitHub Actions (completely free!).

## How to Get Your Windows .exe (and other builds)

### Step 1: Push to GitHub

If you haven't already, push your code to GitHub:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Add multi-platform build configuration"

# Add your GitHub repository as remote
git remote add origin https://github.com/Gopal00NIraula/InventoryManagement.git

# Push to main branch
git push -u origin main
```

### Step 2: GitHub Actions Automatically Builds

Once you push, GitHub Actions will automatically:
1. Build **Windows .exe** (on Windows runners)
2. Build **Linux executable** (on Ubuntu runners)
3. Build **macOS .app and .dmg** (on macOS runners)
4. Build **Debian .deb package** (on Ubuntu runners)

### Step 3: Download Your Builds

1. Go to your GitHub repository: https://github.com/Gopal00NIraula/InventoryManagement
2. Click on the **"Actions"** tab at the top
3. Click on the latest workflow run
4. Scroll down to **"Artifacts"** section
5. Download:
   - `InventoryManagement-Windows` - Contains the .exe file
   - `InventoryManagement-Linux` - Contains the Linux executable
   - `InventoryManagement-macOS` - Contains the .dmg installer
   - `InventoryManagement-DEB` - Contains the .deb package

## Manual Trigger

You can also manually trigger builds:

1. Go to **Actions** tab
2. Select **"Build Multi-Platform Executables"** workflow
3. Click **"Run workflow"** button
4. Select branch (usually `main`)
5. Click **"Run workflow"**

Wait a few minutes, then download artifacts!

## Build Times

Typical build times (all in parallel):
- Windows: ~3-5 minutes
- Linux: ~3-5 minutes  
- macOS: ~5-7 minutes

**Total wait time: ~5-7 minutes** (they run in parallel, not sequential!)

## Artifact Retention

- Artifacts are kept for **30 days**
- After 30 days, you'll need to trigger a new build
- Or create a GitHub Release to keep them permanently

## Creating a Release (Permanent Download Links)

To create permanent download links:

```bash
# Create a version tag
git tag v1.0.0

# Push the tag
git push origin v1.0.0
```

GitHub Actions will automatically create a release with all executables attached!

## Alternative: Local Cross-Platform Building

If you prefer to build Windows .exe locally from Ubuntu:

### Option 1: Use Wine (Complex)
```bash
sudo apt-get install wine wine64
# Then configure Wine with Windows Python... (complicated)
```

### Option 2: Use Docker
```bash
# Use a Windows container (requires WSL2 or specific Docker setup)
# Not recommended due to complexity
```

### Option 3: Use a Windows VM
```bash
# Install VirtualBox
# Create Windows VM
# Build inside VM
```

**Recommendation:** Use GitHub Actions - it's free, automatic, and handles all platforms!

## Checking Build Status

You'll see a badge in your README (optional):

```markdown
![Build Status](https://github.com/Gopal00NIraula/InventoryManagement/workflows/Build%20Multi-Platform%20Executables/badge.svg)
```

## Troubleshooting

### Build Fails

Check the Actions tab for error logs. Common issues:
- Missing dependencies (already handled in workflow)
- Syntax errors in code
- Missing files

### Can't Download Artifacts

- Make sure you're logged into GitHub
- Check that the workflow completed successfully
- Artifacts expire after 30 days

### Want to Test Before Pushing

You can use [act](https://github.com/nektos/act) to run GitHub Actions locally:

```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflows locally
act
```

## Cost

**GitHub Actions is 100% FREE for public repositories!**

For private repositories:
- 2,000 minutes/month free
- Each build uses ~15 minutes total (5 min × 3 platforms)
- = ~133 builds per month for free

## Summary

**Easiest workflow:**
1. Push code to GitHub: `git push`
2. Wait 5-7 minutes
3. Go to Actions tab
4. Download your Windows .exe, Linux binary, and macOS .dmg!

No need for Wine, Docker, or multiple computers! 🚀
