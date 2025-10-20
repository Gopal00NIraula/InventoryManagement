# config.py

import os

# ------------------------------
# Application Configuration File
# ------------------------------

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SQLite database path
DB_PATH = os.path.join(BASE_DIR, "inventory.db")

# App settings
APP_NAME = "Inventory Management System"
WINDOW_SIZE = "800x500"
THEME_COLOR = "#f2f2f2"
