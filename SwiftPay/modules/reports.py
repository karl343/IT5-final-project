"""
SwiftPay Reports Module
Handles report generation, CSV/PDF export
"""

import sys
import os
import csv
from datetime import datetime
from io import BytesIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import db

# Try to import reportlab for PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    HAS_REPORTLAB = True
    
    # Try to register DejaVu Sans for Unicode support (peso sign)
    try:
        # Try common system font paths
        font_paths = [
            ('C:/Windows/Fonts/DejaVuSans.ttf', 'C:/Windows/Fonts/DejaVuSans-Bold.ttf'),
            ('C:/Windows/Fonts/arial.ttf', 'C:/Windows/Fonts/arialbd.ttf'),
            ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
        ]
        
        unicode_font_registered = False
        font_name = 'Helvetica'
        
        for regular_path, bold_path in font_paths:
            if os.path.exists(regular_path):
                try:
                    # Register regular font
                    if 'DejaVu' in regular_path or 'dejavu' in regular_path.lower():
                        font_name = 'DejaVuSans'
                        pdfmetrics.registerFont(TTFont('DejaVuSans', regular_path))
                        # Try to register bold if available
                        if os.path.exists(bold_path):
                            try:
                                pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_path))
                            except:
                                pass  # Bold not available, will use regular
                        unicode_font_registered = True
                        break
                    elif 'arial' in regular_path.lower():
                        font_name = 'Arial'
                        pdfmetrics.registerFont(TTFont('Arial', regular_path))
                        if os.path.exists(bold_path):
                            try:
                                pdfmetrics.registerFont(TTFont('Arial-Bold', bold_path))
                            except:
                                pass
                        unicode_font_registered = True
                        break
                except Exception as e:
                    print(f"Font registration error: {e}")
                    continue
        
        # If no system font found, use built-in Helvetica
        if not unicode_font_registered:
            UNICODE_FONT = 'Helvetica'
            UNICODE_FONT_BOLD = 'Helvetica-Bold'
        else:
            UNICODE_FONT = font_name
            # For custom fonts, use regular font name and let ReportLab handle bold
            # ReportLab can make fonts bold without needing a separate bold font file
            # Only use -Bold suffix if it's actually registered
            registered_fonts = pdfmetrics.getRegisteredFontNames()
            bold_font_name = f'{font_name}-Bold'
            if bold_font_name in registered_fonts:
                UNICODE_FONT_BOLD = bold_font_name
            else:
                # Use regular font - ReportLab will handle bold rendering
                UNICODE_FONT_BOLD = font_name
    except Exception as e:
        print(f"Font setup error: {e}")
        UNICODE_FONT = 'Helvetica'
        UNICODE_FONT_BOLD = 'Helvetica-Bold'
        
except ImportError:
    HAS_REPORTLAB = False
    UNICODE_FONT = None
    UNICODE_FONT_BOLD = None


