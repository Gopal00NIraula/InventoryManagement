# Build Instructions for Inventory Management Application

This document provides step-by-step instructions for building the application for different platforms.

## Prerequisites

### Common Requirements
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Platform-Specific Requirements

#### Windows
- Windows 7 or later
- PyInstaller
- UPX (optional, for smaller executables)

#### Linux (Debian/Ubuntu)
- Debian-based distribution
- dpkg and dpkg-deb tools
- Python3-tk package

#### macOS
- macOS 10.13 (High Sierra) or later
- PyInstaller
- Xcode Command Line Tools
- hdiutil (included with macOS)

---

## Building for Windows

### Step 1: Install PyInstaller

```bash
# Activate your virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install PyInstaller
pip install pyinstaller
```

### Step 2: Build the Executable

**Option A: Using the spec file (Recommended)**
```bash
pyinstaller build_windows.spec
```

**Option B: Manual build**
```bash
pyinstaller --onefile --windowed --name InventoryManagement \
    --add-data "assets:assets" \
    --add-data "config.py:." \
    --hidden-import PIL._tkinter_finder \
    --hidden-import tkinter \
    --hidden-import sqlite3 \
    main.py
```

### Step 3: Find Your Executable

The executable will be located in:
- `dist/InventoryManagement.exe`

### Step 4: Create a Distributable Package

