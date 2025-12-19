"""
SwiftPay Attendance Management Module
Handles time-in/out, attendance tracking, and calculations
"""

import sys
import os
from datetime import datetime, timedelta, time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import db
from modules.audit_log import audit_logger, AuditLogger


class AttendanceManager:
    """
    Manages employee attendance records including time-in/out,
    hours calculation, and attendance reporting.
    """
    
    # Standard work hours configuration
    STANDARD_TIME_IN = time(8, 0)      # 8:00 AM
    STANDARD_TIME_OUT = time(17, 0)    # 5:00 PM
    STANDARD_HOURS = 8                  # Standard work hours per day
    LUNCH_BREAK_HOURS = 1               # Lunch break hours
    OVERTIME_MULTIPLIER = 1.25          # OT rate multiplier
    
    def __init__(self):
        """Initialize AttendanceManager with database connection"""
        self.db = db
    
    def time_in(self, employee_id, time_in=None, date=None, user_id=None):
        """
        Record employee time-in.
        
        Args:
            employee_id: ID of employee
            time_in: Time of arrival (defaults to current time)
            date: Date of attendance (defaults to today)
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Attendance record ID if successful, None otherwise
        """
        if time_in is None:
            time_in = datetime.now().time()
        if date is None:
            date = datetime.now().date()
        
        # Check if already timed in today
        existing = self.get_attendance(employee_id, date)
        if existing and existing.get('time_in'):
            return None  # Already timed in
        
        # Calculate late minutes
        late_minutes = self.calculate_late_minutes(time_in)
        
        if existing:
            # Update existing record
            query = """
                UPDATE attendance 
                SET time_in = %s, late_minutes = %s, status = 'Present'
                WHERE attendance_id = %s
            """
            result = self.db.execute_update(query, (time_in, late_minutes, existing['attendance_id']))
            attendance_id = existing['attendance_id'] if result > 0 else None
        else:
            # Create new record
            query = """
                INSERT INTO attendance (employee_id, attendance_date, time_in, late_minutes, status)
                VALUES (%s, %s, %s, %s, 'Present')
            """
            attendance_id = self.db.execute_insert(query, (employee_id, date, time_in, late_minutes))
        
        # Log time-in
        if attendance_id and user_id:
            from modules.employees import employee_manager
            employee = employee_manager.get_employee_by_id(employee_id)
            employee_name = f"{employee.get('first_name')} {employee.get('last_name')}" if employee else f"Employee {employee_id}"
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_TIME_IN,
                entity_type=AuditLogger.ENTITY_ATTENDANCE,
                entity_id=attendance_id,
                description=f"Time-in recorded for {employee_name} on {date} at {time_in}",
                new_values={'time_in': str(time_in), 'date': str(date), 'late_minutes': late_minutes}
            )
        
        return attendance_id
    
    def time_out(self, employee_id, time_out=None, date=None, user_id=None):
        """
        Record employee time-out and calculate hours worked.
        
        Args:
            employee_id: ID of employee
            time_out: Time of departure (defaults to current time)
            date: Date of attendance (defaults to today)
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Updated attendance record or None
        """
        if time_out is None:
            time_out = datetime.now().time()
        if date is None:
            date = datetime.now().date()
        
        # Get existing attendance record
        attendance = self.get_attendance(employee_id, date)
        
        if not attendance or not attendance.get('time_in'):
            return None  # No time-in record
        
        if attendance.get('time_out'):
            return None  # Already timed out
        
        # Calculate hours worked and overtime
        time_in = attendance['time_in']
        time_in_date = attendance.get('attendance_date', date)
        
        if isinstance(time_in, timedelta):
            # Convert timedelta to time
            total_seconds = int(time_in.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_in = time(hours, minutes, seconds)
        
        # Pass dates to handle midnight crossing
        hours_worked, overtime_hours, undertime = self.calculate_hours(
            time_in, time_out, date_in=time_in_date, date_out=date
        )
        
        query = """
            UPDATE attendance 
            SET time_out = %s, hours_worked = %s, overtime_hours = %s, undertime_minutes = %s
            WHERE attendance_id = %s
        """
        
        result = self.db.execute_update(
            query, 
            (time_out, hours_worked, overtime_hours, undertime, attendance['attendance_id'])
        )
        
        # Log time-out
        if result > 0 and user_id:
            from modules.employees import employee_manager
            employee = employee_manager.get_employee_by_id(employee_id)
            employee_name = f"{employee.get('first_name')} {employee.get('last_name')}" if employee else f"Employee {employee_id}"
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_TIME_OUT,
                entity_type=AuditLogger.ENTITY_ATTENDANCE,
                entity_id=attendance['attendance_id'],
                description=f"Time-out recorded for {employee_name} on {date} at {time_out} ({hours_worked} hours worked)",
                new_values={'time_out': str(time_out), 'hours_worked': hours_worked, 'overtime_hours': overtime_hours}
            )
            return self.get_attendance(employee_id, date)
        return None
    
    def calculate_late_minutes(self, time_in):
        """
        Calculate late minutes based on standard time-in.
        
        Args:
            time_in: Actual time-in
            
        Returns:
            Minutes late (0 if on time or early)
        """
        if isinstance(time_in, timedelta):
            total_seconds = int(time_in.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            time_in = time(hours, minutes)
        
        standard = datetime.combine(datetime.today(), self.STANDARD_TIME_IN)
        actual = datetime.combine(datetime.today(), time_in)
        
        if actual > standard:
            diff = actual - standard
            return int(diff.total_seconds() / 60)
        return 0
    
    def calculate_hours(self, time_in, time_out, date_in=None, date_out=None):
        """
        Calculate hours worked, overtime, and undertime.
        Handles edge cases like clocking across midnight.
        
        Args:
            time_in: Time of arrival
            time_out: Time of departure
            date_in: Date of time in (defaults to today)
            date_out: Date of time out (defaults to today or tomorrow if overnight)
            
        Returns:
            Tuple (hours_worked, overtime_hours, undertime_minutes)
        """
        # Use provided dates or default to today
        if date_in is None:
            date_in = datetime.now().date()
        if date_out is None:
            date_out = datetime.now().date()
        
        # Convert to datetime for calculation
        dt_in = datetime.combine(date_in, time_in)
        dt_out = datetime.combine(date_out, time_out)
        
        # Handle overnight shifts (time_out is earlier than time_in on same day)
        # or when explicitly clocking out on next day
        if dt_out < dt_in:
            # Clock out is before clock in - must be next day
            dt_out += timedelta(days=1)
            date_out = dt_out.date()
        
        # Also handle case where time_out is very early (e.g., 00:30) and time_in is late (e.g., 23:00)
        # This indicates an overnight shift
        if time_out.hour < 6 and time_in.hour >= 18:
            # Likely overnight shift - time_out is next day
            dt_out += timedelta(days=1)
            date_out = dt_out.date()
        
        # Total time difference
        total_time = dt_out - dt_in
        total_hours = total_time.total_seconds() / 3600
        
        # Validate reasonable work hours (prevent negative or excessive hours)
        if total_hours < 0:
            total_hours = 0
        elif total_hours > 24:
            # More than 24 hours - likely data error, cap at 24
            total_hours = 24
        
        # Subtract lunch break (only if work hours > 4 hours)
        if total_hours > 4:
            work_hours = total_hours - self.LUNCH_BREAK_HOURS
        else:
            work_hours = total_hours
        work_hours = max(0, work_hours)
        
        # Calculate overtime (hours beyond standard)
        overtime_hours = max(0, work_hours - self.STANDARD_HOURS)
        regular_hours = min(work_hours, self.STANDARD_HOURS)
        
        # Calculate undertime (if worked less than standard)
        undertime_minutes = 0
        if work_hours < self.STANDARD_HOURS:
            undertime_minutes = int((self.STANDARD_HOURS - work_hours) * 60)
        
        return round(regular_hours, 2), round(overtime_hours, 2), undertime_minutes
    
    def record_absence(self, employee_id, date, remarks=None):
        """
        Record employee absence.
        
        Args:
            employee_id: ID of employee
            date: Date of absence
            remarks: Optional remarks
            
        Returns:
            Attendance record ID
        """
        # Check for existing record
        existing = self.get_attendance(employee_id, date)
        
        if existing:
            query = """
                UPDATE attendance 
                SET status = 'Absent', remarks = %s
                WHERE attendance_id = %s
            """
            self.db.execute_update(query, (remarks, existing['attendance_id']))
            return existing['attendance_id']
        else:
            query = """
                INSERT INTO attendance (employee_id, attendance_date, status, remarks)
                VALUES (%s, %s, 'Absent', %s)
            """
            return self.db.execute_insert(query, (employee_id, date, remarks))
    
    def record_leave(self, employee_id, date, remarks=None):
        """
        Record employee leave.
        
        Args:
            employee_id: ID of employee
            date: Date of leave
            remarks: Leave type/reason
            
        Returns:
            Attendance record ID
        """
        existing = self.get_attendance(employee_id, date)
        
        if existing:
            query = """
                UPDATE attendance 
                SET status = 'Leave', remarks = %s
                WHERE attendance_id = %s
            """
            self.db.execute_update(query, (remarks, existing['attendance_id']))
            return existing['attendance_id']
        else:
            query = """
                INSERT INTO attendance (employee_id, attendance_date, status, remarks)
                VALUES (%s, %s, 'Leave', %s)
            """
            return self.db.execute_insert(query, (employee_id, date, remarks))
    
    def get_attendance(self, employee_id, date):
        """
        Get attendance record for employee on specific date.
        
        Args:
            employee_id: ID of employee
            date: Date to check
            
        Returns:
            Attendance record dictionary or None
        """
        query = """
            SELECT * FROM attendance 
            WHERE employee_id = %s AND attendance_date = %s
        """
        return self.db.execute_query(query, (employee_id, date), fetch_one=True)
    
    def get_attendance_by_date_range(self, employee_id, start_date, end_date):
        """
        Get attendance records for date range.
        
        Args:
            employee_id: ID of employee (or None for all)
            start_date: Start date
            end_date: End date
            
        Returns:
            List of attendance records
        """
        if employee_id:
            query = """
                SELECT a.*, e.employee_code, e.first_name, e.last_name,
                       CONCAT(e.first_name, ' ', e.last_name) as full_name
                FROM attendance a
                JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.employee_id = %s 
                  AND a.attendance_date BETWEEN %s AND %s
                ORDER BY a.attendance_date DESC
            """
            return self.db.execute_query(query, (employee_id, start_date, end_date))
        else:
            query = """
                SELECT a.*, e.employee_code, e.first_name, e.last_name,
                       CONCAT(e.first_name, ' ', e.last_name) as full_name
                FROM attendance a
                JOIN employees e ON a.employee_id = e.employee_id
                WHERE a.attendance_date BETWEEN %s AND %s
                ORDER BY a.attendance_date DESC, e.last_name, e.first_name
            """
            return self.db.execute_query(query, (start_date, end_date))
    
    def get_attendance_summary(self, employee_id, start_date, end_date):
        """
        Get attendance summary for an employee.
        
        Args:
            employee_id: ID of employee
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with attendance statistics
        """
        query = """
            SELECT 
                COUNT(*) as total_days,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_days,
                SUM(CASE WHEN status = 'Absent' THEN 1 ELSE 0 END) as absent_days,
                SUM(CASE WHEN status = 'Leave' THEN 1 ELSE 0 END) as leave_days,
                SUM(CASE WHEN status = 'Half-Day' THEN 1 ELSE 0 END) as halfday_count,
                COALESCE(SUM(hours_worked), 0) as total_hours,
                COALESCE(SUM(overtime_hours), 0) as total_overtime,
                COALESCE(SUM(late_minutes), 0) as total_late_minutes,
                COALESCE(SUM(undertime_minutes), 0) as total_undertime_minutes
            FROM attendance
            WHERE employee_id = %s 
              AND attendance_date BETWEEN %s AND %s
        """
        
        result = self.db.execute_query(query, (employee_id, start_date, end_date), fetch_one=True)
        
        if result:
            return {
                'total_days': result.get('total_days', 0) or 0,
                'present_days': result.get('present_days', 0) or 0,
                'absent_days': result.get('absent_days', 0) or 0,
                'leave_days': result.get('leave_days', 0) or 0,
                'halfday_count': result.get('halfday_count', 0) or 0,
                'total_hours': float(result.get('total_hours', 0) or 0),
                'total_overtime': float(result.get('total_overtime', 0) or 0),
                'total_late_minutes': result.get('total_late_minutes', 0) or 0,
                'total_undertime_minutes': result.get('total_undertime_minutes', 0) or 0
            }
        
        return {
            'total_days': 0, 'present_days': 0, 'absent_days': 0,
            'leave_days': 0, 'halfday_count': 0, 'total_hours': 0,
            'total_overtime': 0, 'total_late_minutes': 0, 'total_undertime_minutes': 0
        }
    
    def get_today_attendance(self):
        """
        Get all attendance records for today.
        
        Returns:
            List of today's attendance records with employee info
        """
        today = datetime.now().date()
        
        query = """
            SELECT a.*, e.employee_code, e.first_name, e.last_name,
                   CONCAT(e.first_name, ' ', e.last_name) as full_name,
                   e.position, e.department
            FROM employees e
            LEFT JOIN attendance a ON e.employee_id = a.employee_id 
                AND a.attendance_date = %s
            WHERE e.status = 'Active'
            ORDER BY e.last_name, e.first_name
        """
        
        return self.db.execute_query(query, (today,))
    
    def get_employees_present_today(self):
        """
        Get count of employees present today.
        
        Returns:
            Number of employees present
        """
        today = datetime.now().date()
        query = """
            SELECT COUNT(*) as count FROM attendance 
            WHERE attendance_date = %s AND status = 'Present'
        """
        result = self.db.execute_query(query, (today,), fetch_one=True)
        return result.get('count', 0) if result else 0
    
    def update_attendance(self, attendance_id, data, user_id=None):
        """
        Update attendance record.
        
        Args:
            attendance_id: ID of attendance record
            data: Dictionary with fields to update
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Number of rows affected
        """
        allowed_fields = [
            'time_in', 'time_out', 'hours_worked', 'overtime_hours',
            'late_minutes', 'undertime_minutes', 'status', 'remarks'
        ]
        
        updates = []
        params = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
        
        if not updates:
            return 0
        
        params.append(attendance_id)
        query = f"UPDATE attendance SET {', '.join(updates)} WHERE attendance_id = %s"
        
        # Get old values for audit log
        old_attendance = None
        if user_id:
            query_old = "SELECT * FROM attendance WHERE attendance_id = %s"
            old_attendance = self.db.execute_query(query_old, (attendance_id,), fetch_one=True)
        
        result = self.db.execute_update(query, tuple(params))
        
        # Log attendance update
        if result > 0 and user_id and old_attendance:
            from modules.employees import employee_manager
            employee = employee_manager.get_employee_by_id(old_attendance.get('employee_id'))
            employee_name = f"{employee.get('first_name')} {employee.get('last_name')}" if employee else f"Employee {old_attendance.get('employee_id')}"
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_UPDATE,
                entity_type=AuditLogger.ENTITY_ATTENDANCE,
                entity_id=attendance_id,
                description=f"Updated attendance record for {employee_name}",
                old_values={k: str(v) for k, v in old_attendance.items() if k in data},
                new_values=data
            )
        
        return result
    
    def delete_attendance(self, attendance_id, user_id=None):
        """
        Delete attendance record.
        
        Args:
            attendance_id: ID of attendance record
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Number of rows affected
        """
        # Get attendance info before deletion
        attendance = None
        if user_id:
            attendance = self.db.execute_query(
                "SELECT * FROM attendance WHERE attendance_id = %s",
                (attendance_id,),
                fetch_one=True
            )
        
        result = self.db.execute_update(
            "DELETE FROM attendance WHERE attendance_id = %s",
            (attendance_id,)
        )
        
        # Log attendance deletion
        if result > 0 and user_id and attendance:
            from modules.employees import employee_manager
            employee = employee_manager.get_employee_by_id(attendance.get('employee_id'))
            employee_name = f"{employee.get('first_name')} {employee.get('last_name')}" if employee else f"Employee {attendance.get('employee_id')}"
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_DELETE,
                entity_type=AuditLogger.ENTITY_ATTENDANCE,
                entity_id=attendance_id,
                description=f"Deleted attendance record for {employee_name} on {attendance.get('attendance_date')}",
                old_values={'attendance_date': str(attendance.get('attendance_date')), 'status': attendance.get('status')}
            )
        
        return result
    
    def bulk_record_attendance(self, attendance_list):
        """
        Record attendance for multiple employees.
        
        Args:
            attendance_list: List of attendance dictionaries
                Each dict should have: employee_id, date, time_in, time_out
            
        Returns:
            Number of records created/updated
        """
        count = 0
        for record in attendance_list:
            employee_id = record.get('employee_id')
            date = record.get('date')
            time_in = record.get('time_in')
            time_out = record.get('time_out')
            status = record.get('status', 'Present')
            
            if employee_id and date:
                if status == 'Absent':
                    self.record_absence(employee_id, date, record.get('remarks'))
                elif status == 'Leave':
                    self.record_leave(employee_id, date, record.get('remarks'))
                else:
                    if time_in:
                        self.time_in(employee_id, time_in, date)
                    if time_out:
                        self.time_out(employee_id, time_out, date)
                count += 1
        
        return count


# Create a global attendance manager instance
attendance_manager = AttendanceManager()

