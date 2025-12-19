"""
SwiftPay Employee Management Module
Handles CRUD operations for employees
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import db
from modules.audit_log import audit_logger, AuditLogger


class EmployeeManager:
    """
    Manages employee records including CRUD operations.
    """
    
    def __init__(self):
        """Initialize EmployeeManager with database connection"""
        self.db = db
    
    def generate_employee_code(self):
        """
        Generate next employee code.
        Format: EMP001, EMP002, etc.
        
        Returns:
            Generated employee code string
        """
        query = """
            SELECT employee_code FROM employees 
            ORDER BY employee_id DESC 
            LIMIT 1
        """
        result = self.db.execute_query(query, fetch_one=True)
        
        if result and result.get('employee_code'):
            last_code = result['employee_code']
            # Extract number from code (e.g., EMP001 -> 1)
            try:
                num = int(last_code.replace('EMP', '')) + 1
            except ValueError:
                num = 1
        else:
            num = 1
        
        return f"EMP{num:03d}"
    
    def create_employee(self, employee_data, user_id=None):
        """
        Create a new employee record.
        
        Args:
            employee_data: Dictionary with employee information
                - first_name (required)
                - last_name (required)
                - position (required)
                - rate_per_hour (required)
                - email, phone, address, department (optional)
                - daily_rate, allowance (optional)
                - sss_deduction, philhealth_deduction, pagibig_deduction (optional)
                - date_hired (optional)
            user_id: ID of user performing the action (for audit log)
                
        Returns:
            New employee ID if successful, None otherwise
        """
        employee_code = employee_data.get('employee_code') or self.generate_employee_code()
        
        query = """
            INSERT INTO employees (
                employee_code, first_name, last_name, email, phone, address,
                position, department, rate_per_hour, daily_rate, allowance,
                sss_deduction, philhealth_deduction, pagibig_deduction, tax_deduction,
                status, date_hired
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        # Calculate daily rate if not provided (8 hours/day)
        rate_per_hour = float(employee_data.get('rate_per_hour', 0))
        daily_rate = employee_data.get('daily_rate') or (rate_per_hour * 8)
        
        params = (
            employee_code,
            employee_data.get('first_name', ''),
            employee_data.get('last_name', ''),
            employee_data.get('email', ''),
            employee_data.get('phone', ''),
            employee_data.get('address', ''),
            employee_data.get('position', ''),
            employee_data.get('department', ''),
            rate_per_hour,
            daily_rate,
            float(employee_data.get('allowance', 0)),
            float(employee_data.get('sss_deduction', 0)),
            float(employee_data.get('philhealth_deduction', 0)),
            float(employee_data.get('pagibig_deduction', 0)),
            float(employee_data.get('tax_deduction', 0)),
            employee_data.get('status', 'Active'),
            employee_data.get('date_hired') or datetime.now().date()
        )
        
        employee_id = self.db.execute_insert(query, params)
        
        # Log employee creation
        if employee_id and user_id:
            employee_code = employee_data.get('employee_code') or self.generate_employee_code()
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_CREATE,
                entity_type=AuditLogger.ENTITY_EMPLOYEE,
                entity_id=employee_id,
                description=f"Created employee '{employee_data.get('first_name')} {employee_data.get('last_name')}' ({employee_code})",
                new_values={
                    'employee_code': employee_code,
                    'first_name': employee_data.get('first_name'),
                    'last_name': employee_data.get('last_name'),
                    'position': employee_data.get('position')
                }
            )
        
        return employee_id
    
    def update_employee(self, employee_id, employee_data, user_id=None):
        """
        Update an existing employee record.
        
        Args:
            employee_id: ID of employee to update
            employee_data: Dictionary with fields to update
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Number of rows affected
        """
        allowed_fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'position', 'department', 'rate_per_hour', 'daily_rate', 'allowance',
            'sss_deduction', 'philhealth_deduction', 'pagibig_deduction', 'tax_deduction',
            'status', 'date_hired'
        ]
        
        updates = []
        params = []
        
        for field in allowed_fields:
            if field in employee_data:
                updates.append(f"{field} = %s")
                params.append(employee_data[field])
        
        if not updates:
            return 0
        
        params.append(employee_id)
        query = f"UPDATE employees SET {', '.join(updates)} WHERE employee_id = %s"
        
        # Get old values for audit log
        old_employee = self.get_employee_by_id(employee_id)
        old_values = {}
        if old_employee:
            for field in employee_data.keys():
                if field in old_employee:
                    old_values[field] = old_employee[field]
        
        result = self.db.execute_update(query, tuple(params))
        
        # Log employee update
        if result > 0 and user_id:
            employee = self.get_employee_by_id(employee_id)
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_UPDATE,
                entity_type=AuditLogger.ENTITY_EMPLOYEE,
                entity_id=employee_id,
                description=f"Updated employee '{employee.get('first_name') if employee else 'Unknown'} {employee.get('last_name') if employee else ''}'",
                old_values=old_values if old_values else None,
                new_values=employee_data
            )
        
        return result
    
    def delete_employee(self, employee_id, hard_delete=False, user_id=None):
        """
        Delete an employee record.
        
        Args:
            employee_id: ID of employee to delete
            hard_delete: If True, permanently delete; else soft delete
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Number of rows affected
        """
        # Get employee info before deletion
        employee = self.get_employee_by_id(employee_id)
        
        if hard_delete:
            query = "DELETE FROM employees WHERE employee_id = %s"
        else:
            query = "UPDATE employees SET status = 'Inactive' WHERE employee_id = %s"
        
        result = self.db.execute_update(query, (employee_id,))
        
        # Log employee deletion
        if result > 0 and user_id and employee:
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_DELETE,
                entity_type=AuditLogger.ENTITY_EMPLOYEE,
                entity_id=employee_id,
                description=f"{'Permanently deleted' if hard_delete else 'Deleted'} employee '{employee.get('first_name')} {employee.get('last_name')}' ({employee.get('employee_code')})",
                old_values={
                    'employee_code': employee.get('employee_code'),
                    'first_name': employee.get('first_name'),
                    'last_name': employee.get('last_name'),
                    'status': employee.get('status')
                }
            )
        
        return result
    
    def get_employee_by_id(self, employee_id):
        """
        Get employee by ID.
        
        Args:
            employee_id: ID of employee
            
        Returns:
            Employee dictionary or None
        """
        query = "SELECT * FROM employees WHERE employee_id = %s"
        return self.db.execute_query(query, (employee_id,), fetch_one=True)
    
    def get_employee_by_code(self, employee_code):
        """
        Get employee by employee code.
        
        Args:
            employee_code: Employee code (e.g., EMP001)
            
        Returns:
            Employee dictionary or None
        """
        query = "SELECT * FROM employees WHERE employee_code = %s"
        return self.db.execute_query(query, (employee_code,), fetch_one=True)
    
    def get_all_employees(self, status_filter=None, search_term=None):
        """
        Get all employees with optional filters.
        
        Args:
            status_filter: Filter by status ('Active', 'Inactive', or None for all)
            search_term: Search in name, code, position, department
            
        Returns:
            List of employee dictionaries
        """
        query = """
            SELECT 
                employee_id, employee_code, first_name, last_name,
                CONCAT(first_name, ' ', last_name) AS full_name,
                email, phone, address, position, department,
                rate_per_hour, daily_rate, allowance,
                sss_deduction, philhealth_deduction, pagibig_deduction, tax_deduction,
                status, date_hired, created_at
            FROM employees
            WHERE 1=1
        """
        params = []
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        
        if search_term:
            query += """ AND (
                first_name LIKE %s OR 
                last_name LIKE %s OR 
                employee_code LIKE %s OR 
                position LIKE %s OR 
                department LIKE %s
            )"""
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern] * 5)
        
        query += " ORDER BY last_name, first_name"
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    def get_active_employees(self):
        """
        Get all active employees.
        
        Returns:
            List of active employee dictionaries
        """
        return self.get_all_employees(status_filter='Active')
    
    def get_employee_count(self, status_filter=None):
        """
        Get count of employees.
        
        Args:
            status_filter: Filter by status
            
        Returns:
            Employee count
        """
        if status_filter:
            query = "SELECT COUNT(*) as count FROM employees WHERE status = %s"
            result = self.db.execute_query(query, (status_filter,), fetch_one=True)
        else:
            query = "SELECT COUNT(*) as count FROM employees"
            result = self.db.execute_query(query, fetch_one=True)
        
        return result.get('count', 0) if result else 0
    
    def get_employees_by_department(self, department):
        """
        Get employees in a specific department.
        
        Args:
            department: Department name
            
        Returns:
            List of employees in department
        """
        query = """
            SELECT * FROM employees 
            WHERE department = %s AND status = 'Active'
            ORDER BY last_name, first_name
        """
        return self.db.execute_query(query, (department,))
    
    def get_departments(self):
        """
        Get list of all departments.
        
        Returns:
            List of department names
        """
        query = """
            SELECT DISTINCT department FROM employees 
            WHERE department IS NOT NULL AND department != ''
            ORDER BY department
        """
        results = self.db.execute_query(query)
        return [r['department'] for r in results] if results else []
    
    def get_positions(self):
        """
        Get list of all positions.
        
        Returns:
            List of position names
        """
        query = """
            SELECT DISTINCT position FROM employees 
            WHERE position IS NOT NULL AND position != ''
            ORDER BY position
        """
        results = self.db.execute_query(query)
        return [r['position'] for r in results] if results else []
    
    def validate_employee_data(self, data, is_update=False):
        """
        Validate employee data before save.
        
        Args:
            data: Employee data dictionary
            is_update: If True, some fields are optional
            
        Returns:
            Tuple (is_valid, error_message)
        """
        errors = []
        
        if not is_update:
            if not data.get('first_name'):
                errors.append("First name is required")
            if not data.get('last_name'):
                errors.append("Last name is required")
            if not data.get('position'):
                errors.append("Position is required")
            if not data.get('rate_per_hour'):
                errors.append("Rate per hour is required")
        
        # Validate numeric fields
        numeric_fields = [
            'rate_per_hour', 'daily_rate', 'allowance',
            'sss_deduction', 'philhealth_deduction', 'pagibig_deduction', 'tax_deduction'
        ]
        
        for field in numeric_fields:
            if field in data:
                try:
                    value = float(data[field])
                    if value < 0:
                        errors.append(f"{field.replace('_', ' ').title()} cannot be negative")
                except (ValueError, TypeError):
                    errors.append(f"{field.replace('_', ' ').title()} must be a number")
        
        # Validate email format if provided
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("Invalid email format")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, None


# Create a global employee manager instance
employee_manager = EmployeeManager()

