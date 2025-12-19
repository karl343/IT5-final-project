#!/usr/bin/env python3
"""
Script to create the audit_log table in the database.
Run this if the audit_log table is missing.
"""

import sys
import os

# Add the application directory to Python path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from database.db import db

def create_audit_log_table():
    """Create the audit_log table if it doesn't exist"""
    
    print("Checking if audit_log table exists...")
    
    if db.table_exists('audit_log'):
        print("audit_log table already exists!")
        return True
    
    print("Creating audit_log table...")
    
    create_table_query = """
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action_type VARCHAR(50) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_id INT,
            action_description TEXT,
            old_values TEXT,
            new_values TEXT,
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
            INDEX idx_user_id (user_id),
            INDEX idx_action_type (action_type),
            INDEX idx_entity_type (entity_type),
            INDEX idx_created_at (created_at)
        )
    """
    
    try:
        result = db.execute_update(create_table_query)
        if db.table_exists('audit_log'):
            print("audit_log table created successfully!")
            return True
        else:
            print("Failed to create audit_log table")
            return False
    except Exception as e:
        print(f"Error creating audit_log table: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SwiftPay - Create Audit Log Table")
    print("=" * 50)
    print()
    
    success = create_audit_log_table()
    
    print()
    if success:
        print("Setup complete! You can now use the audit log feature.")
    else:
        print("Setup failed. Please check the error messages above.")
        sys.exit(1)

