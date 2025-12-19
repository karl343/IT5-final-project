"""
SwiftPay User Authentication Module
Handles user login, registration, and management
"""

import bcrypt
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import db
from modules.audit_log import audit_logger, AuditLogger


class UserManager:
    """
    Manages user authentication and user CRUD operations.
    Implements secure password hashing using bcrypt.
    """
    
    def __init__(self):
        """Initialize UserManager with database connection"""
        self.db = db
        self.current_user = None
    
    def hash_password(self, password):
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored password hash
            
        Returns:
            Boolean indicating if password matches
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def login(self, username, password):
        """
        Authenticate user login.
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            Dictionary with user info if successful, None otherwise
        """
        query = """
            SELECT user_id, username, password_hash, full_name, role, status
            FROM users
            WHERE username = %s AND status = 'Active'
        """
        
        user = self.db.execute_query(query, (username,), fetch_one=True)
        
        if user and self.verify_password(password, user['password_hash']):
            # Remove password hash from returned data
            self.current_user = {
                'user_id': user['user_id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role']
            }
            # Log login
            audit_logger.log_user_action(
                user_id=user['user_id'],
                action_type=AuditLogger.ACTION_LOGIN,
                entity_type=AuditLogger.ENTITY_USER,
                entity_id=user['user_id'],
                description=f"User '{user['username']}' logged in"
            )
            return self.current_user
        
        return None
    
    def logout(self):
        """Clear current user session"""
        if self.current_user:
            # Log logout
            audit_logger.log_user_action(
                user_id=self.current_user.get('user_id'),
                action_type=AuditLogger.ACTION_LOGOUT,
                entity_type=AuditLogger.ENTITY_USER,
                entity_id=self.current_user.get('user_id'),
                description=f"User '{self.current_user.get('username')}' logged out"
            )
        self.current_user = None
    
    def get_current_user(self):
        """Get currently logged in user"""
        return self.current_user
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.current_user and self.current_user.get('role') == 'Admin'
    
    def create_user(self, username, password, full_name, role='Staff'):
        """
        Create a new user account.
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role (Admin/Staff)
            
        Returns:
            New user ID if successful, None otherwise
        """
        # Check if username already exists
        existing = self.db.execute_query(
            "SELECT user_id FROM users WHERE username = %s",
            (username,),
            fetch_one=True
        )
        
        if existing:
            return None
        
        hashed = self.hash_password(password)
        
        query = """
            INSERT INTO users (username, password_hash, full_name, role, status)
            VALUES (%s, %s, %s, %s, 'Active')
        """
        
        user_id = self.db.execute_insert(query, (username, hashed, full_name, role))
        
        # Log user creation
        if user_id and self.current_user:
            audit_logger.log_user_action(
                user_id=self.current_user.get('user_id'),
                action_type=AuditLogger.ACTION_CREATE,
                entity_type=AuditLogger.ENTITY_USER,
                entity_id=user_id,
                description=f"Created new user '{username}' with role '{role}'",
                new_values={'username': username, 'full_name': full_name, 'role': role}
            )
        
        return user_id
    
    def update_user(self, user_id, full_name=None, role=None, status=None):
        """
        Update user information.
        
        Args:
            user_id: ID of user to update
            full_name: New full name (optional)
            role: New role (optional)
            status: New status (optional)
            
        Returns:
            Number of rows affected
        """
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        if role:
            updates.append("role = %s")
            params.append(role)
        if status:
            updates.append("status = %s")
            params.append(status)
        
        if not updates:
            return 0
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        
        # Get old values for audit log
        old_user = self.get_user_by_id(user_id)
        old_values = {}
        if old_user:
            if full_name:
                old_values['full_name'] = old_user.get('full_name')
            if role:
                old_values['role'] = old_user.get('role')
            if status:
                old_values['status'] = old_user.get('status')
        
        result = self.db.execute_update(query, tuple(params))
        
        # Log user update
        if result > 0 and self.current_user:
            new_values = {}
            if full_name:
                new_values['full_name'] = full_name
            if role:
                new_values['role'] = role
            if status:
                new_values['status'] = status
            
            audit_logger.log_user_action(
                user_id=self.current_user.get('user_id'),
                action_type=AuditLogger.ACTION_UPDATE,
                entity_type=AuditLogger.ENTITY_USER,
                entity_id=user_id,
                description=f"Updated user ID {user_id}",
                old_values=old_values if old_values else None,
                new_values=new_values if new_values else None
            )
        
        return result
    
    def change_password(self, user_id, old_password, new_password):
        """
        Change user's password.
        
        Args:
            user_id: ID of user
            old_password: Current password
            new_password: New password
            
        Returns:
            Boolean indicating success
        """
        # Verify old password
        user = self.db.execute_query(
            "SELECT password_hash FROM users WHERE user_id = %s",
            (user_id,),
            fetch_one=True
        )
        
        if not user or not self.verify_password(old_password, user['password_hash']):
            return False
        
        # Update with new password
        new_hash = self.hash_password(new_password)
        result = self.db.execute_update(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (new_hash, user_id)
        )
        
        # Log password change
        if result > 0:
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_PASSWORD_CHANGE,
                entity_type=AuditLogger.ENTITY_USER,
                entity_id=user_id,
                description="User changed their password"
            )
        
        return result > 0
    
    def reset_password(self, user_id, new_password):
        """
        Reset user's password (admin function).
        
        Args:
            user_id: ID of user
            new_password: New password
            
        Returns:
            Boolean indicating success
        """
        new_hash = self.hash_password(new_password)
        result = self.db.execute_update(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (new_hash, user_id)
        )
        
        # Log password reset
        if result > 0 and self.current_user:
            audit_logger.log_user_action(
                user_id=self.current_user.get('user_id'),
                action_type=AuditLogger.ACTION_PASSWORD_RESET,
                entity_type=AuditLogger.ENTITY_USER,
                entity_id=user_id,
                description=f"Password reset for user ID {user_id}"
            )
        
        return result > 0
    
    def delete_user(self, user_id):
        """
        Soft delete a user (set status to Inactive).
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            Number of rows affected
        """
        # Get user info before deletion
        user = self.get_user_by_id(user_id)
        
        result = self.db.execute_update(
            "UPDATE users SET status = 'Inactive' WHERE user_id = %s",
            (user_id,)
        )
        
        # Log user deletion
        if result > 0 and self.current_user and user:
            audit_logger.log_user_action(
                user_id=self.current_user.get('user_id'),
                action_type=AuditLogger.ACTION_DELETE,
                entity_type=AuditLogger.ENTITY_USER,
                entity_id=user_id,
                description=f"Deleted user '{user.get('username')}'",
                old_values={'username': user.get('username'), 'status': user.get('status')}
            )
        
        return result
    
    def get_all_users(self, include_inactive=False):
        """
        Get all users.
        
        Args:
            include_inactive: Include inactive users
            
        Returns:
            List of user dictionaries
        """
        if include_inactive:
            query = """
                SELECT user_id, username, full_name, role, status, created_at
                FROM users
                ORDER BY full_name
            """
            return self.db.execute_query(query)
        else:
            query = """
                SELECT user_id, username, full_name, role, status, created_at
                FROM users
                WHERE status = 'Active'
                ORDER BY full_name
            """
            return self.db.execute_query(query)
    
    def get_user_by_id(self, user_id):
        """
        Get user by ID.
        
        Args:
            user_id: ID of user
            
        Returns:
            User dictionary or None
        """
        query = """
            SELECT user_id, username, full_name, role, status, created_at
            FROM users
            WHERE user_id = %s
        """
        return self.db.execute_query(query, (user_id,), fetch_one=True)
    
    def initialize_admin(self):
        """
        Create default admin user if no admin exists.
        Default credentials: admin / admin123
        """
        # Check if admin user exists
        admin = self.db.execute_query(
            "SELECT user_id, password_hash FROM users WHERE username = 'admin' LIMIT 1",
            fetch_one=True
        )
        
        if not admin:
            # Create new admin user
            self.create_user(
                username='admin',
                password='admin123',
                full_name='System Administrator',
                role='Admin'
            )
            print("Default admin user created (admin/admin123)")
        else:
            # Verify the password works, if not reset it
            if not self.verify_password('admin123', admin['password_hash']):
                new_hash = self.hash_password('admin123')
                self.db.execute_update(
                    "UPDATE users SET password_hash = %s, status = 'Active' WHERE username = 'admin'",
                    (new_hash,)
                )
                print("Admin password reset to default (admin/admin123)")
        
        return True


# Create a global user manager instance
user_manager = UserManager()

