# Inventory Management System

A comprehensive desktop application for managing inventory, suppliers, customers, orders, and more. Built with Python and Tkinter.

## 📋 Table of Contents
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [User Guide](#user-guide)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## ✨ Features

### Core Features
- **User Authentication**: Role-based access control (Admin/Manager/Staff)
- **Inventory Management**: Add, edit, delete, and search inventory items
- **Supplier Management**: Manage supplier information and relationships
- **Customer Management**: Track customer details and order history
- **Purchase Orders**: Create and manage purchase orders from suppliers
- **Sales Orders**: Process and track customer sales orders
- **Stock Alerts**: Automatic notifications for low stock and reorder levels
- **Audit Logging**: Complete audit trail of all system activities

### Advanced Features
- **Barcode & QR Code Generation**: Generate and print barcodes/QR codes for items
- **Email Notifications**: Automated email alerts for stock levels and order updates
- **Data Import/Export**: CSV and Excel import/export for bulk operations
- **Reports & Analytics**: Sales reports, inventory reports, and analytics
- **Dashboard**: Real-time overview of inventory status and recent activities
- **Multi-user Support**: Concurrent user access with proper authentication

## 💻 System Requirements

### Software Requirements
- **Operating System**: Linux (Ubuntu 20.04+), Windows 10+, or macOS 10.14+
- **Python**: Python 3.12 or higher
- **Display**: Minimum 1280x720 resolution

### Hardware Requirements
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 100MB for application + space for database
- **Network**: Optional (for email notifications)

## 📥 Installation

### 1. Clone or Download the Repository
```bash
cd /path/to/your/projects
# If you have git:
git clone <repository-url>
# Or extract the downloaded ZIP file
```

### 2. Install System Dependencies (Linux/Ubuntu)
```bash
# Install Python 3.12 and required packages
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-tk python3-pil.imagetk

# For older Python versions, install python3-tk and python3-pil separately
```

### 3. Create Virtual Environment
```bash
cd InventoryManagement
python3 -m venv .venv
```

### 4. Activate Virtual Environment
```bash
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 5. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Running the Application

### Using Virtual Environment (Recommended)
```bash
# Make sure you're in the project directory
cd /path/to/InventoryManagement

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Run the application
python main.py
```

### Using System Python
```bash
python3 main.py
```

### First-Time Setup
On first run, the application will:
1. Create the SQLite database (`inventory.db`)
2. Initialize all required tables
3. Create a default admin user:
   - **Username**: `admin`
   - **Password**: `admin123`
   - **⚠️ IMPORTANT**: Change this password after first login!

## 📖 User Guide

### Login
1. Launch the application
2. Enter username and password
3. Click "Login" or press Enter

### Dashboard Overview
- **Dashboard Tab**: View key metrics, recent activity, and items needing attention
- **Inventory Tab**: Manage inventory items
- **Suppliers Tab**: Manage supplier information
- **Customers Tab**: Manage customer information
- **Purchase Orders Tab**: Create and track purchase orders
- **Sales Orders Tab**: Process sales orders
- **Stock Alerts Tab**: Monitor low stock items
- **Reports Tab**: Generate various reports
- **Audit Log Tab**: View system activity history
- **Barcodes Tab**: Generate and manage barcodes/QR codes
- **Users Tab**: Manage user accounts (Admin only)

### Managing Inventory

#### Add New Item
1. Click "➕ Add Item"
2. Fill in required fields:
   - SKU (Stock Keeping Unit)
   - Name
   - Category
   - Quantity
   - Unit (pcs, kg, ltr, etc.)
   - Cost Price
   - Selling Price
3. Optional fields:
   - Description
   - Reorder Level
   - Supplier
   - Location
   - Barcode/QR Code
4. Click "Save"

#### Edit Item
1. Select item from the table
2. Click "✏️ Edit Item"
3. Modify fields as needed
4. Click "Update"

#### Delete Item
1. Select item from the table
2. Click "🗑️ Delete Item"
3. Confirm deletion

#### Search Items
- Enter search term in the search box
- Press Enter or click "Search"
- Use "Refresh" to show all items

#### Import/Export
- **Export**: Click "📤 Export" to save data to CSV or Excel
- **Import**: Click "📥 Import" to load data from CSV or Excel

### Managing Suppliers

#### Add Supplier
1. Go to "🏢 Suppliers" tab
2. Click "➕ Add Supplier"
3. Fill in:
   - Name (required)
   - Email (required)
   - Phone (required)
   - Contact Person, Address, City, Country, Notes (optional)
4. Click "Save"

### Managing Customers
Same process as suppliers, using the "👥 Customers" tab

### Purchase Orders

#### Create Purchase Order
1. Go to "📥 Purchase Orders" tab
2. Click "➕ Create Order"
3. Select supplier
4. Add items:
   - Select item
   - Enter quantity
   - Price auto-fills from item cost
   - Click "Add Item"
5. Review total amount
6. Click "Create Order"

#### Complete Purchase Order
1. Select order from table
2. Click "✅ Complete Order"
3. Inventory quantities will be updated automatically
4. Email notification sent (if configured)

### Sales Orders
Similar to Purchase Orders, using the "📤 Sales Orders" tab

### Stock Alerts
- View items with low stock or out of stock
- Click "Send Email Alerts" to notify admins
- Click "Generate Report" for printable alert list

### Reports
1. Select report type (Sales, Inventory, Low Stock)
2. Choose date range
3. Click "Generate Report"
4. View or export results

### Barcode Management
1. Go to "📊 Barcodes" tab
2. Select item from dropdown
3. Choose barcode or QR code format
4. Click "Generate"
5. Use "Print" to print labels
6. Use "Save Image" to save as file

### Email Configuration (Admin Only)
1. Click "⚙️ Email Settings" in dashboard header
2. Configure SMTP settings:
   - SMTP Server (e.g., smtp.gmail.com)
   - SMTP Port (e.g., 587)
   - Sender Email
   - Password
3. Enable/disable email notifications
4. Click "Test Email" to verify settings
5. Click "Save Settings"

### User Management (Admin Only)
1. Go to "👤 Users" tab
2. Add, edit, or delete users
3. Assign roles: Admin, Manager, or Staff
4. Reset passwords as needed

## 📁 Project Structure

```
InventoryManagement/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .env                  # Email configuration (created after setup)
├── inventory.db          # SQLite database (created on first run)
│
├── database/             # Database layer
│   ├── __init__.py
│   ├── db_connection.py  # Database connection management
│   └── db_setup.py       # Database schema and migrations
│
├── models/               # Data models and business logic
│   ├── __init__.py
│   ├── user_model.py           # User management
│   ├── inventory_model.py      # Inventory operations
│   ├── supplier_model.py       # Supplier management
│   ├── customer_model.py       # Customer management
│   ├── purchase_order_model.py # Purchase order operations
│   ├── sales_order_model.py    # Sales order operations
│   ├── stock_alert_model.py    # Stock alerts and monitoring
│   ├── audit_log_model.py      # Audit trail
│   ├── report_model.py         # Report generation
│   ├── barcode_model.py        # Barcode operations
│   └── dashboard_stats.py      # Dashboard statistics
│
├── views/                # User interface
│   ├── __init__.py
│   ├── auth_view.py      # Login screen
│   ├── dashboard_view.py # Main application window
│   └── app.py           # Application initialization
│
├── controllers/          # Business logic controllers
│   ├── __init__.py
│   ├── login_controller.py         # Authentication
│   ├── inventory_controller.py     # Inventory logic
│   ├── purchase_order_controller.py
│   ├── sales_order_controller.py
│   └── barcode_controller.py
│
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── encryption.py     # Password hashing
│   ├── email_notifications.py  # Email sending
│   └── import_export.py  # CSV/Excel import/export
│
└── assets/               # Images and resources
    └── barcodes/        # Generated barcode images
```

## 🗄️ Database Schema

### Tables

#### users
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- password (TEXT - hashed)
- role (TEXT - Admin/Manager/Staff)
- email (TEXT)
- created_at (TIMESTAMP)

#### inventory_items
- id (INTEGER PRIMARY KEY)
- sku (TEXT UNIQUE)
- name (TEXT)
- description (TEXT)
- category (TEXT)
- quantity (INTEGER)
- unit (TEXT)
- cost_price (REAL)
- selling_price (REAL)
- reorder_level (INTEGER)
- supplier_id (INTEGER FK)
- location (TEXT)
- barcode (TEXT)
- qr_code (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

#### suppliers
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- contact_person (TEXT)
- email (TEXT)
- phone (TEXT)
- address (TEXT)
- city (TEXT)
- country (TEXT)
- notes (TEXT)
- created_at (TIMESTAMP)

#### customers
- Similar structure to suppliers

#### purchase_orders
- id (INTEGER PRIMARY KEY)
- order_number (TEXT UNIQUE)
- supplier_id (INTEGER FK)
- order_date (TIMESTAMP)
- status (TEXT - Pending/Completed/Cancelled)
- total_amount (REAL)
- notes (TEXT)
- created_by (INTEGER FK - users)

#### purchase_order_items
- id (INTEGER PRIMARY KEY)
- purchase_order_id (INTEGER FK)
- item_id (INTEGER FK)
- quantity (INTEGER)
- unit_price (REAL)
- subtotal (REAL)

#### sales_orders
- Similar structure to purchase_orders
- customer_id instead of supplier_id

#### sales_order_items
- Similar structure to purchase_order_items

#### stock_alerts
- id (INTEGER PRIMARY KEY)
- item_id (INTEGER FK)
- alert_type (TEXT)
- threshold (INTEGER)
- current_quantity (INTEGER)
- created_at (TIMESTAMP)
- resolved (BOOLEAN)

#### audit_log
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER FK)
- action (TEXT)
- resource_type (TEXT)
- resource_id (INTEGER)
- details (TEXT)
- timestamp (TIMESTAMP)

## ⚙️ Configuration

### Email Configuration (.env file)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
USE_TLS=True
EMAIL_ENABLED=True
```

**Note for Gmail users:**
- Enable 2-Factor Authentication
- Generate an "App Password" instead of using your regular password
- Use the app password in the SENDER_PASSWORD field

### Application Settings (config.py)
- Database path
- Default admin credentials
- Application window size
- Theme colors

## 🔧 Troubleshooting

### Database Issues
**Problem**: Database locked error
**Solution**: Close all instances of the application and restart

**Problem**: Database corruption
**Solution**: Restore from backup or delete `inventory.db` to recreate

### Import Errors
**Problem**: "No module named 'PIL'"
**Solution**: 
```bash
pip install pillow
# On Linux:
sudo apt install python3-pil.imagetk
```

**Problem**: "No module named 'openpyxl'"
**Solution**:
```bash
pip install openpyxl
```

### Email Issues
**Problem**: Email not sending
**Solution**:
1. Check SMTP settings in Email Configuration
2. Verify email/password are correct
3. For Gmail, use an App Password
4. Check firewall/antivirus isn't blocking port 587

### Virtual Environment Issues
**Problem**: "No module named pip"
**Solution**:
```bash
# Install python3-venv
sudo apt install python3.12-venv
# Recreate venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Display Issues
**Problem**: Window too small or cut off
**Solution**: Adjust screen resolution or modify window size in config.py

## 👨‍💻 Development

### Running Tests
Currently, the application uses manual testing. Automated tests coming soon.

### Adding New Features
1. Create model in `models/` for data operations
2. Add UI components in `views/dashboard_view.py`
3. Implement business logic in `controllers/`
4. Update database schema in `database/db_setup.py` if needed
5. Test thoroughly before deployment

### Database Migrations
- Database schema is auto-migrated on application start
- Add migration code in `database/db_setup.py`
- Migrations preserve existing data

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Support

For issues, questions, or feature requests:
1. Check the Troubleshooting section
2. Review the User Guide
3. Contact system administrator

## 🔄 Updates and Maintenance

### Backup Recommendations
- Backup `inventory.db` regularly
- Backup `.env` configuration file
- Store backups in secure location

### Update Process
1. Backup database
2. Pull latest code changes
3. Update dependencies: `pip install -r requirements.txt`
4. Test in development environment
5. Deploy to production

---

**Version**: 1.0.0  
**Last Updated**: December 2, 2025  
**Developed with**: Python 3.12 + Tkinter
