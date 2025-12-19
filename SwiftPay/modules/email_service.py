"""
Email Service Module
Handles sending daily attendance summaries via email using smtplib.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
from typing import List, Dict, Optional
import os


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        """Initialize email service with configuration"""
        # Email configuration - can be set via environment variables or config file
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        self.use_tls = os.getenv('USE_TLS', 'true').lower() == 'true'
    
    def send_daily_attendance_summary(self, recipient_email: str, summary_data: Dict, date: Optional[date] = None) -> bool:
        """
        Send daily attendance summary email.
        
        Args:
            recipient_email: Email address of recipient
            summary_data: Dictionary containing attendance summary data
            date: Date of the summary (defaults to today)
            
        Returns:
            Boolean indicating success
        """
        if not self.sender_email or not self.sender_password:
            print("Email service not configured. Set SENDER_EMAIL and SENDER_PASSWORD environment variables.")
            return False
        
        if date is None:
            date = datetime.now().date()
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Daily Attendance Summary - {date.strftime('%B %d, %Y')}"
            
            # Build email content
            html_content = self._build_summary_html(summary_data, date)
            text_content = self._build_summary_text(summary_data, date)
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def _build_summary_text(self, summary_data: Dict, date: date) -> str:
        """Build plain text version of summary"""
        text = f"""
Daily Attendance Summary - {date.strftime('%B %d, %Y')}

===========================================
SUMMARY STATISTICS
===========================================
Total Employees: {summary_data.get('total_employees', 0)}
Present: {summary_data.get('present_count', 0)}
Absent: {summary_data.get('absent_count', 0)}
On Leave: {summary_data.get('leave_count', 0)}
Late Arrivals: {summary_data.get('late_count', 0)}
Total Hours Worked: {summary_data.get('total_hours', 0):.2f}
Total Overtime Hours: {summary_data.get('total_overtime', 0):.2f}

===========================================
ATTENDANCE DETAILS
===========================================
"""
        
        attendance_list = summary_data.get('attendance_list', [])
        for record in attendance_list:
            emp_name = record.get('employee_name', 'Unknown')
            status = record.get('status', 'Unknown')
            time_in = record.get('time_in', 'N/A')
            time_out = record.get('time_out', 'N/A')
            hours = record.get('hours_worked', 0)
            
            text += f"\n{emp_name}: {status}\n"
            if time_in != 'N/A':
                text += f"  Time In: {time_in}\n"
            if time_out != 'N/A':
                text += f"  Time Out: {time_out}\n"
            if hours > 0:
                text += f"  Hours Worked: {hours:.2f}\n"
        
        text += "\n\n---\nThis is an automated message from SwiftPay Attendance System."
        
        return text
    
    def _build_summary_html(self, summary_data: Dict, date: date) -> str:
        """Build HTML version of summary"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #0055FF; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
        .stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #0055FF; }}
        .stat-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #0055FF; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #0055FF; color: white; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .status-present {{ color: #10B981; font-weight: bold; }}
        .status-absent {{ color: #EF4444; font-weight: bold; }}
        .status-leave {{ color: #F59E0B; font-weight: bold; }}
        .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Daily Attendance Summary</h1>
            <p>{date.strftime('%B %d, %Y')}</p>
        </div>
        <div class="content">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Total Employees</div>
                    <div class="stat-value">{summary_data.get('total_employees', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Present</div>
                    <div class="stat-value">{summary_data.get('present_count', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Absent</div>
                    <div class="stat-value">{summary_data.get('absent_count', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Hours</div>
                    <div class="stat-value">{summary_data.get('total_hours', 0):.2f}</div>
                </div>
            </div>
            
            <h2>Attendance Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Employee</th>
                        <th>Status</th>
                        <th>Time In</th>
                        <th>Time Out</th>
                        <th>Hours</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        attendance_list = summary_data.get('attendance_list', [])
        for record in attendance_list:
            emp_name = record.get('employee_name', 'Unknown')
            status = record.get('status', 'Unknown')
            time_in = str(record.get('time_in', 'N/A'))[:5] if record.get('time_in') else 'N/A'
            time_out = str(record.get('time_out', 'N/A'))[:5] if record.get('time_out') else 'N/A'
            hours = record.get('hours_worked', 0) or 0
            
            status_class = f"status-{status.lower()}" if status else ""
            
            html += f"""
                    <tr>
                        <td>{emp_name}</td>
                        <td class="{status_class}">{status}</td>
                        <td>{time_in}</td>
                        <td>{time_out}</td>
                        <td>{hours:.2f}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
            
            <div class="footer">
                <p>This is an automated message from SwiftPay Attendance System.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html


# Global instance
email_service = EmailService()

