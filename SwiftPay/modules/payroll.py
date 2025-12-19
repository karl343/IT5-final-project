"""
SwiftPay Payroll Computation Module
Handles payroll calculation, generation, and management
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import db
from modules.audit_log import audit_logger, AuditLogger


class PayrollManager:
    """
    Manages payroll computation, generation, and reporting.
    Implements all payroll formulas and calculations.
    """
    
    # Payroll configuration
    OVERTIME_MULTIPLIER = Decimal('1.25')
    STANDARD_HOURS_PER_DAY = 8
    WORKING_DAYS_PER_MONTH = 22
    
    def __init__(self):
        """Initialize PayrollManager with database connection"""
        self.db = db
    
    def calculate_basic_pay(self, hours_worked, rate_per_hour):
        """
        Calculate basic pay from hours worked.
        Formula: BasicPay = TotalHours × RatePerHour
        
        Args:
            hours_worked: Total regular hours worked
            rate_per_hour: Hourly rate
            
        Returns:
            Basic pay amount
        """
        return Decimal(str(hours_worked)) * Decimal(str(rate_per_hour))
    
    def calculate_overtime_pay(self, overtime_hours, rate_per_hour):
        """
        Calculate overtime pay.
        Formula: OTPay = OTHours × (RatePerHour × 1.25)
        
        Args:
            overtime_hours: Total overtime hours
            rate_per_hour: Regular hourly rate
            
        Returns:
            Overtime pay amount
        """
        ot_rate = Decimal(str(rate_per_hour)) * self.OVERTIME_MULTIPLIER
        return Decimal(str(overtime_hours)) * ot_rate
    
    def calculate_late_deduction(self, late_minutes, rate_per_hour):
        """
        Calculate late deduction.
        Formula: LateDeduction = LateMinutes × (RatePerHour / 60)
        
        Args:
            late_minutes: Total minutes late
            rate_per_hour: Hourly rate
            
        Returns:
            Late deduction amount
        """
        minute_rate = Decimal(str(rate_per_hour)) / Decimal('60')
        return Decimal(str(late_minutes)) * minute_rate
    
    def calculate_absence_deduction(self, absences, daily_rate):
        """
        Calculate absence deduction.
        Formula: AbsenceDeduction = DailyRate × Absences
        
        Args:
            absences: Number of absent days
            daily_rate: Daily rate of employee
            
        Returns:
            Absence deduction amount
        """
        return Decimal(str(absences)) * Decimal(str(daily_rate))
    
    def calculate_employee_payroll(self, employee_id, start_date, end_date):
        """
        Calculate payroll for a single employee.
        
        Args:
            employee_id: ID of employee
            start_date: Payroll period start
            end_date: Payroll period end
            
        Returns:
            Dictionary with all payroll details
        """
        # Get employee information
        emp_query = "SELECT * FROM employees WHERE employee_id = %s"
        employee = self.db.execute_query(emp_query, (employee_id,), fetch_one=True)
        
        if not employee:
            return None
        
        # Get attendance summary
        att_query = """
            SELECT 
                COUNT(CASE WHEN status = 'Present' THEN 1 END) as days_present,
                COUNT(CASE WHEN status = 'Absent' THEN 1 END) as days_absent,
                COUNT(CASE WHEN status = 'Half-Day' THEN 1 END) as days_halfday,
                COALESCE(SUM(hours_worked), 0) as total_hours,
                COALESCE(SUM(overtime_hours), 0) as overtime_hours,
                COALESCE(SUM(late_minutes), 0) as total_late_minutes
            FROM attendance
            WHERE employee_id = %s 
              AND attendance_date BETWEEN %s AND %s
              AND status IN ('Present', 'Half-Day', 'Absent')
        """
        attendance = self.db.execute_query(att_query, (employee_id, start_date, end_date), fetch_one=True)
        
        # Extract values
        rate_per_hour = Decimal(str(employee.get('rate_per_hour', 0)))
        daily_rate = Decimal(str(employee.get('daily_rate', 0)))
        allowance = Decimal(str(employee.get('allowance', 0)))
        
        days_worked = (attendance.get('days_present', 0) or 0) + (attendance.get('days_halfday', 0) or 0) * Decimal('0.5')
        hours_worked = Decimal(str(attendance.get('total_hours', 0) or 0))
        overtime_hours = Decimal(str(attendance.get('overtime_hours', 0) or 0))
        late_minutes = attendance.get('total_late_minutes', 0) or 0
        absences = attendance.get('days_absent', 0) or 0
        
        # Calculate pays
        basic_pay = self.calculate_basic_pay(hours_worked, rate_per_hour)
        overtime_pay = self.calculate_overtime_pay(overtime_hours, rate_per_hour)
        
        # Calculate gross pay
        gross_pay = basic_pay + overtime_pay + allowance
        
        # Calculate deductions
        sss = Decimal(str(employee.get('sss_deduction', 0)))
        philhealth = Decimal(str(employee.get('philhealth_deduction', 0)))
        pagibig = Decimal(str(employee.get('pagibig_deduction', 0)))
        tax = Decimal(str(employee.get('tax_deduction', 0)))
        late_deduction = self.calculate_late_deduction(late_minutes, rate_per_hour)
        absence_deduction = self.calculate_absence_deduction(absences, daily_rate)
        
        total_deductions = sss + philhealth + pagibig + tax + late_deduction + absence_deduction
        
        # Calculate net pay
        net_pay = gross_pay - total_deductions
        
        return {
            'employee_id': employee_id,
            'employee_code': employee.get('employee_code'),
            'employee_name': f"{employee.get('first_name')} {employee.get('last_name')}",
            'position': employee.get('position'),
            'department': employee.get('department'),
            'days_worked': float(days_worked),
            'hours_worked': float(hours_worked),
            'overtime_hours': float(overtime_hours),
            'late_minutes': late_minutes,
            'absences': absences,
            'rate_per_hour': float(rate_per_hour),
            'daily_rate': float(daily_rate),
            'basic_pay': float(basic_pay.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'overtime_pay': float(overtime_pay.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'allowance': float(allowance),
            'gross_pay': float(gross_pay.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'sss_deduction': float(sss),
            'philhealth_deduction': float(philhealth),
            'pagibig_deduction': float(pagibig),
            'tax_deduction': float(tax),
            'late_deduction': float(late_deduction.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'absence_deduction': float(absence_deduction.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'total_deductions': float(total_deductions.quantize(Decimal('0.01'), ROUND_HALF_UP)),
            'net_pay': float(net_pay.quantize(Decimal('0.01'), ROUND_HALF_UP))
        }
    
    def generate_payroll(self, start_date, end_date, payroll_period=None, processed_by=None):
        """
        Generate payroll for all active employees.
        
        Args:
            start_date: Payroll period start
            end_date: Payroll period end
            payroll_period: Period description (e.g., "January 2024 - Period 1")
            processed_by: User ID who processed the payroll
            
        Returns:
            Payroll ID if successful, None otherwise
        """
        if not payroll_period:
            payroll_period = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        
        # Get all active employees
        emp_query = "SELECT employee_id FROM employees WHERE status = 'Active'"
        employees = self.db.execute_query(emp_query)
        
        if not employees:
            return None
        
        # Create payroll header
        header_query = """
            INSERT INTO payroll (payroll_period, start_date, end_date, status, processed_by, processed_at)
            VALUES (%s, %s, %s, 'Draft', %s, NOW())
        """
        payroll_id = self.db.execute_insert(header_query, (payroll_period, start_date, end_date, processed_by))
        
        if not payroll_id:
            return None
        
        # Calculate and insert payroll details for each employee
        total_employees = 0
        total_gross = Decimal('0')
        total_deductions = Decimal('0')
        total_net = Decimal('0')
        
        for emp in employees:
            payroll_data = self.calculate_employee_payroll(emp['employee_id'], start_date, end_date)
            
            if payroll_data:
                detail_query = """
                    INSERT INTO payroll_details (
                        payroll_id, employee_id, days_worked, hours_worked, overtime_hours,
                        late_minutes, absences, basic_pay, overtime_pay, allowance, gross_pay,
                        sss_deduction, philhealth_deduction, pagibig_deduction, tax_deduction,
                        late_deduction, absence_deduction, total_deductions, net_pay
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                params = (
                    payroll_id,
                    payroll_data['employee_id'],
                    payroll_data['days_worked'],
                    payroll_data['hours_worked'],
                    payroll_data['overtime_hours'],
                    payroll_data['late_minutes'],
                    payroll_data['absences'],
                    payroll_data['basic_pay'],
                    payroll_data['overtime_pay'],
                    payroll_data['allowance'],
                    payroll_data['gross_pay'],
                    payroll_data['sss_deduction'],
                    payroll_data['philhealth_deduction'],
                    payroll_data['pagibig_deduction'],
                    payroll_data['tax_deduction'],
                    payroll_data['late_deduction'],
                    payroll_data['absence_deduction'],
                    payroll_data['total_deductions'],
                    payroll_data['net_pay']
                )
                
                self.db.execute_insert(detail_query, params)
                
                total_employees += 1
                total_gross += Decimal(str(payroll_data['gross_pay']))
                total_deductions += Decimal(str(payroll_data['total_deductions']))
                total_net += Decimal(str(payroll_data['net_pay']))
        
        # Update payroll header with totals
        update_query = """
            UPDATE payroll 
            SET total_employees = %s, total_gross_pay = %s, 
                total_deductions = %s, total_net_pay = %s
            WHERE payroll_id = %s
        """
        self.db.execute_update(update_query, (
            total_employees, 
            float(total_gross), 
            float(total_deductions), 
            float(total_net),
            payroll_id
        ))
        
        # Log payroll generation
        if payroll_id and processed_by:
            audit_logger.log_user_action(
                user_id=processed_by,
                action_type=AuditLogger.ACTION_GENERATE,
                entity_type=AuditLogger.ENTITY_PAYROLL,
                entity_id=payroll_id,
                description=f"Generated payroll for period '{payroll_period}' ({total_employees} employees, ${float(total_net):,.2f} total)",
                new_values={
                    'payroll_period': payroll_period,
                    'start_date': str(start_date),
                    'end_date': str(end_date),
                    'total_employees': total_employees,
                    'total_net_pay': float(total_net)
                }
            )
        
        return payroll_id
    
    def get_payroll_by_id(self, payroll_id):
        """
        Get payroll header by ID.
        
        Args:
            payroll_id: ID of payroll
            
        Returns:
            Payroll dictionary or None
        """
        query = """
            SELECT p.*, u.full_name as processed_by_name
            FROM payroll p
            LEFT JOIN users u ON p.processed_by = u.user_id
            WHERE p.payroll_id = %s
        """
        return self.db.execute_query(query, (payroll_id,), fetch_one=True)
    
    def get_payroll_details(self, payroll_id):
        """
        Get payroll details for a specific payroll.
        
        Args:
            payroll_id: ID of payroll
            
        Returns:
            List of payroll detail records
        """
        query = """
            SELECT pd.*, e.employee_code, e.first_name, e.last_name,
                   CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                   e.position, e.department
            FROM payroll_details pd
            JOIN employees e ON pd.employee_id = e.employee_id
            WHERE pd.payroll_id = %s
            ORDER BY e.last_name, e.first_name
        """
        return self.db.execute_query(query, (payroll_id,))
    
    def get_employee_payslip(self, payroll_id, employee_id):
        """
        Get payslip data for specific employee in a payroll.
        
        Args:
            payroll_id: ID of payroll
            employee_id: ID of employee
            
        Returns:
            Payslip dictionary or None
        """
        query = """
            SELECT pd.*, p.payroll_period, p.start_date, p.end_date,
                   e.employee_code, e.first_name, e.last_name,
                   CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                   e.position, e.department, e.rate_per_hour, e.daily_rate
            FROM payroll_details pd
            JOIN payroll p ON pd.payroll_id = p.payroll_id
            JOIN employees e ON pd.employee_id = e.employee_id
            WHERE pd.payroll_id = %s AND pd.employee_id = %s
        """
        return self.db.execute_query(query, (payroll_id, employee_id), fetch_one=True)
    
    def get_all_payrolls(self, status_filter=None, limit=None):
        """
        Get all payroll records.
        
        Args:
            status_filter: Filter by status
            limit: Maximum records to return (None for all)
            
        Returns:
            List of payroll records
        """
        if status_filter:
            if limit:
                query = """
                    SELECT p.*, u.full_name as processed_by_name
                    FROM payroll p
                    LEFT JOIN users u ON p.processed_by = u.user_id
                    WHERE p.status = %s
                    ORDER BY p.created_at DESC
                    LIMIT %s
                """
                return self.db.execute_query(query, (status_filter, limit))
            else:
                query = """
                    SELECT p.*, u.full_name as processed_by_name
                    FROM payroll p
                    LEFT JOIN users u ON p.processed_by = u.user_id
                    WHERE p.status = %s
                    ORDER BY p.created_at DESC
                """
                return self.db.execute_query(query, (status_filter,))
        else:
            if limit:
                query = """
                    SELECT p.*, u.full_name as processed_by_name
                    FROM payroll p
                    LEFT JOIN users u ON p.processed_by = u.user_id
                    ORDER BY p.created_at DESC
                    LIMIT %s
                """
                return self.db.execute_query(query, (limit,))
            else:
                query = """
                    SELECT p.*, u.full_name as processed_by_name
                    FROM payroll p
                    LEFT JOIN users u ON p.processed_by = u.user_id
                    ORDER BY p.created_at DESC
                """
                return self.db.execute_query(query)
    
    def update_payroll_status(self, payroll_id, status, user_id=None):
        """
        Update payroll status.
        
        Args:
            payroll_id: ID of payroll
            status: New status (Draft, Processed, Approved, Paid)
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Number of rows affected
        """
        valid_statuses = ['Draft', 'Processed', 'Approved', 'Paid']
        if status not in valid_statuses:
            return 0
        
        # Get old status
        payroll = self.get_payroll_by_id(payroll_id)
        old_status = payroll.get('status') if payroll else None
        
        result = self.db.execute_update(
            "UPDATE payroll SET status = %s WHERE payroll_id = %s",
            (status, payroll_id)
        )
        
        # Log status change
        if result > 0 and user_id and payroll:
            action_type = AuditLogger.ACTION_APPROVE if status == 'Approved' else AuditLogger.ACTION_UPDATE
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=action_type,
                entity_type=AuditLogger.ENTITY_PAYROLL,
                entity_id=payroll_id,
                description=f"Updated payroll status from '{old_status}' to '{status}' for period '{payroll.get('payroll_period')}'",
                old_values={'status': old_status},
                new_values={'status': status}
            )
        
        return result
    
    def delete_payroll(self, payroll_id, user_id=None):
        """
        Delete payroll and its details.
        
        Args:
            payroll_id: ID of payroll to delete
            user_id: ID of user performing the action (for audit log)
            
        Returns:
            Number of rows affected
        """
        # Get payroll info before deletion
        payroll = self.get_payroll_by_id(payroll_id)
        
        # Details will be cascade deleted
        result = self.db.execute_update(
            "DELETE FROM payroll WHERE payroll_id = %s",
            (payroll_id,)
        )
        
        # Log payroll deletion
        if result > 0 and user_id and payroll:
            audit_logger.log_user_action(
                user_id=user_id,
                action_type=AuditLogger.ACTION_DELETE,
                entity_type=AuditLogger.ENTITY_PAYROLL,
                entity_id=payroll_id,
                description=f"Deleted payroll for period '{payroll.get('payroll_period')}'",
                old_values={
                    'payroll_period': payroll.get('payroll_period'),
                    'status': payroll.get('status'),
                    'total_net_pay': float(payroll.get('total_net_pay', 0))
                }
            )
        
        return result
    
    def get_employee_payroll_history(self, employee_id, limit=12):
        """
        Get payroll history for an employee.
        
        Args:
            employee_id: ID of employee
            limit: Maximum records to return
            
        Returns:
            List of payroll history records
        """
        query = """
            SELECT pd.*, p.payroll_period, p.start_date, p.end_date, p.status
            FROM payroll_details pd
            JOIN payroll p ON pd.payroll_id = p.payroll_id
            WHERE pd.employee_id = %s
            ORDER BY p.end_date DESC
            LIMIT %s
        """
        return self.db.execute_query(query, (employee_id, limit))
    
    def get_payroll_summary(self, year=None, month=None):
        """
        Get payroll summary statistics.
        
        Args:
            year: Filter by year
            month: Filter by month
            
        Returns:
            Summary statistics dictionary
        """
        where_clause = "WHERE 1=1"
        params = []
        
        if year:
            where_clause += " AND YEAR(p.start_date) = %s"
            params.append(year)
        if month:
            where_clause += " AND MONTH(p.start_date) = %s"
            params.append(month)
        
        query = f"""
            SELECT 
                COUNT(DISTINCT p.payroll_id) as total_payrolls,
                SUM(p.total_employees) as total_employee_payments,
                SUM(p.total_gross_pay) as total_gross,
                SUM(p.total_deductions) as total_deductions,
                SUM(p.total_net_pay) as total_net
            FROM payroll p
            {where_clause}
            AND p.status IN ('Paid', 'Approved', 'Processed')
        """
        
        result = self.db.execute_query(query, tuple(params) if params else None, fetch_one=True)
        
        return {
            'total_payrolls': result.get('total_payrolls', 0) or 0,
            'total_employee_payments': result.get('total_employee_payments', 0) or 0,
            'total_gross': float(result.get('total_gross', 0) or 0),
            'total_deductions': float(result.get('total_deductions', 0) or 0),
            'total_net': float(result.get('total_net', 0) or 0)
        }


# Create a global payroll manager instance
payroll_manager = PayrollManager()

