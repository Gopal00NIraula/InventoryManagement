# GitHub Actions Build Guide

This project is configured to automatically build a **Windows executable** using GitHub Actions (completely free!).

## How to Get Your Windows .exe

### Step 1: Push to GitHub

If you haven't already, push your code to GitHub:

```bash
# Add all files
git add .

# Commit
git commit -m "Update build configuration"

# Push to main branch
git push origin main
```

### Step 2: GitHub Actions Automatically Builds

Once you push, GitHub Actions will automatically:
1. Build **Windows .exe** (on Windows runners)
2. Package it as a downloadable artifact

### Step 3: Download Your Build

1. Go to your GitHub repository: https://github.com/Gopal00NIraula/InventoryManagement
2. Click on the **"Actions"** tab at the top
3. Click on the latest workflow run
4. Scroll down to **"Artifacts"** section
5. Download **InventoryManagement-Windows** - Contains the .exe file

## Manual Trigger

You can also manually trigger builds:

1. Go to **Actions** tab
2. Select **"Build Windows Executable"** workflow
3. Click **"Run workflow"** button
4. Select branch (usually `main`)
5. Click **"Run workflow"**

Wait a few minutes, then download the artifact!

## Build Time

Typical build time: **3-5 minutes**

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

GitHub Actions will automatically create a release with the executable attached!

## Using the Windows .exe

Once downloaded:
1. Extract `InventoryManagement.exe` from the zip file
2. Copy to any Windows computer (no Python required!)
3. Double-click to run
4. First launch creates the `inventory.db` database

**Note:** Windows Defender may show a warning (common with PyInstaller). Click "More info" → "Run anyway"

## Checking Build Status

You can add a badge to your README (optional):

```markdown
![Build Status](https://github.com/Gopal00NIraula/InventoryManagement/workflows/Build%20Windows%20Executable/badge.svg)
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

## Cost

**GitHub Actions is 100% FREE for public repositories!**

For private repositories:
- 2,000 minutes/month free
- Each build uses ~3-5 minutes
- = ~400-600 builds per month for free

## Summary

**Easiest workflow:**
1. Push code to GitHub: `git push`
2. Wait 3-5 minutes
3. Go to Actions tab
4. Download your Windows .exe!

No need for a Windows computer or complex cross-compilation! 🚀
