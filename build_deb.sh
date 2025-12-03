#!/bin/bash

# Build script for creating .deb package
# This script creates a Debian package for the Inventory Management application

APP_NAME="inventory-management"
APP_VERSION="1.0.0"
MAINTAINER="Your Name <your.email@example.com>"
DESCRIPTION="Inventory Management System - A comprehensive inventory tracking application"

# Create directory structure
mkdir -p debian-package/DEBIAN
mkdir -p debian-package/opt/$APP_NAME
mkdir -p debian-package/usr/share/applications
mkdir -p debian-package/usr/share/pixmaps
mkdir -p debian-package/usr/local/bin

# Create control file
cat > debian-package/DEBIAN/control << EOF
Package: $APP_NAME
Version: $APP_VERSION
Section: utils
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-tk, python3-pil, python3-pil.imagetk
Maintainer: $MAINTAINER
Description: $DESCRIPTION
 A desktop application for managing inventory, suppliers, customers,
 purchase orders, sales orders, and stock alerts with barcode support.
EOF

# Copy application files to package
echo "Copying application files..."
cp -r * debian-package/opt/$APP_NAME/ 2>/dev/null || true
rm -rf debian-package/opt/$APP_NAME/debian-package
rm -rf debian-package/opt/$APP_NAME/dist
rm -rf debian-package/opt/$APP_NAME/build
rm -rf debian-package/opt/$APP_NAME/__pycache__
find debian-package/opt/$APP_NAME -name "*.pyc" -delete
find debian-package/opt/$APP_NAME -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create launcher script
cat > debian-package/usr/local/bin/$APP_NAME << 'EOF'
#!/bin/bash
cd /opt/inventory-management
python3 main.py
EOF
chmod +x debian-package/usr/local/bin/$APP_NAME

# Create desktop entry
cat > debian-package/usr/share/applications/$APP_NAME.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Inventory Management
Comment=Manage your inventory efficiently
Exec=/usr/local/bin/$APP_NAME
Icon=inventory-management
Terminal=false
Categories=Office;Database;
EOF

# Create postinst script for installing Python dependencies
cat > debian-package/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

echo "Installing Python dependencies..."
cd /opt/inventory-management

# Check if virtual environment exists, if not create it
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Install dependencies
.venv/bin/pip install --upgrade pip
.venv/bin/pip install python-barcode qrcode pillow openpyxl

# Update the launcher to use virtual environment
cat > /usr/local/bin/inventory-management << 'LAUNCHER'
#!/bin/bash
cd /opt/inventory-management
.venv/bin/python main.py
LAUNCHER
chmod +x /usr/local/bin/inventory-management

echo "Installation complete!"
exit 0
EOF
chmod +x debian-package/DEBIAN/postinst

# Create prerm script for cleanup
cat > debian-package/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e
echo "Removing Inventory Management..."
exit 0
EOF
chmod +x debian-package/DEBIAN/prerm

# Build the package
echo "Building .deb package..."
dpkg-deb --build debian-package ${APP_NAME}_${APP_VERSION}_amd64.deb

echo "Package created: ${APP_NAME}_${APP_VERSION}_amd64.deb"
echo ""
echo "To install: sudo dpkg -i ${APP_NAME}_${APP_VERSION}_amd64.deb"
echo "To uninstall: sudo apt remove $APP_NAME"
