#!/bin/bash

# Build script for creating macOS .dmg installer
# This script creates a DMG disk image for the Inventory Management application

APP_NAME="Inventory Management"
APP_BUNDLE="InventoryManagement.app"
DMG_NAME="InventoryManagement-1.0.0"
VOLUME_NAME="Inventory Management Installer"
DMG_BACKGROUND="installer_background.png"

echo "Building macOS application bundle..."

# Step 1: Build the app using PyInstaller
if [ ! -f "build_macos.spec" ]; then
    echo "Error: build_macos.spec not found!"
    exit 1
fi

pyinstaller build_macos.spec --clean

if [ ! -d "dist/$APP_BUNDLE" ]; then
    echo "Error: Application bundle not created!"
    exit 1
fi

echo "Application bundle created successfully!"

# Step 2: Create DMG
echo "Creating DMG installer..."

# Create a temporary folder for DMG contents
mkdir -p dmg_temp
cp -r "dist/$APP_BUNDLE" dmg_temp/

# Create a symbolic link to Applications folder
ln -s /Applications dmg_temp/Applications

# Optional: Add a background image
# Uncomment these lines if you have a background image
# mkdir -p dmg_temp/.background
# cp "$DMG_BACKGROUND" dmg_temp/.background/

# Create the DMG
if [ -f "${DMG_NAME}.dmg" ]; then
    rm "${DMG_NAME}.dmg"
fi

# Create a temporary DMG
hdiutil create -volname "$VOLUME_NAME" -srcfolder dmg_temp -ov -format UDRW temp.dmg

# Mount the temporary DMG
device=$(hdiutil attach -readwrite -noverify -noautoopen temp.dmg | grep -E '^/dev/' | sed 1q | awk '{print $1}')

# Wait for mount
sleep 2

# Optional: Set custom icon positions and window size
# This requires AppleScript
osascript <<EOT
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 700, 500}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        set position of item "$APP_BUNDLE" of container window to {150, 200}
        set position of item "Applications" of container window to {450, 200}
        update without registering applications
        delay 2
    end tell
end tell
EOT

# Sync and unmount
sync
hdiutil detach "$device"

# Convert to compressed DMG
hdiutil convert temp.dmg -format UDZO -o "${DMG_NAME}.dmg"

# Clean up
rm temp.dmg
rm -rf dmg_temp

echo "DMG created: ${DMG_NAME}.dmg"
echo ""
echo "To install:"
echo "1. Double-click ${DMG_NAME}.dmg"
echo "2. Drag '$APP_NAME' to the Applications folder"
echo "3. Launch from Applications or Spotlight"
