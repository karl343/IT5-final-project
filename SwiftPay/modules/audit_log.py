"""
SwiftPay Audit Log Module
Handles logging of all system activities and user actions
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import db


class AuditLogger:
    """
    Manages audit logging for all system activities.
    Tracks user actions, data changes, and system events.
    """
    
    # Action types
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_VIEW = 'VIEW'
    ACTION_EXPORT = 'EXPORT'
    ACTION_APPROVE = 'APPROVE'
    ACTION_REJECT = 'REJECT'
    ACTION_PASSWORD_CHANGE = 'PASSWORD_CHANGE'
    ACTION_PASSWORD_RESET = 'PASSWORD_RESET'
    ACTION_TIME_IN = 'TIME_IN'
    ACTION_TIME_OUT = 'TIME_OUT'
    ACTION_GENERATE = 'GENERATE'
    
    # Entity types
    ENTITY_USER = 'USER'
    ENTITY_EMPLOYEE = 'EMPLOYEE'
    ENTITY_ATTENDANCE = 'ATTENDANCE'
    ENTITY_PAYROLL = 'PAYROLL'
    ENTITY_REPORT = 'REPORT'
    ENTITY_SYSTEM = 'SYSTEM'
    
    def __init__(self):
        """Initialize AuditLogger with database connection"""
        self.db = db
    
    def log(self, user_id, action_type, entity_type, entity_id=None, 
            description=None, old_values=None, new_values=None, 
            ip_address=None, user_agent=None):
        """
        Log an audit event.
        
        Args:
            user_id: ID of user performing the action (None for system actions)
            action_type: Type of action (CREATE, UPDATE, DELETE, etc.)
            entity_type: Type of entity (USER, EMPLOYEE, PAYROLL, etc.)
            entity_id: ID of the affected entity
            description: Human-readable description of the action
            old_values: Dictionary of old values (will be JSON encoded)
            new_values: Dictionary of new values (will be JSON encoded)
            ip_address: IP address of the user
            user_agent: User agent string
            
        Returns:
            Log ID if successful, None otherwise
        """
        # Convert dictionaries to JSON strings
        old_json = json.dumps(old_values) if old_values else None
        new_json = json.dumps(new_values) if new_values else None
        
        query = """
            INSERT INTO audit_log (
                user_id, action_type, entity_type, entity_id,
                action_description, old_values, new_values,
                ip_address, user_agent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            user_id,
            action_type,
            entity_type,
            entity_id,
            description,
            old_json,
            new_json,
            ip_address,
            user_agent
        )
        
        return self.db.execute_insert(query, params)
    
    def log_user_action(self, user_id, action_type, entity_type, entity_id=None,
                       description=None, old_values=None, new_values=None):
        """
        Log a user action (simplified method).
        
        Args:
            user_id: ID of user performing the action
            action_type: Type of action
            entity_type: Type of entity
            entity_id: ID of the affected entity
            description: Description of the action
            old_values: Old values dictionary
            new_values: New values dictionary
            
        Returns:
            Log ID if successful, None otherwise
        """
        return self.log(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=old_values,
            new_values=new_values
        )
    
    def get_logs(self, user_id=None, action_type=None, entity_type=None,
                 entity_id=None, start_date=None, end_date=None, limit=100):
        """
        Retrieve audit logs with filters.
        
        Args:
            user_id: Filter by user ID
            action_type: Filter by action type
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of records to return
            
        Returns:
            List of audit log records
        """
        query = """
            SELECT 
                al.*,
                u.username,
                u.full_name as user_name
            FROM audit_log al
            LEFT JOIN users u ON al.user_id = u.user_id
            WHERE 1=1
        """
        params = []
        
        if user_id:
            query += " AND al.user_id = %s"
            params.append(user_id)
        
        if action_type:
            query += " AND al.action_type = %s"
            params.append(action_type)
        
        if entity_type:
            query += " AND al.entity_type = %s"
            params.append(entity_type)
        
        if entity_id:
            query += " AND al.entity_id = %s"
            params.append(entity_id)
        
        if start_date:
            query += " AND DATE(al.created_at) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(al.created_at) <= %s"
            params.append(end_date)
        
        query += " ORDER BY al.created_at DESC LIMIT %s"
        params.append(limit)
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def get_logs_by_date_range(self, start_date, end_date, limit=500):
        """
        Get logs within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            limit: Maximum records
            
        Returns:
            List of audit log records
        """
        return self.get_logs(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def get_user_activity(self, user_id, limit=50):
        """
        Get activity logs for a specific user.
        
        Args:
            user_id: ID of user
            limit: Maximum records
            
        Returns:
            List of audit log records
        """
        return self.get_logs(user_id=user_id, limit=limit)
    
    def get_entity_history(self, entity_type, entity_id, limit=50):
        """
        Get change history for a specific entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            limit: Maximum records
            
        Returns:
            List of audit log records
        """
        return self.get_logs(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        )
    
    def get_recent_logs(self, limit=50):
        """
        Get most recent audit logs.
        
        Args:
            limit: Maximum records
            
        Returns:
            List of recent audit log records
        """
        return self.get_logs(limit=limit)
    
    def get_log_statistics(self, start_date=None, end_date=None):
        """
        Get audit log statistics.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Dictionary with statistics
        """
        where_clause = "WHERE 1=1"
        params = []
        
        if start_date:
            where_clause += " AND DATE(created_at) >= %s"
            params.append(start_date)
        
        if end_date:
            where_clause += " AND DATE(created_at) <= %s"
            params.append(end_date)
        
        query = f"""
            SELECT 
                COUNT(*) as total_logs,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(CASE WHEN action_type = 'CREATE' THEN 1 END) as creates,
                COUNT(CASE WHEN action_type = 'UPDATE' THEN 1 END) as updates,
                COUNT(CASE WHEN action_type = 'DELETE' THEN 1 END) as deletes,
                COUNT(CASE WHEN action_type = 'LOGIN' THEN 1 END) as logins,
                COUNT(CASE WHEN entity_type = 'EMPLOYEE' THEN 1 END) as employee_actions,
                COUNT(CASE WHEN entity_type = 'PAYROLL' THEN 1 END) as payroll_actions,
                COUNT(CASE WHEN entity_type = 'USER' THEN 1 END) as user_actions
            FROM audit_log
            {where_clause}
        """
        
        result = self.db.execute_query(query, tuple(params) if params else None, fetch_one=True)
        
        if result:
            return {
                'total_logs': result.get('total_logs', 0) or 0,
                'unique_users': result.get('unique_users', 0) or 0,
                'creates': result.get('creates', 0) or 0,
                'updates': result.get('updates', 0) or 0,
                'deletes': result.get('deletes', 0) or 0,
                'logins': result.get('logins', 0) or 0,
                'employee_actions': result.get('employee_actions', 0) or 0,
                'payroll_actions': result.get('payroll_actions', 0) or 0,
                'user_actions': result.get('user_actions', 0) or 0
            }
        
        return {
            'total_logs': 0, 'unique_users': 0, 'creates': 0, 'updates': 0,
            'deletes': 0, 'logins': 0, 'employee_actions': 0,
            'payroll_actions': 0, 'user_actions': 0
        }
    
    def delete_old_logs(self, days_to_keep=90):
        """
        Delete audit logs older than specified days.
        Use with caution - this permanently deletes logs.
        
        Args:
            days_to_keep: Number of days to keep logs
            
        Returns:
            Number of deleted records
        """
        query = """
            DELETE FROM audit_log
            WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        return self.db.execute_update(query, (days_to_keep,))


# Create a global audit logger instance
audit_logger = AuditLogger()