class ReportManager:
    """
    Manages report generation and export functionality.
    Supports CSV and PDF export formats.
    """
    
    def __init__(self):
        """Initialize ReportManager with database connection"""
        self.db = db
    
    # ==================== ATTENDANCE REPORTS ====================
    
    def get_attendance_report(self, start_date, end_date, employee_id=None, department=None):
        """
        Generate attendance report data.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            employee_id: Filter by employee (optional)
            department: Filter by department (optional)
            
        Returns:
            List of attendance records
        """
        query = """
            SELECT 
                a.attendance_date,
                e.employee_code,
                CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                e.position,
                e.department,
                a.time_in,
                a.time_out,
                a.hours_worked,
                a.overtime_hours,
                a.late_minutes,
                a.status,
                a.remarks
            FROM attendance a
            JOIN employees e ON a.employee_id = e.employee_id
            WHERE a.attendance_date BETWEEN %s AND %s
        """
        params = [start_date, end_date]
        
        if employee_id:
            query += " AND a.employee_id = %s"
            params.append(employee_id)
        
        if department:
            query += " AND e.department = %s"
            params.append(department)
        
        query += " ORDER BY a.attendance_date DESC, e.last_name, e.first_name"
        
        return self.db.execute_query(query, tuple(params))
    
    def get_attendance_summary_report(self, start_date, end_date, department=None):
        """
        Generate attendance summary report by employee.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            department: Filter by department (optional)
            
        Returns:
            List of attendance summaries per employee
        """
        query = """
            SELECT 
                e.employee_code,
                CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                e.position,
                e.department,
                COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as present_days,
                COUNT(CASE WHEN a.status = 'Absent' THEN 1 END) as absent_days,
                COUNT(CASE WHEN a.status = 'Leave' THEN 1 END) as leave_days,
                COUNT(CASE WHEN a.status = 'Half-Day' THEN 1 END) as halfday_days,
                COALESCE(SUM(a.hours_worked), 0) as total_hours,
                COALESCE(SUM(a.overtime_hours), 0) as total_overtime,
                COALESCE(SUM(a.late_minutes), 0) as total_late_minutes
            FROM employees e
            LEFT JOIN attendance a ON e.employee_id = a.employee_id 
                AND a.attendance_date BETWEEN %s AND %s
            WHERE e.status = 'Active'
        """
        params = [start_date, end_date]
        
        if department:
            query += " AND e.department = %s"
            params.append(department)
        
        query += " GROUP BY e.employee_id ORDER BY e.last_name, e.first_name"
        
        return self.db.execute_query(query, tuple(params))
    
    # ==================== PAYROLL REPORTS ====================
    
    def get_payroll_report(self, payroll_id):
        """
        Generate detailed payroll report.
        
        Args:
            payroll_id: ID of payroll
            
        Returns:
            Dictionary with payroll header and details
        """
        # Get payroll header
        header_query = """
            SELECT p.*, u.full_name as processed_by_name
            FROM payroll p
            LEFT JOIN users u ON p.processed_by = u.user_id
            WHERE p.payroll_id = %s
        """
        header = self.db.execute_query(header_query, (payroll_id,), fetch_one=True)
        
        if not header:
            return None
        
        # Get payroll details
        details_query = """
            SELECT 
                pd.*,
                e.employee_code,
                CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                e.position,
                e.department
            FROM payroll_details pd
            JOIN employees e ON pd.employee_id = e.employee_id
            WHERE pd.payroll_id = %s
            ORDER BY e.last_name, e.first_name
        """
        details = self.db.execute_query(details_query, (payroll_id,))
        
        return {
            'header': header,
            'details': details
        }
    
    def get_payroll_summary_report(self, year=None, month=None):
        """
        Generate payroll summary report.
        
        Args:
            year: Filter by year
            month: Filter by month
            
        Returns:
            List of payroll summaries
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
                p.payroll_id,
                p.payroll_period,
                p.start_date,
                p.end_date,
                p.total_employees,
                p.total_gross_pay,
                p.total_deductions,
                p.total_net_pay,
                p.status,
                p.processed_at,
                u.full_name as processed_by_name
            FROM payroll p
            LEFT JOIN users u ON p.processed_by = u.user_id
            {where_clause}
            ORDER BY p.start_date DESC
        """
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    # ==================== EMPLOYEE REPORTS ====================
    
    def get_employee_list_report(self, status_filter=None, department=None):
        """
        Generate employee list report.
        
        Args:
            status_filter: Filter by status
            department: Filter by department
            
        Returns:
            List of employees
        """
        query = """
            SELECT 
                employee_code,
                CONCAT(first_name, ' ', last_name) as employee_name,
                email,
                phone,
                position,
                department,
                rate_per_hour,
                daily_rate,
                allowance,
                sss_deduction,
                philhealth_deduction,
                pagibig_deduction,
                status,
                date_hired
            FROM employees
            WHERE 1=1
        """
        params = []
        
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)
        
        if department:
            query += " AND department = %s"
            params.append(department)
        
        query += " ORDER BY last_name, first_name"
        
        return self.db.execute_query(query, tuple(params) if params else None)
    
    # ==================== CSV EXPORT ====================
    
    def export_to_csv(self, data, filename, headers=None):
        """
        Export data to CSV file.
        
        Args:
            data: List of dictionaries to export
            filename: Output file path
            headers: Column headers (optional, uses dict keys if not provided)
            
        Returns:
            Boolean indicating success
        """
        if not data:
            return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if headers:
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                else:
                    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                
                writer.writeheader()
                
                for row in data:
                    # Convert any non-string values
                    clean_row = {}
                    for key, value in row.items():
                        if headers and key not in headers:
                            continue
                        if value is None:
                            clean_row[key] = ''
                        elif isinstance(value, datetime):
                            clean_row[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            clean_row[key] = str(value)
                    writer.writerow(clean_row)
            
            return True
            
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
    
    def export_attendance_csv(self, start_date, end_date, filename, employee_id=None):
        """
        Export attendance report to CSV.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            filename: Output file path
            employee_id: Filter by employee (optional)
            
        Returns:
            Boolean indicating success
        """
        data = self.get_attendance_report(start_date, end_date, employee_id)
        
        headers = [
            'attendance_date', 'employee_code', 'employee_name', 'position',
            'department', 'time_in', 'time_out', 'hours_worked', 'overtime_hours',
            'late_minutes', 'status', 'remarks'
        ]
        
        return self.export_to_csv(data, filename, headers)
    
    def export_payroll_csv(self, payroll_id, filename):
        """
        Export payroll report to CSV.
        
        Args:
            payroll_id: ID of payroll
            filename: Output file path
            
        Returns:
            Boolean indicating success
        """
        report = self.get_payroll_report(payroll_id)
        
        if not report or not report.get('details'):
            return False
        
        headers = [
            'employee_code', 'employee_name', 'position', 'department',
            'days_worked', 'hours_worked', 'overtime_hours', 'basic_pay',
            'overtime_pay', 'allowance', 'gross_pay', 'sss_deduction',
            'philhealth_deduction', 'pagibig_deduction', 'tax_deduction',
            'late_deduction', 'absence_deduction', 'total_deductions', 'net_pay'
        ]
        
        return self.export_to_csv(report['details'], filename, headers)
    
    def export_employees_csv(self, filename, status_filter=None):
        """
        Export employee list to CSV.
        
        Args:
            filename: Output file path
            status_filter: Filter by status
            
        Returns:
            Boolean indicating success
        """
        data = self.get_employee_list_report(status_filter)
        return self.export_to_csv(data, filename)
    
    # ==================== PDF EXPORT ====================
    
    def export_to_pdf(self, title, data, headers, filename, orientation='portrait'):
        """
        Export data to PDF file.
        
        Args:
            title: Report title
            data: List of dictionaries to export
            headers: Column headers
            filename: Output file path
            orientation: 'portrait' or 'landscape'
            
        Returns:
            Boolean indicating success
        """
        if not HAS_REPORTLAB:
            print("ReportLab library not installed. Install with: pip install reportlab")
            return False
        
        if not data:
            return False
        
        try:
            pagesize = letter if orientation == 'portrait' else (letter[1], letter[0])
            doc = SimpleDocTemplate(filename, pagesize=pagesize)
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            elements.append(Paragraph(title, title_style))
            
            # Subtitle with date
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=20
            )
            elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", subtitle_style))
            
            # Build table data
            table_data = [headers]
            for row in data:
                row_data = []
                for header in headers:
                    value = row.get(header, '')
                    if value is None:
                        value = ''
                    elif isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d')
                    elif isinstance(value, float):
                        value = f"{value:,.2f}"
                    row_data.append(str(value))
                table_data.append(row_data)
            
            # Create table
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"PDF export error: {e}")
            return False
    
    def export_attendance_pdf(self, start_date, end_date, filename, employee_id=None):
        """
        Export attendance report to PDF.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            filename: Output file path
            employee_id: Filter by employee (optional)
            
        Returns:
            Boolean indicating success
        """
        data = self.get_attendance_report(start_date, end_date, employee_id)
        
        title = f"Attendance Report ({start_date} to {end_date})"
        headers = ['attendance_date', 'employee_code', 'employee_name', 
                   'time_in', 'time_out', 'hours_worked', 'status']
        
        return self.export_to_pdf(title, data, headers, filename, 'landscape')
    
    def export_payroll_pdf(self, payroll_id, filename):
        """
        Export payroll report to PDF.
        
        Args:
            payroll_id: ID of payroll
            filename: Output file path
            
        Returns:
            Boolean indicating success
        """
        report = self.get_payroll_report(payroll_id)
        
        if not report:
            return False
        
        header = report['header']
        title = f"Payroll Report: {header.get('payroll_period', 'N/A')}"
        
        headers = ['employee_code', 'employee_name', 'basic_pay', 'overtime_pay',
                   'gross_pay', 'total_deductions', 'net_pay']
        
        return self.export_to_pdf(title, report['details'], headers, filename, 'landscape')
    
    def export_payroll_summary_pdf(self, year=None, month=None, filename=None):
        """
        Export payroll summary report to PDF.
        
        Args:
            year: Filter by year
            month: Filter by month
            filename: Output file path
            
        Returns:
            Boolean indicating success
        """
        if not HAS_REPORTLAB:
            print("ReportLab not available. Cannot generate PDF.")
            return False
        
        try:
            import os
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(filename) if filename else ''
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            # Get payroll summary data
            data = self.get_payroll_summary_report(year, month)
            
            if not data:
                print("No payroll data to export")
                return False
            
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            month_name = ""
            if month:
                months = ["", "January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"]
                month_name = months[month] + " "
            
            title_text = f"Payroll Summary Report"
            if year:
                title_text += f" - {month_name}{year}"
            elif month:
                title_text += f" - {month_name}"
            
            # Use Helvetica-Bold for titles (always available, reliable)
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.HexColor('#0055FF'),
                spaceAfter=15,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'  # Use built-in bold font for reliability
            )
            elements.append(Paragraph(title_text, title_style))
            elements.append(Spacer(1, 0.15*inch))
            
            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#6B7280'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
            elements.append(Spacer(1, 0.35*inch))
            
            # Summary statistics
            total_gross = sum(float(rec.get('total_gross_pay', 0) or 0) for rec in data)
            total_deductions = sum(float(rec.get('total_deductions', 0) or 0) for rec in data)
            total_net = sum(float(rec.get('total_net_pay', 0) or 0) for rec in data)
            
            # Format amounts with peso sign - using Paragraph for better Unicode support
            # Use PHP symbol if peso sign not supported
            peso_symbol = "₱" if UNICODE_FONT == 'DejaVuSans' else "PHP "
            total_gross_str = f"{peso_symbol}{total_gross:,.2f}"
            total_deductions_str = f"{peso_symbol}{total_deductions:,.2f}"
            total_net_str = f"{peso_symbol}{total_net:,.2f}"
            
            summary_data = [
                ['Metric', 'Amount'],
                ['Total Gross Pay', total_gross_str],
                ['Total Deductions', total_deductions_str],
                ['Total Net Pay', total_net_str],
            ]
            
            summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
            font_name = 'Helvetica-Bold'  # Use built-in bold font
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0055FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 13),
                ('FONTSIZE', (0, 1), (0, 2), 11),
                ('FONTSIZE', (1, 1), (1, 2), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                ('TOPPADDING', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, 2), colors.HexColor('#F9FAFB')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8F5E9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('FONTNAME', (0, -1), (-1, -1), font_name),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#1B5E20')),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.4*inch))
            
            # Payroll details table
            table_data = [
                ['Period', 'Start Date', 'End Date', 'Employees', 'Gross Pay', 'Deductions', 'Net Pay', 'Status']
            ]
            
            # Track row colors for negative values and status
            net_pay_colors = []
            status_colors = []
            
            for rec in data:
                period = rec.get('payroll_period', 'N/A')
                start = rec.get('start_date', '')
                if hasattr(start, 'strftime'):
                    start = start.strftime('%Y-%m-%d')
                end = rec.get('end_date', '')
                if hasattr(end, 'strftime'):
                    end = end.strftime('%Y-%m-%d')
                employees = str(rec.get('total_employees', 0))
                
                # Format amounts with peso sign
                gross_val = float(rec.get('total_gross_pay', 0) or 0)
                deductions_val = float(rec.get('total_deductions', 0) or 0)
                net_val = float(rec.get('total_net_pay', 0) or 0)
                
                peso_symbol = "₱" if UNICODE_FONT == 'DejaVuSans' else "PHP "
                gross = f"{peso_symbol}{gross_val:,.2f}"
                deductions = f"{peso_symbol}{deductions_val:,.2f}"
                net = f"{peso_symbol}{net_val:,.2f}"
                
                status = rec.get('status', 'N/A')
                
                # Track colors for this row
                net_pay_colors.append(colors.HexColor('#DC2626') if net_val < 0 else colors.black)
                status_colors.append(colors.HexColor('#10B981') if status == 'Paid' else colors.HexColor('#6B7280'))
                
                table_data.append([period, str(start), str(end), employees, gross, deductions, net, status])
            
            # Create table with improved column widths
            table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 0.8*inch, 1.1*inch, 1.1*inch, 1.1*inch, 0.9*inch])
            
            # Build table style with improved formatting
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0055FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Employees column
                ('ALIGN', (4, 1), (6, -1), 'RIGHT'),  # Money columns
                ('ALIGN', (7, 1), (7, -1), 'CENTER'),  # Status column
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Use built-in bold font
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                ('TOPPADDING', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ]
            
            # Add color coding for net pay and status columns
            for i, (net_color, status_color) in enumerate(zip(net_pay_colors, status_colors)):
                row = i + 1  # +1 because row 0 is header
                table_style.append(('TEXTCOLOR', (6, row), (6, row), net_color))
                table_style.append(('TEXTCOLOR', (7, row), (7, row), status_color))
            
            table.setStyle(TableStyle(table_style))
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            # Verify file was created
            if os.path.exists(filename):
                print(f"Payroll summary PDF created successfully: {filename}")
                return True
            else:
                print(f"Error: PDF file was not created at {filename}")
                return False
                
        except PermissionError as e:
            print(f"Permission error generating payroll summary PDF: {e}")
            print(f"Make sure you have write permissions for: {filename}")
            raise  # Re-raise to be caught by UI layer
        except FileNotFoundError as e:
            print(f"Directory not found for PDF export: {e}")
            print(f"Path: {filename}")
            raise
        except Exception as e:
            import traceback
            print(f"Error generating payroll summary PDF: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise  # Re-raise to be caught by UI layer with better error handling
    
    def generate_payslip_pdf(self, payroll_id, employee_id, filename):
        """
        Generate individual payslip PDF.
        
        Args:
            payroll_id: ID of payroll
            employee_id: ID of employee
            filename: Output file path
            
        Returns:
            Boolean indicating success
        """
        if not HAS_REPORTLAB:
            print("ReportLab library not installed")
            return False
        
        # Get payslip data
        query = """
            SELECT pd.*, p.payroll_period, p.start_date, p.end_date,
                   e.employee_code, e.first_name, e.last_name,
                   CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                   e.position, e.department
            FROM payroll_details pd
            JOIN payroll p ON pd.payroll_id = p.payroll_id
            JOIN employees e ON pd.employee_id = e.employee_id
            WHERE pd.payroll_id = %s AND pd.employee_id = %s
        """
        payslip = self.db.execute_query(query, (payroll_id, employee_id), fetch_one=True)
        
        if not payslip:
            return False
        
        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Company header
            title_style = ParagraphStyle(
                'CompanyTitle',
                parent=styles['Heading1'],
                fontSize=20,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=5
            )
            elements.append(Paragraph("SwiftPay", title_style))
            elements.append(Paragraph("PAYSLIP", ParagraphStyle('Subtitle', fontSize=14, alignment=TA_CENTER, spaceAfter=20)))
            
            # Employee info
            info_data = [
                ['Employee Code:', payslip.get('employee_code', ''), 'Period:', payslip.get('payroll_period', '')],
                ['Employee Name:', payslip.get('employee_name', ''), 'Start Date:', str(payslip.get('start_date', ''))],
                ['Position:', payslip.get('position', ''), 'End Date:', str(payslip.get('end_date', ''))],
                ['Department:', payslip.get('department', ''), '', ''],
            ]
            
            info_table = Table(info_data, colWidths=[100, 150, 80, 150])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 20))
            
            # Earnings section
            elements.append(Paragraph("EARNINGS", ParagraphStyle('SectionHeader', fontSize=12, fontName='Helvetica-Bold', spaceAfter=10)))
            
            # Format amounts with peso sign
            peso_symbol = "₱" if UNICODE_FONT == 'DejaVuSans' else "PHP "
            basic_pay = float(payslip.get('basic_pay', 0) or 0)
            overtime_pay = float(payslip.get('overtime_pay', 0) or 0)
            allowance = float(payslip.get('allowance', 0) or 0)
            gross_pay = float(payslip.get('gross_pay', 0) or 0)
            
            earnings_data = [
                ['Description', 'Amount'],
                ['Basic Pay', f"{peso_symbol}{basic_pay:,.2f}"],
                ['Overtime Pay', f"{peso_symbol}{overtime_pay:,.2f}"],
                ['Allowance', f"{peso_symbol}{allowance:,.2f}"],
                ['GROSS PAY', f"{peso_symbol}{gross_pay:,.2f}"],
            ]
            
            earnings_table = Table(earnings_data, colWidths=[300, 150])
            font_name = 'Helvetica-Bold'  # Use built-in bold font
            earnings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTNAME', (0, -1), (-1, -1), font_name),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(earnings_table)
            elements.append(Spacer(1, 20))
            
            # Deductions section
            elements.append(Paragraph("DEDUCTIONS", ParagraphStyle('SectionHeader', fontSize=12, fontName='Helvetica-Bold', spaceAfter=10)))
            
            # Format deduction amounts with peso sign
            peso_symbol = "₱" if UNICODE_FONT == 'DejaVuSans' else "PHP "
            sss = float(payslip.get('sss_deduction', 0) or 0)
            philhealth = float(payslip.get('philhealth_deduction', 0) or 0)
            pagibig = float(payslip.get('pagibig_deduction', 0) or 0)
            tax = float(payslip.get('tax_deduction', 0) or 0)
            late = float(payslip.get('late_deduction', 0) or 0)
            absence = float(payslip.get('absence_deduction', 0) or 0)
            total_deductions = float(payslip.get('total_deductions', 0) or 0)
            
            deductions_data = [
                ['Description', 'Amount'],
                ['SSS', f"{peso_symbol}{sss:,.2f}"],
                ['PhilHealth', f"{peso_symbol}{philhealth:,.2f}"],
                ['Pag-IBIG', f"{peso_symbol}{pagibig:,.2f}"],
                ['Tax', f"{peso_symbol}{tax:,.2f}"],
                ['Late Deduction', f"{peso_symbol}{late:,.2f}"],
                ['Absence Deduction', f"{peso_symbol}{absence:,.2f}"],
                ['TOTAL DEDUCTIONS', f"{peso_symbol}{total_deductions:,.2f}"],
            ]
            
            deductions_table = Table(deductions_data, colWidths=[300, 150])
            deductions_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), font_name),
                ('FONTNAME', (0, -1), (-1, -1), font_name),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(deductions_table)
            elements.append(Spacer(1, 20))
            
            # Net pay
            peso_symbol = "₱" if UNICODE_FONT == 'DejaVuSans' else "PHP "
            net_pay = float(payslip.get('net_pay', 0) or 0)
            net_pay_data = [
                ['NET PAY', f"{peso_symbol}{net_pay:,.2f}"]
            ]
            
            net_pay_table = Table(net_pay_data, colWidths=[300, 150])
            net_pay_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
            ]))
            elements.append(net_pay_table)
            
            # Footer
            elements.append(Spacer(1, 40))
            footer_style = ParagraphStyle('Footer', fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
            elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y %I:%M %p')}", footer_style))
            elements.append(Paragraph("This is a computer-generated payslip.", footer_style))
            
            doc.build(elements)
            return True
            
        except Exception as e:
            print(f"Payslip PDF error: {e}")
            return False
    
    # ==================== DASHBOARD STATISTICS ====================
    
    def get_dashboard_stats(self):
        """
        Get statistics for dashboard display.
        
        Returns:
            Dictionary with various statistics
        """
        stats = {}
        
        # Employee counts
        emp_query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'Inactive' THEN 1 ELSE 0 END) as inactive
            FROM employees
        """
        emp_result = self.db.execute_query(emp_query, fetch_one=True)
        stats['employees'] = {
            'total': emp_result.get('total', 0) or 0,
            'active': emp_result.get('active', 0) or 0,
            'inactive': emp_result.get('inactive', 0) or 0
        }
        
        # Today's attendance
        today = datetime.now().date()
        att_query = """
            SELECT 
                COUNT(*) as present
            FROM attendance
            WHERE attendance_date = %s AND status = 'Present'
        """
        att_result = self.db.execute_query(att_query, (today,), fetch_one=True)
        stats['today_attendance'] = {
            'present': att_result.get('present', 0) or 0,
            'total_active': stats['employees']['active']
        }
        
        # Recent payroll
        payroll_query = """
            SELECT payroll_id, payroll_period, total_net_pay, status
            FROM payroll
            ORDER BY created_at DESC
            LIMIT 1
        """
        payroll_result = self.db.execute_query(payroll_query, fetch_one=True)
        stats['recent_payroll'] = payroll_result or {}
        
        # Monthly totals - only count Paid/Approved payrolls
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_query = """
            SELECT 
                COALESCE(SUM(total_net_pay), 0) as monthly_total
            FROM payroll
            WHERE MONTH(start_date) = %s 
            AND YEAR(start_date) = %s
            AND status IN ('Paid', 'Approved')
        """
        monthly_result = self.db.execute_query(monthly_query, (current_month, current_year), fetch_one=True)
        stats['monthly_payroll'] = float(monthly_result.get('monthly_total', 0) or 0)
        
        return stats

    def get_weekly_attendance(self):
        """
        Get weekly attendance data for the current week.
        
        Returns:
            Dictionary with days of week, hours worked, and attendance counts
        """
        from datetime import timedelta
        
        today = datetime.now().date()
        # Get Monday of current week
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        # Get data for each day of the week
        weekly_data = {
            'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'present': [],
            'overtime': [],
            'hours_worked': []  # Hours worked per day
        }
        
        # Sample hours data (Mon: 8, Tue: 7.5, Wed: 8, Thu: 6, Fri: 8, Sat: 0, Sun: 0)
        sample_hours = [8.0, 7.5, 8.0, 6.0, 8.0, 0.0, 0.0]
        
        for i in range(7):
            day_date = monday + timedelta(days=i)
            
            # Count present employees
            present_query = """
                SELECT COUNT(*) as count
                FROM attendance
                WHERE attendance_date = %s AND status = 'Present'
            """
            present_result = self.db.execute_query(present_query, (day_date,), fetch_one=True)
            present_count = present_result.get('count', 0) or 0
            
            # Count overtime hours (employees with overtime > 0)
            overtime_query = """
                SELECT COUNT(*) as count
                FROM attendance
                WHERE attendance_date = %s AND status = 'Present' AND overtime_hours > 0
            """
            overtime_result = self.db.execute_query(overtime_query, (day_date,), fetch_one=True)
            overtime_count = overtime_result.get('count', 0) or 0
            
            # Get average hours worked for the day
            hours_query = """
                SELECT AVG(hours_worked) as avg_hours
                FROM attendance
                WHERE attendance_date = %s AND status = 'Present'
            """
            hours_result = self.db.execute_query(hours_query, (day_date,), fetch_one=True)
            avg_hours = float(hours_result.get('avg_hours', 0) or 0)
            
            # Use sample data if no real data available
            if avg_hours == 0 and present_count == 0:
                avg_hours = sample_hours[i]
            
            weekly_data['present'].append(present_count)
            weekly_data['overtime'].append(overtime_count)
            weekly_data['hours_worked'].append(avg_hours)
        
        return weekly_data
    
    def get_payroll_breakdown(self):
        """
        Get payroll breakdown for current month.
        
        Returns:
            Dictionary with payroll breakdown percentages (salary, bonuses, taxes, deductions)
        """
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Get payroll details for current month
        query = """
            SELECT 
                COALESCE(SUM(basic_pay), 0) as salary_total,
                COALESCE(SUM(overtime_pay), 0) as bonuses_total,
                COALESCE(SUM(total_deductions), 0) as deductions_total
            FROM payroll_details pd
            JOIN payroll p ON pd.payroll_id = p.payroll_id
            WHERE MONTH(p.start_date) = %s AND YEAR(p.start_date) = %s
        """
        
        result = self.db.execute_query(query, (current_month, current_year), fetch_one=True)
        
        salary = float(result.get('salary_total', 0) or 0)
        bonuses = float(result.get('bonuses_total', 0) or 0)
        deductions = float(result.get('deductions_total', 0) or 0)
        
        # Calculate taxes as 10% of salary (sample calculation)
        taxes = salary * 0.10 if salary > 0 else 0
        
        total = salary + bonuses + taxes + deductions
        
        if total == 0:
            # Return sample percentages if no data (salary: 70%, bonuses: 15%, taxes: 10%, deductions: 5%)
            return {
                'salary': 70.0,
                'bonuses': 15.0,
                'taxes': 10.0,
                'deductions': 5.0
            }
        
        return {
            'salary': (salary / total) * 100,
            'bonuses': (bonuses / total) * 100,
            'taxes': (taxes / total) * 100,
            'deductions': (deductions / total) * 100
        }
    
    def get_employee_count_change(self):
        """
        Get employee count change from last month.
        
        Returns:
            Integer representing the change (positive or negative)
        """
        from datetime import timedelta
        
        today = datetime.now().date()
        first_day_current = today.replace(day=1)
        first_day_last = (first_day_current - timedelta(days=1)).replace(day=1)
        last_day_last = first_day_current - timedelta(days=1)
        
        # Count employees active at end of last month
        last_month_query = """
            SELECT COUNT(*) as count
            FROM employees
            WHERE status = 'Active' 
            AND (date_hired IS NULL OR date_hired <= %s)
        """
        last_month_result = self.db.execute_query(last_month_query, (last_day_last,), fetch_one=True)
        last_month_count = last_month_result.get('count', 0) or 0
        
        # Count employees active now
        current_query = """
            SELECT COUNT(*) as count
            FROM employees
            WHERE status = 'Active'
        """
        current_result = self.db.execute_query(current_query, fetch_one=True)
        current_count = current_result.get('count', 0) or 0
        
        return current_count - last_month_count
    
    def get_payroll_change(self):
        """
        Get payroll change percentage from last month.
        
        Returns:
            Float representing the percentage change
        """
        from datetime import timedelta
        
        today = datetime.now().date()
        current_month = today.month
        current_year = today.year
        
        # Get last month
        if current_month == 1:
            last_month = 12
            last_year = current_year - 1
        else:
            last_month = current_month - 1
            last_year = current_year
        
        # Current month total (only Paid/Approved)
        current_query = """
            SELECT COALESCE(SUM(total_net_pay), 0) as monthly_total
            FROM payroll
            WHERE MONTH(start_date) = %s 
            AND YEAR(start_date) = %s
            AND status IN ('Paid', 'Approved')
        """
        current_result = self.db.execute_query(current_query, (current_month, current_year), fetch_one=True)
        current_total = float(current_result.get('monthly_total', 0) or 0)
        
        # Last month total (only Paid/Approved)
        last_query = """
            SELECT COALESCE(SUM(total_net_pay), 0) as monthly_total
            FROM payroll
            WHERE MONTH(start_date) = %s 
            AND YEAR(start_date) = %s
            AND status IN ('Paid', 'Approved')
        """
        last_result = self.db.execute_query(last_query, (last_month, last_year), fetch_one=True)
        last_total = float(last_result.get('monthly_total', 0) or 0)
        
        if last_total == 0:
            return 0.0
        
        return ((current_total - last_total) / last_total) * 100
    
    def get_pending_approvals(self):
        """
        Get count of pending overtime requests/approvals.
        
        Returns:
            Integer count of pending approvals
        """
        # For now, count payrolls in Draft status as pending
        query = """
            SELECT COUNT(*) as count
            FROM payroll
            WHERE status = 'Draft'
        """
        result = self.db.execute_query(query, fetch_one=True)
        return result.get('count', 0) or 0
    
    def generate_dashboard_pdf(self, filename):
        """
        Generate a PDF report of dashboard statistics.
        
        Args:
            filename: Output PDF file path
            
        Returns:
            Boolean indicating success
        """
        if not HAS_REPORTLAB:
            print("ReportLab not available. Cannot generate PDF.")
            print("Install with: pip install reportlab")
            return False
        
        try:
            import os
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(filename)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0055FF'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            elements.append(Paragraph("Dashboard Report", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Date
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#6B7280'),
                alignment=TA_CENTER
            )
            elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", date_style))
            elements.append(Spacer(1, 0.4*inch))
            
            # Get dashboard stats
            stats = self.get_dashboard_stats()
            weekly_data = self.get_weekly_attendance()
            breakdown = self.get_payroll_breakdown()
            
            # Statistics section
            heading_style = ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#111827'),
                spaceAfter=12,
                spaceBefore=20
            )
            elements.append(Paragraph("Key Statistics", heading_style))
            
            # Stats table
            stats_data = [
                ['Metric', 'Value'],
                ['Total Employees', str(stats.get('employees', {}).get('active', 0))],
                ['Present Today', str(stats.get('today_attendance', {}).get('present', 0))],
                ['Monthly Payroll', f"{'₱' if UNICODE_FONT == 'DejaVuSans' else 'PHP '}{stats.get('monthly_payroll', 0):,.0f}"],
                ['Pending Approvals', str(self.get_pending_approvals())],
            ]
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0055FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ]))
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Weekly Attendance section
            elements.append(Paragraph("Weekly Attendance", heading_style))
            total_hours = sum(weekly_data.get('hours_worked', [0]))
            attendance_data = [
                ['Day', 'Hours Worked', 'Progress'],
            ]
            for day, hours in zip(weekly_data['days'], weekly_data.get('hours_worked', [0]*7)):
                progress = f"{(hours/8.0)*100:.0f}%" if hours > 0 else "0%"
                attendance_data.append([day, f"{hours:.1f}h", progress])
            
            attendance_data.append(['Total', f"{total_hours:.1f}h / 40h", f"{(total_hours/40.0)*100:.0f}%"])
            
            attendance_table = Table(attendance_data, colWidths=[1.5*inch, 2*inch, 1.5*inch])
            attendance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0055FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(attendance_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Payroll Breakdown section
            elements.append(Paragraph("Payroll Breakdown", heading_style))
            breakdown_data = [
                ['Category', 'Percentage'],
                ['Salary', f"{breakdown.get('salary', 70):.1f}%"],
                ['Bonuses', f"{breakdown.get('bonuses', 15):.1f}%"],
                ['Taxes', f"{breakdown.get('taxes', 10):.1f}%"],
                ['Deductions', f"{breakdown.get('deductions', 5):.1f}%"],
            ]
            
            breakdown_table = Table(breakdown_data, colWidths=[3*inch, 2*inch])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0055FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ]))
            elements.append(breakdown_table)
            
            # Build PDF
            doc.build(elements)
            
            # Verify file was created
            if os.path.exists(filename):
                print(f"Dashboard PDF created successfully: {filename}")
                return True
            else:
                print(f"Error: PDF file was not created at {filename}")
                return False
            
        except PermissionError as e:
            print(f"Permission error generating dashboard PDF: {e}")
            print(f"Make sure you have write permissions for: {filename}")
            return False
        except Exception as e:
            import traceback
            print(f"Error generating dashboard PDF: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return False


# Create a global report manager instance
report_manager = ReportManager()

