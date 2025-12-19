"""
SwiftPay Reports Page
Report generation and export functionality
"""

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QMessageBox, QHeaderView,
    QTabWidget, QAbstractItemView, QGroupBox, QFileDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles
from modules.reports import report_manager
from modules.employees import employee_manager


class ReportsPage(QWidget):
    """
    Reports and analytics page with various report types.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Tab widget for different report types
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background-color: white;
            }
        """)
        
        # Attendance Reports Tab
        attendance_tab = self.create_attendance_tab()
        tabs.addTab(attendance_tab, "Attendance Reports")
        
        # Payroll Reports Tab
        payroll_tab = self.create_payroll_tab()
        tabs.addTab(payroll_tab, "Payroll Reports")
        
        # Employee Reports Tab
        employee_tab = self.create_employee_tab()
        tabs.addTab(employee_tab, "Employee Reports")
        
        layout.addWidget(tabs)
    
    def create_attendance_tab(self):
        """Create attendance reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Filter section
        filter_group = QGroupBox("Report Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        # Employee filter
        emp_label = QLabel("Employee:")
        self.att_employee = QComboBox()
        self.att_employee.addItem("All Employees", None)
        employees = employee_manager.get_active_employees()
        if employees:
            for emp in employees:
                name = f"{emp.get('employee_code')} - {emp.get('first_name')} {emp.get('last_name')}"
                self.att_employee.addItem(name, emp.get('employee_id'))
        
        # Date range
        start_label = QLabel("From:")
        self.att_start = QDateEdit()
        self.att_start.setDate(QDate.currentDate().addMonths(-1))
        self.att_start.setCalendarPopup(True)
        
        end_label = QLabel("To:")
        self.att_end = QDateEdit()
        self.att_end.setDate(QDate.currentDate())
        self.att_end.setCalendarPopup(True)
        
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.setMinimumHeight(40)
        generate_btn.setStyleSheet(Styles.BTN_PRIMARY)
        generate_btn.clicked.connect(self.generate_attendance_report)
        
        filter_layout.addWidget(emp_label)
        filter_layout.addWidget(self.att_employee)
        filter_layout.addWidget(start_label)
        filter_layout.addWidget(self.att_start)
        filter_layout.addWidget(end_label)
        filter_layout.addWidget(self.att_end)
        filter_layout.addWidget(generate_btn)
        filter_layout.addStretch()
        
        layout.addWidget(filter_group)
        
        # Export button
        export_layout = QHBoxLayout()
        
        pdf_btn = QPushButton("📄 Export PDF")
        pdf_btn.setStyleSheet(Styles.BTN_OUTLINE)
        pdf_btn.clicked.connect(self.export_attendance_pdf)
        
        export_layout.addStretch()
        export_layout.addWidget(pdf_btn)
        
        layout.addLayout(export_layout)
        
        # Results table
        self.att_table = QTableWidget()
        self.setup_attendance_table()
        layout.addWidget(self.att_table, 1)
        
        return tab
    
    def create_payroll_tab(self):
        """Create payroll reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Filter section
        filter_group = QGroupBox("Report Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        # Year filter
        year_label = QLabel("Year:")
        self.pay_year = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 1):
            self.pay_year.addItem(str(year), year)
        self.pay_year.setCurrentText(str(current_year))
        
        # Month filter
        month_label = QLabel("Month:")
        self.pay_month = QComboBox()
        self.pay_month.addItem("All Months", None)
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        for i, month in enumerate(months, 1):
            self.pay_month.addItem(month, i)
        
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.setMinimumHeight(40)
        generate_btn.setStyleSheet(Styles.BTN_PRIMARY)
        generate_btn.clicked.connect(self.generate_payroll_report)
        
        # Export PDF button
        export_pdf_btn = QPushButton("📄 Export PDF")
        export_pdf_btn.setMinimumHeight(40)
        export_pdf_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B5CF6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
            QPushButton:pressed {
                background-color: #6D28D9;
            }
        """)
        export_pdf_btn.clicked.connect(self.export_payroll_pdf)
        
        filter_layout.addWidget(year_label)
        filter_layout.addWidget(self.pay_year)
        filter_layout.addWidget(month_label)
        filter_layout.addWidget(self.pay_month)
        filter_layout.addWidget(generate_btn)
        filter_layout.addWidget(export_pdf_btn)
        filter_layout.addStretch()
        
        layout.addWidget(filter_group)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        
        self.pay_total_card = self.create_summary_card("Total Payrolls", "0", "#0055FF", "📊")
        self.pay_gross_card = self.create_summary_card("Total Gross", "₱0", "#10B981", "💰")
        self.pay_ded_card = self.create_summary_card("Total Deductions", "₱0", "#F59E0B", "📉")
        self.pay_net_card = self.create_summary_card("Total Net Pay", "₱0", "#0277BD", "💵")
        
        summary_layout.addWidget(self.pay_total_card)
        summary_layout.addWidget(self.pay_gross_card)
        summary_layout.addWidget(self.pay_ded_card)
        summary_layout.addWidget(self.pay_net_card)
        
        layout.addLayout(summary_layout)
        
        # Export buttons removed - only PDF export available
        
        # Results table
        self.pay_table = QTableWidget()
        self.setup_payroll_table()
        layout.addWidget(self.pay_table, 1)
        
        return tab
    
    def create_employee_tab(self):
        """Create employee reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Filter section
        filter_group = QGroupBox("Report Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        # Status filter
        status_label = QLabel("Status:")
        self.emp_status = QComboBox()
        self.emp_status.addItems(["All", "Active", "Inactive"])
        
        # Department filter
        dept_label = QLabel("Department:")
        self.emp_dept = QComboBox()
        self.emp_dept.addItem("All Departments", None)
        departments = employee_manager.get_departments()
        for dept in departments:
            self.emp_dept.addItem(dept, dept)
        
        generate_btn = QPushButton("📊 Generate Report")
        generate_btn.setMinimumHeight(40)
        generate_btn.setStyleSheet(Styles.BTN_PRIMARY)
        generate_btn.clicked.connect(self.generate_employee_report)
        
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.emp_status)
        filter_layout.addWidget(dept_label)
        filter_layout.addWidget(self.emp_dept)
        filter_layout.addWidget(generate_btn)
        filter_layout.addStretch()
        
        layout.addWidget(filter_group)
        
        # Summary
        summary_layout = QHBoxLayout()
        
        self.emp_total_card = self.create_summary_card("Total Employees", "0", "#0055FF", "👥")
        self.emp_active_card = self.create_summary_card("Active", "0", "#10B981", "✅")
        self.emp_inactive_card = self.create_summary_card("Inactive", "0", "#6B7280", "❌")
        
        summary_layout.addWidget(self.emp_total_card)
        summary_layout.addWidget(self.emp_active_card)
        summary_layout.addWidget(self.emp_inactive_card)
        summary_layout.addStretch()
        
        layout.addLayout(summary_layout)
        
        # Export buttons removed - only PDF export available
        
        # Results table
        self.emp_table = QTableWidget()
        self.setup_employee_table()
        layout.addWidget(self.emp_table, 1)
        
        return tab
    
    def create_summary_card(self, title, value, color, icon=""):
        """Create a modern summary card widget with improved styling"""
        card = QFrame()
        card.setObjectName("summaryCard")
        card.setStyleSheet(f"""
            QFrame#summaryCard {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                padding: 0px;
            }}
            QFrame#summaryCard:hover {{
                border-color: {color};
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
        """)
        card.setMinimumSize(200, 100)
        card.setMaximumHeight(120)
        
        # Main layout
        main_layout = QHBoxLayout(card)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left accent bar (stylized bracket)
        accent_bar = QFrame()
        accent_bar.setFixedWidth(6)
        accent_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }}
        """)
        main_layout.addWidget(accent_bar)
        
        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(8)
        
        # Title and icon row
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"color: {color}; font-size: 18px;")
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6B7280; font-size: 12px; font-weight: 500;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        content_layout.addLayout(title_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"""
            color: {color};
            font-size: 26px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        content_layout.addWidget(value_label)
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        
        return card
    
    def setup_attendance_table(self):
        """Setup attendance report table"""
        columns = [
            "Date", "Code", "Employee", "Position", "Department",
            "Time In", "Time Out", "Hours", "OT", "Late", "Status"
        ]
        
        self.att_table.setColumnCount(len(columns))
        self.att_table.setHorizontalHeaderLabels(columns)
        
        header = self.att_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.att_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.att_table.setAlternatingRowColors(True)
        self.att_table.verticalHeader().setVisible(False)
    
    def setup_payroll_table(self):
        """Setup payroll report table"""
        columns = [
            "Period", "Start Date", "End Date", "Employees",
            "Gross Pay", "Deductions", "Net Pay", "Status"
        ]
        
        self.pay_table.setColumnCount(len(columns))
        self.pay_table.setHorizontalHeaderLabels(columns)
        
        header = self.pay_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.pay_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.pay_table.setAlternatingRowColors(True)
        self.pay_table.verticalHeader().setVisible(False)
    
    def setup_employee_table(self):
        """Setup employee report table"""
        columns = [
            "Code", "Name", "Email", "Position", "Department",
            "Rate/Hour", "Daily Rate", "Status", "Date Hired"
        ]
        
        self.emp_table.setColumnCount(len(columns))
        self.emp_table.setHorizontalHeaderLabels(columns)
        
        header = self.emp_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.emp_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.emp_table.setAlternatingRowColors(True)
        self.emp_table.verticalHeader().setVisible(False)
    
    # ==================== ATTENDANCE REPORTS ====================
    
    def generate_attendance_report(self):
        """Generate attendance report"""
        employee_id = self.att_employee.currentData()
        start = self.att_start.date().toPyDate()
        end = self.att_end.date().toPyDate()
        
        try:
            data = report_manager.get_attendance_report(start, end, employee_id)
            self.populate_attendance_table(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def populate_attendance_table(self, data):
        """Populate attendance report table"""
        self.att_table.setRowCount(0)
        
        if not data:
            return
        
        for row, rec in enumerate(data):
            self.att_table.insertRow(row)
            
            # Date
            date = rec.get('attendance_date', '')
            if hasattr(date, 'strftime'):
                date = date.strftime('%Y-%m-%d')
            self.att_table.setItem(row, 0, QTableWidgetItem(str(date)))
            
            self.att_table.setItem(row, 1, QTableWidgetItem(rec.get('employee_code', '')))
            self.att_table.setItem(row, 2, QTableWidgetItem(rec.get('employee_name', '')))
            self.att_table.setItem(row, 3, QTableWidgetItem(rec.get('position', '')))
            self.att_table.setItem(row, 4, QTableWidgetItem(rec.get('department', '')))
            
            # Times
            time_in = rec.get('time_in', '')
            if time_in:
                time_in = str(time_in)[:5] if hasattr(time_in, '__str__') else ''
            self.att_table.setItem(row, 5, QTableWidgetItem(str(time_in) if time_in else ''))
            
            time_out = rec.get('time_out', '')
            if time_out:
                time_out = str(time_out)[:5] if hasattr(time_out, '__str__') else ''
            self.att_table.setItem(row, 6, QTableWidgetItem(str(time_out) if time_out else ''))
            
            self.att_table.setItem(row, 7, QTableWidgetItem(f"{rec.get('hours_worked', 0) or 0:.2f}"))
            self.att_table.setItem(row, 8, QTableWidgetItem(f"{rec.get('overtime_hours', 0) or 0:.2f}"))
            self.att_table.setItem(row, 9, QTableWidgetItem(str(rec.get('late_minutes', 0) or 0)))
            
            status = rec.get('status', '')
            status_item = QTableWidgetItem(status)
            if status == 'Present':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif status == 'Absent':
                status_item.setForeground(Qt.GlobalColor.red)
            self.att_table.setItem(row, 10, status_item)
            
            self.att_table.setRowHeight(row, 35)
    
    def export_attendance_pdf(self):
        """Export attendance report to PDF"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Report", "attendance_report.pdf", "PDF Files (*.pdf)"
        )
        
        if filename:
            employee_id = self.att_employee.currentData()
            start = self.att_start.date().toPyDate()
            end = self.att_end.date().toPyDate()
            
            result = report_manager.export_attendance_pdf(start, end, filename, employee_id)
            
            if result:
                QMessageBox.information(self, "Success", f"Report exported to:\n{filename}")
            else:
                QMessageBox.warning(self, "Error", "Export failed. Make sure ReportLab is installed.")
    
    # ==================== PAYROLL REPORTS ====================
    
    def generate_payroll_report(self):
        """Generate payroll report"""
        year = self.pay_year.currentData()
        month = self.pay_month.currentData()
        
        try:
            data = report_manager.get_payroll_summary_report(year, month)
            self.populate_payroll_table(data)
            self.update_payroll_summary(year, month)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def populate_payroll_table(self, data):
        """Populate payroll report table"""
        self.pay_table.setRowCount(0)
        
        if not data:
            return
        
        for row, rec in enumerate(data):
            self.pay_table.insertRow(row)
            
            self.pay_table.setItem(row, 0, QTableWidgetItem(rec.get('payroll_period', '')))
            
            start = rec.get('start_date', '')
            if hasattr(start, 'strftime'):
                start = start.strftime('%Y-%m-%d')
            self.pay_table.setItem(row, 1, QTableWidgetItem(str(start)))
            
            end = rec.get('end_date', '')
            if hasattr(end, 'strftime'):
                end = end.strftime('%Y-%m-%d')
            self.pay_table.setItem(row, 2, QTableWidgetItem(str(end)))
            
            self.pay_table.setItem(row, 3, QTableWidgetItem(str(rec.get('total_employees', 0))))
            
            gross = QTableWidgetItem(f"₱{float(rec.get('total_gross_pay', 0)):,.2f}")
            gross.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.pay_table.setItem(row, 4, gross)
            
            ded = QTableWidgetItem(f"₱{float(rec.get('total_deductions', 0)):,.2f}")
            ded.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.pay_table.setItem(row, 5, ded)
            
            net = QTableWidgetItem(f"₱{float(rec.get('total_net_pay', 0)):,.2f}")
            net.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            net.setForeground(Qt.GlobalColor.darkGreen)
            self.pay_table.setItem(row, 6, net)
            
            status = rec.get('status', '')
            status_item = QTableWidgetItem(status)
            if status == 'Paid':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            self.pay_table.setItem(row, 7, status_item)
            
            self.pay_table.setRowHeight(row, 35)
    
    def export_payroll_pdf(self):
        """Export payroll report to PDF"""
        try:
            # Check if ReportLab is available
            try:
                import reportlab
            except ImportError:
                QMessageBox.warning(
                    self,
                    "ReportLab Not Installed",
                    "ReportLab library is required to export PDF files.\n\n"
                    "To install:\n"
                    "1. Open PyCharm Settings → Python Interpreter\n"
                    "2. Click '+' and search for 'reportlab'\n"
                    "3. Install it\n\n"
                    "Or run in terminal:\n"
                    "pip install reportlab"
                )
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Payroll Report",
                f"payroll_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                # Ensure filename ends with .pdf
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
                
                year = self.pay_year.currentData()
                month = self.pay_month.currentData()
                
                result = report_manager.export_payroll_summary_pdf(year, month, filename)
                
                if result:
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Payroll report has been exported successfully!\n\n"
                        f"File location:\n{filename}\n\n"
                        f"The PDF contains all payroll data for the selected period."
                    )
                else:
                    # Check for specific error conditions
                    error_msg = "Failed to export payroll report.\n\n"
                    
                    # Check if ReportLab is installed
                    try:
                        import reportlab
                        error_msg += "ReportLab is installed.\n"
                    except ImportError:
                        error_msg += "⚠️ ReportLab library is not installed.\n"
                        error_msg += "Install it with: pip install reportlab\n\n"
                    
                    # Check file path
                    import os
                    dir_path = os.path.dirname(filename)
                    if dir_path and not os.path.exists(dir_path):
                        error_msg += "⚠️ Directory does not exist.\n"
                    elif not os.access(os.path.dirname(filename) if dir_path else os.getcwd(), os.W_OK):
                        error_msg += "⚠️ No write permission for this location.\n"
                    
                    # Check if data exists
                    data = report_manager.get_payroll_summary_report(year, month)
                    if not data:
                        error_msg += "⚠️ No payroll data found for the selected period.\n"
                    
                    error_msg += "\nPlease check the error console for more details."
                    
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        error_msg
                    )
        except PermissionError as e:
            QMessageBox.critical(
                self,
                "Permission Error",
                f"Permission denied when trying to save the file.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please:\n"
                f"1. Choose a different location\n"
                f"2. Check file permissions\n"
                f"3. Make sure the file is not open in another program"
            )
        except Exception as e:
            import traceback
            error_details = str(e)
            QMessageBox.critical(
                self,
                "Export Error",
                f"An unexpected error occurred while exporting:\n\n"
                f"{error_details}\n\n"
                f"Please check:\n"
                f"1. ReportLab is properly installed\n"
                f"2. You have write permissions\n"
                f"3. The file path is valid\n\n"
                f"Check the console for full error details."
            )
            print(f"Export error traceback:\n{traceback.format_exc()}")
    
    def update_payroll_summary(self, year, month):
        """Update payroll summary cards"""
        from modules.payroll import payroll_manager
        summary = payroll_manager.get_payroll_summary(year, month)
        
        self.pay_total_card.findChild(QLabel, "value").setText(str(summary.get('total_payrolls', 0)))
        self.pay_gross_card.findChild(QLabel, "value").setText(f"₱{summary.get('total_gross', 0):,.2f}")
        self.pay_ded_card.findChild(QLabel, "value").setText(f"₱{summary.get('total_deductions', 0):,.2f}")
        self.pay_net_card.findChild(QLabel, "value").setText(f"₱{summary.get('total_net', 0):,.2f}")
    
    # ==================== EMPLOYEE REPORTS ====================
    
    def generate_employee_report(self):
        """Generate employee report"""
        status = self.emp_status.currentText()
        if status == "All":
            status = None
        
        department = self.emp_dept.currentData()
        
        try:
            data = report_manager.get_employee_list_report(status, department)
            self.populate_employee_table(data)
            self.update_employee_summary()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def populate_employee_table(self, data):
        """Populate employee report table"""
        self.emp_table.setRowCount(0)
        
        if not data:
            return
        
        for row, rec in enumerate(data):
            self.emp_table.insertRow(row)
            
            self.emp_table.setItem(row, 0, QTableWidgetItem(rec.get('employee_code', '')))
            self.emp_table.setItem(row, 1, QTableWidgetItem(rec.get('employee_name', '')))
            self.emp_table.setItem(row, 2, QTableWidgetItem(rec.get('email', '')))
            self.emp_table.setItem(row, 3, QTableWidgetItem(rec.get('position', '')))
            self.emp_table.setItem(row, 4, QTableWidgetItem(rec.get('department', '')))
            
            rate = QTableWidgetItem(f"₱{float(rec.get('rate_per_hour', 0)):,.2f}")
            rate.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.emp_table.setItem(row, 5, rate)
            
            daily = QTableWidgetItem(f"₱{float(rec.get('daily_rate', 0)):,.2f}")
            daily.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.emp_table.setItem(row, 6, daily)
            
            status = rec.get('status', '')
            status_item = QTableWidgetItem(status)
            if status == 'Active':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.gray)
            self.emp_table.setItem(row, 7, status_item)
            
            hired = rec.get('date_hired', '')
            if hasattr(hired, 'strftime'):
                hired = hired.strftime('%Y-%m-%d')
            self.emp_table.setItem(row, 8, QTableWidgetItem(str(hired) if hired else ''))
            
            self.emp_table.setRowHeight(row, 35)
    
    def update_employee_summary(self):
        """Update employee summary cards"""
        total = employee_manager.get_employee_count()
        active = employee_manager.get_employee_count('Active')
        inactive = employee_manager.get_employee_count('Inactive')
        
        self.emp_total_card.findChild(QLabel, "value").setText(str(total))
        self.emp_active_card.findChild(QLabel, "value").setText(str(active))
        self.emp_inactive_card.findChild(QLabel, "value").setText(str(inactive))
    

