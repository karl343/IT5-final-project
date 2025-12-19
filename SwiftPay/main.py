#!/usr/bin/env python3


import sys
import os

# Add the application directory to Python path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QColor


def create_audit_log_table(db):
    """
    Create the audit_log table if it doesn't exist.
    """
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
        db.execute_update(create_table_query)
        print("✓ audit_log table created successfully")
    except Exception as e:
        print(f"✗ Error creating audit_log table: {e}")


def initialize_database():
    """
    Initialize the database connection and schema.
    Creates tables if they don't exist.
    """
    try:
        from database.db import db
        
        # Check if main tables exist - if not, initialize full schema
        if not db.table_exists('users'):
            print("Initializing database schema...")
            schema_path = os.path.join(APP_DIR, 'database', 'schema.sql')
            db.initialize_schema(schema_path)
        else:
            # Check if audit_log table exists, create it if missing
            if not db.table_exists('audit_log'):
                print("Creating missing audit_log table...")
                create_audit_log_table(db)
        
        # Initialize default admin user
        from modules.users import user_manager
        user_manager.initialize_admin()
        
        return True
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False


def show_splash_screen(app):
    """
    Display a splash screen during application startup.
    """
    # Create a simple splash screen
    splash_pixmap = QPixmap(400, 250)
    splash_pixmap.fill(QColor("#1a237e"))
    
    splash = QSplashScreen(splash_pixmap)
    splash.setStyleSheet("""
        QSplashScreen {
            background-color: #1a237e;
        }
    """)
    
    # Show splash
    splash.show()
    splash.showMessage(
        "SwiftPay\nPayroll Management System\n\nLoading...",
        Qt.AlignmentFlag.AlignCenter,
        Qt.GlobalColor.white
    )
    
    # Process events to display splash
    app.processEvents()
    
    return splash


def main():
    """
    Main function to start the SwiftPay application.
    """
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("SwiftPay")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SwiftPay")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Show splash screen
    splash = show_splash_screen(app)
    
    # Initialize database
    splash.showMessage(
        "SwiftPay\nPayroll Management System\n\nConnecting to database...",
        Qt.AlignmentFlag.AlignCenter,
        Qt.GlobalColor.white
    )
    app.processEvents()
    
    db_initialized = initialize_database()
    
    if not db_initialized:
        splash.close()
        QMessageBox.critical(
            None,
            "Database Error",
            "Failed to connect to the database.\n\n"
            "Please ensure:\n"
            "1. MySQL server is running\n"
            "2. Database credentials in database/db.py are correct\n"
            "3. The 'swiftpay_db' database exists or can be created\n\n"
            "Run the schema.sql file manually if needed."
        )
        sys.exit(1)
    
    # Load modules
    splash.showMessage(
        "SwiftPay\nPayroll Management System\n\nLoading modules...",
        Qt.AlignmentFlag.AlignCenter,
        Qt.GlobalColor.white
    )
    app.processEvents()
    
    # Import UI components
    from ui.login_ui import LoginWindow
    from ui.dashboard_ui import DashboardWindow
    
    # Close splash screen
    splash.close()
    
    # Create and show login window
    login_window = None
    dashboard_window = None
    
    def on_login_success(user_data):
        """Handle successful login"""
        nonlocal dashboard_window, login_window
        
        # Create and show dashboard
        dashboard_window = DashboardWindow(user_data)
        dashboard_window.logout_requested.connect(on_logout)
        dashboard_window.show()
    
    def on_logout():
        """Handle logout"""
        nonlocal login_window, dashboard_window
        
        # Close dashboard
        if dashboard_window:
            dashboard_window.close()
            dashboard_window = None
        
        # Show login window again
        login_window = LoginWindow()
        login_window.login_success.connect(on_login_success)
        login_window.show()
    
    # Show login window
    login_window = LoginWindow()
    login_window.login_success.connect(on_login_success)
    login_window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

