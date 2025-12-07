#!/usr/bin/env python3
"""
Password Reset Utility for Inventory Management System
This script allows you to reset passwords for any user account.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import get_connection
from utils.encryption import hash_password
import getpass

def list_users():
    """Display all users in the system."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT username, email, role, first_name, last_name 
        FROM users 
        ORDER BY role, username
    """)
    users = cursor.fetchall()
    
    print("\n" + "=" * 80)
    print("CURRENT USERS IN SYSTEM")
    print("=" * 80)
    
    if not users:
        print("No users found in database.")
        conn.close()
        return []
    
    for i, user in enumerate(users, 1):
        username, email, role, first_name, last_name = user
        name = f"{first_name or ''} {last_name or ''}".strip() or "N/A"
        email_display = email or "N/A"
        
        print(f"\n{i}. Username: {username}")
        print(f"   Name: {name}")
        print(f"   Email: {email_display}")
        print(f"   Role: {role}")
        print("-" * 80)
    
    conn.close()
    return [user[0] for user in users]  # Return list of usernames

def reset_password(username, new_password):
    """Reset password for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"\n❌ Error: User '{username}' not found!")
        conn.close()
        return False
    
    # Hash the new password
    hashed_password = hash_password(new_password)
    
    # Update the password
    cursor.execute("""
        UPDATE users 
        SET password = ? 
        WHERE username = ?
    """, (hashed_password, username))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Password successfully reset for user: {username}")
    return True

def main():
    print("\n" + "=" * 80)
    print("INVENTORY MANAGEMENT SYSTEM - PASSWORD RESET UTILITY")
    print("=" * 80)
    
    # List all users
    usernames = list_users()
    
    if not usernames:
        print("\n❌ No users found in database. Please create a user first.")
        return
    
    print("\n")
    
    # Get username to reset
    while True:
        username = input("Enter username to reset password (or 'quit' to exit): ").strip()
        
        if username.lower() == 'quit':
            print("\nExiting password reset utility.")
            return
        
        if username in usernames:
            break
        else:
            print(f"❌ Invalid username. Please choose from the list above.")
    
    # Get new password
    print(f"\nResetting password for user: {username}")
    print("Password requirements:")
    print("  - Minimum 4 characters (recommended: 8+ characters)")
    print("  - Mix of letters, numbers, and symbols recommended")
    print()
    
    while True:
        password1 = getpass.getpass("Enter new password: ")
        
        if len(password1) < 4:
            print("❌ Password must be at least 4 characters long. Try again.\n")
            continue
        
        password2 = getpass.getpass("Confirm new password: ")
        
        if password1 != password2:
            print("❌ Passwords do not match. Try again.\n")
            continue
        
        break
    
    # Confirm reset
    print(f"\n⚠️  You are about to reset the password for: {username}")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        if reset_password(username, password1):
            print("\n" + "=" * 80)
            print("PASSWORD RESET SUCCESSFUL!")
            print("=" * 80)
            print(f"\nYou can now login with:")
            print(f"  Username: {username}")
            print(f"  Password: (the password you just set)")
            print("\nPlease keep your password secure and do not share it with others.")
            print("=" * 80)
    else:
        print("\n❌ Password reset cancelled.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Password reset cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