1. Create a folder named `InventoryManagement-Windows`
2. Copy `dist/InventoryManagement.exe` to this folder
3. Add a README.txt with usage instructions
4. Optionally, create an installer using tools like:
   - Inno Setup (https://jrsoftware.org/isinfo.php)
   - NSIS (https://nsis.sourceforge.io/)

### Windows Installer Example (Inno Setup)

Create a file named `installer.iss`:

```iss
[Setup]
AppName=Inventory Management
AppVersion=1.0.0
DefaultDirName={pf}\InventoryManagement
DefaultGroupName=Inventory Management
OutputDir=output
OutputBaseFilename=InventoryManagement-Setup

[Files]
Source: "dist\InventoryManagement.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\Inventory Management"; Filename: "{app}\InventoryManagement.exe"
Name: "{commondesktop}\Inventory Management"; Filename: "{app}\InventoryManagement.exe"
```

Then run Inno Setup Compiler to create the installer.

---

## Building for Linux (Debian/Ubuntu)

### Method 1: Create .deb Package (Recommended)

#### Step 1: Make the build script executable
```bash
chmod +x build_deb.sh
```

#### Step 2: Edit the script to customize metadata
Open `build_deb.sh` and update:
- `MAINTAINER` - Your name and email
- `APP_VERSION` - Your version number
- `DESCRIPTION` - Application description

#### Step 3: Run the build script
```bash
./build_deb.sh
```

#### Step 4: Install the package
```bash
sudo dpkg -i inventory-management_1.0.0_amd64.deb
```

To fix any dependency issues:
```bash
sudo apt-get install -f
```

#### Step 5: Run the application
```bash
inventory-management
# Or find it in your application menu
```

### Method 2: PyInstaller Binary

#### Step 1: Install PyInstaller
```bash
source .venv/bin/activate
pip install pyinstaller
```

#### Step 2: Build using the spec file
```bash
pyinstaller build_linux.spec
```

#### Step 3: Find your executable
The executable will be in `dist/InventoryManagement`

#### Step 4: Create a distributable archive
```bash
mkdir -p InventoryManagement-Linux
cp dist/InventoryManagement InventoryManagement-Linux/
cp README.md InventoryManagement-Linux/
tar -czf InventoryManagement-Linux.tar.gz InventoryManagement-Linux/
```

---

## Building for macOS

### Method 1: Create .app Bundle with DMG Installer (Recommended)

#### Step 1: Install PyInstaller
```bash
source .venv/bin/activate
pip install pyinstaller
```

#### Step 2: Build the .app bundle
```bash
pyinstaller build_macos.spec --clean
```

The application bundle will be created in `dist/InventoryManagement.app`

#### Step 3: Test the application
```bash
open dist/InventoryManagement.app
```

#### Step 4: Create DMG installer (Optional but Recommended)
```bash
chmod +x build_macos_dmg.sh
./build_macos_dmg.sh
```

This creates a professional installer: `InventoryManagement-1.0.0.dmg`

### Method 2: Manual .app Bundle Creation

If you want to customize the bundle further:

#### Step 1: Build using PyInstaller
```bash
pyinstaller build_macos.spec
```

#### Step 2: Customize Info.plist
Edit the `info_plist` section in `build_macos.spec` to update:
- Bundle identifier
- Version numbers
- Copyright information
- Display name

#### Step 3: Add Application Icon (Optional)
1. Create an `.icns` file (macOS icon format)
2. Update `build_macos.spec`: `icon='path/to/icon.icns'`
3. Rebuild: `pyinstaller build_macos.spec --clean`

#### Step 4: Code Signing (For Distribution)

To distribute outside of personal use, you should code sign:

```bash
# Sign the application
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/InventoryManagement.app

# Verify the signature
codesign --verify --verbose dist/InventoryManagement.app

# Create a signed DMG
codesign --sign "Developer ID Application: Your Name" \
  InventoryManagement-1.0.0.dmg
```

**Note:** Code signing requires:
- Apple Developer account ($99/year)
- Developer ID certificate
- Notarization for macOS 10.15+

### Method 3: Quick Distribution (No Installer)

For simple distribution without DMG:

```bash
# Build the app
pyinstaller build_macos.spec

# Create a ZIP archive
cd dist
zip -r InventoryManagement-macOS.zip InventoryManagement.app
cd ..
```

Users can:
1. Download and unzip
2. Drag InventoryManagement.app to Applications
3. Right-click and select "Open" (first time only, due to Gatekeeper)

---

## Testing Your Build

### Windows
1. Copy the .exe to a clean Windows machine (without Python installed)
2. Double-click to run
3. Verify all features work correctly

### Linux
1. Install the .deb package on a clean system:
   ```bash
   sudo dpkg -i inventory-management_1.0.0_amd64.deb
   sudo apt-get install -f  # Fix dependencies
   ```
2. Run from terminal or application menu
3. Verify all features work correctly

### macOS
1. Mount the DMG:
   ```bash
   open InventoryManagement-1.0.0.dmg
   ```
2. Drag the app to Applications folder
3. Right-click the app and select "Open" (first time only)
4. Verify all features work correctly

**Note:** On first launch, macOS may show a security warning. Go to System Preferences > Security & Privacy > General and click "Open Anyway" if needed.

---

## Troubleshooting

### Windows Build Issues

**Issue: Missing modules**
- Add missing imports to `hiddenimports` in the spec file
- Example: `hiddenimports=['missing_module']`

**Issue: Large executable size**
- Install UPX and set `upx=True` in the spec file
- Download UPX from: https://upx.github.io/

**Issue: Antivirus flags the executable**
- This is common with PyInstaller executables
- Code sign your executable with a certificate
- Submit to antivirus vendors as false positive

### Linux Build Issues

**Issue: Missing tkinter**
```bash
sudo apt-get install python3-tk
```

**Issue: Missing dependencies**
```bash
sudo apt-get install -f
```

**Issue: Permission denied**
```bash
chmod +x build_deb.sh
```

### macOS Build Issues

**Issue: "Python is not installed as a framework"**
- This is a tkinter issue on macOS
- Solution: Use python.org installer or pythonw
- Or install Python via Homebrew: `brew install python-tk`

**Issue: Gatekeeper blocks the app**
- Right-click the app and select "Open"
- Or disable Gatekeeper temporarily:
  ```bash
  sudo spctl --master-disable
  ```

**Issue: App won't open (damaged/incomplete)**
- Remove quarantine attribute:
  ```bash
  xattr -cr dist/InventoryManagement.app
  ```

**Issue: Creating DMG fails**
- Ensure you have Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```

### Database Issues

All builds will create a fresh `inventory.db` on first run. The database is created in:
- **Windows**: Same directory as the executable
- **Linux (.deb)**: `/opt/inventory-management/`
- **Linux (binary)**: Same directory as the executable
- **macOS (.app)**: Inside the application bundle at `InventoryManagement.app/Contents/MacOS/`

---

## Distribution Checklist

Before distributing your application:

- [ ] Test on clean systems without Python installed
- [ ] Verify all features work (add items, barcode generation, reports, etc.)
- [ ] Include a README or user guide
- [ ] Add version information
- [ ] Consider code signing (especially for Windows)
- [ ] Create backup/restore documentation
- [ ] Test database creation and migrations
- [ ] Verify email notifications (if configured)
- [ ] Test import/export functionality
- [ ] Check barcode generation works correctly

---

## Advanced Options

### Creating a Windows Installer with Inno Setup

1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create an installer script (example provided above)
3. Compile to create a professional installer

### Adding an Application Icon

1. Create/obtain icon files for each platform:
   - **Windows**: `.ico` file (256x256 recommended, can contain multiple sizes)
   - **Linux**: `.png` file (256x256 recommended)
   - **macOS**: `.icns` file (1024x1024 source, contains multiple sizes)

2. **Creating macOS .icns from PNG:**
   ```bash
   # Start with a 1024x1024 PNG file
   mkdir icon.iconset
   sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
   sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
   sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
   sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
   sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
   sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
   sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
   sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
   sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
   sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
   iconutil -c icns icon.iconset
   ```

3. **Update the spec files:**
   
   **Windows** (`build_windows.spec`):
   ```python
   exe = EXE(
       ...
       icon='assets/icon.ico',
   )
   ```
   
   **macOS** (`build_macos.spec`):
   ```python
   app = BUNDLE(
       ...
       icon='assets/icon.icns',
   )
   ```
   
   **Linux** (`build_deb.sh`):
   ```bash
   cp assets/icon.png debian-package/usr/share/pixmaps/inventory-management.png
   ```

### Cross-Platform Building

**Building Windows .exe on Linux/macOS:**
- Use Wine + PyInstaller
- Use Docker with Windows base image
- Use CI/CD (GitHub Actions, GitLab CI)

**Building Linux .deb on Windows/macOS:**
- Use WSL (Windows Subsystem for Linux)
- Use Docker with Ubuntu base image
- Use Virtual Machine with Linux

**Building macOS .app on Linux/Windows:**
- Requires actual macOS hardware or macOS VM
- Cannot cross-compile to macOS due to Apple restrictions
- Alternative: Use CI/CD with macOS runners (GitHub Actions)

### GitHub Actions CI/CD Example

Create `.github/workflows/build.yml` to build for all platforms automatically:

```yaml
name: Build Multi-Platform

on: [push, pull_request]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install pyinstaller python-barcode qrcode pillow openpyxl
      - run: pyinstaller build_windows.spec
      - uses: actions/upload-artifact@v2
        with:
          name: Windows-Build
          path: dist/InventoryManagement.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install pyinstaller python-barcode qrcode pillow openpyxl
      - run: pyinstaller build_macos.spec
      - run: chmod +x build_macos_dmg.sh && ./build_macos_dmg.sh
      - uses: actions/upload-artifact@v2
        with:
          name: macOS-Build
          path: InventoryManagement-1.0.0.dmg

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: sudo apt-get update && sudo apt-get install -y python3-tk
      - run: pip install pyinstaller python-barcode qrcode pillow openpyxl
      - run: chmod +x build_deb.sh && ./build_deb.sh
      - uses: actions/upload-artifact@v2
        with:
          name: Linux-Build
          path: inventory-management_1.0.0_amd64.deb
```

---

## Support

For build issues:
1. Check PyInstaller documentation: https://pyinstaller.org/
2. Check Debian packaging guide: https://www.debian.org/doc/manuals/maint-guide/
3. Review the test reports in this project
4. Check system requirements match target platform

## Version History

- v1.0.0 - Initial release with full inventory management features
