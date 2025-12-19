"""
SwiftPay Attendance Management Page
Time-in/out tracking and attendance records
"""

import sys
import os
from datetime import datetime, time, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QDateEdit, QTimeEdit,
    QMessageBox, QHeaderView, QScrollArea, QTabWidget,
    QAbstractItemView, QTextEdit, QGroupBox, QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QTime, QTimer
from PyQt6.QtGui import QFont

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles
from modules.attendance import attendance_manager
from modules.employees import employee_manager
from modules.reports import report_manager


class AttendanceDialog(QDialog):
    """
    Dialog for recording attendance manually.
    """
    
    def __init__(self, parent=None, attendance_data=None):
        super().__init__(parent)
        self.attendance_data = attendance_data
        self.is_edit = attendance_data is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_attendance_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        title = "Edit Attendance" if self.is_edit else "Record Attendance"
        self.setWindowTitle(title)
        self.setFixedSize(450, 400)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a237e;")
        layout.addWidget(title_label)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Employee dropdown
        self.employee_combo = QComboBox()
        self.load_employees()
        self.employee_combo.setEnabled(not self.is_edit)
        form_layout.addRow("Employee:", self.employee_combo)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setEnabled(not self.is_edit)
        form_layout.addRow("Date:", self.date_edit)
        
        # Time In
        self.time_in = QTimeEdit()
        self.time_in.setDisplayFormat("hh:mm AP")
        self.time_in.setTime(QTime(8, 0))
        form_layout.addRow("Time In:", self.time_in)
        
        # Time Out
        self.time_out = QTimeEdit()
        self.time_out.setDisplayFormat("hh:mm AP")
        self.time_out.setTime(QTime(17, 0))
        form_layout.addRow("Time Out:", self.time_out)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Present", "Absent", "Half-Day", "Leave"])
        form_layout.addRow("Status:", self.status_combo)
        
        # Remarks
        self.remarks = QLineEdit()
        self.remarks.setPlaceholderText("Optional remarks")
        form_layout.addRow("Remarks:", self.remarks)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(42)
        cancel_btn.setStyleSheet(Styles.BTN_OUTLINE)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setMinimumHeight(42)
        save_btn.setStyleSheet(Styles.BTN_PRIMARY)
        save_btn.clicked.connect(self.save_attendance)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_employees(self):
        """Load active employees into dropdown"""
        employees = employee_manager.get_active_employees()
        self.employee_combo.clear()
        
        if employees:
            for emp in employees:
                name = f"{emp.get('employee_code')} - {emp.get('first_name')} {emp.get('last_name')}"
                self.employee_combo.addItem(name, emp.get('employee_id'))
    
    def load_attendance_data(self):
        """Load existing attendance data"""
        if not self.attendance_data:
            return
        
        # Find and select employee
        emp_id = self.attendance_data.get('employee_id')
        for i in range(self.employee_combo.count()):
            if self.employee_combo.itemData(i) == emp_id:
                self.employee_combo.setCurrentIndex(i)
                break
        
        # Set date
        date = self.attendance_data.get('attendance_date')
        if date:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            self.date_edit.setDate(QDate(date.year, date.month, date.day))
        
        # Set time in
        time_in = self.attendance_data.get('time_in')
        if time_in:
            if isinstance(time_in, timedelta):
                total_seconds = int(time_in.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                self.time_in.setTime(QTime(hours, minutes))
            elif isinstance(time_in, time):
                self.time_in.setTime(QTime(time_in.hour, time_in.minute))
        
        # Set time out
        time_out = self.attendance_data.get('time_out')
        if time_out:
            if isinstance(time_out, timedelta):
                total_seconds = int(time_out.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                self.time_out.setTime(QTime(hours, minutes))
            elif isinstance(time_out, time):
                self.time_out.setTime(QTime(time_out.hour, time_out.minute))
        
        self.status_combo.setCurrentText(self.attendance_data.get('status', 'Present'))
        self.remarks.setText(self.attendance_data.get('remarks', '') or '')
    
    def save_attendance(self):
        """Save attendance record"""
        employee_id = self.employee_combo.currentData()
        if not employee_id:
            QMessageBox.warning(self, "Error", "Please select an employee.")
            return
        
        date = self.date_edit.date().toPyDate()
        time_in = self.time_in.time().toPyTime()
        time_out = self.time_out.time().toPyTime()
        status = self.status_combo.currentText()
        remarks = self.remarks.text().strip()
        
        try:
            if self.is_edit:
                # Update existing record
                data = {
                    'time_in': time_in,
                    'time_out': time_out,
                    'status': status,
                    'remarks': remarks
                }
                result = attendance_manager.update_attendance(
                    self.attendance_data['attendance_id'],
                    data
                )
                if result >= 0:
                    QMessageBox.information(self, "Success", "Attendance updated!")
                    self.accept()
            else:
                # Record new attendance
                if status == 'Absent':
                    attendance_manager.record_absence(employee_id, date, remarks)
                elif status == 'Leave':
                    attendance_manager.record_leave(employee_id, date, remarks)
                else:
                    attendance_manager.time_in(employee_id, time_in, date)
                    attendance_manager.time_out(employee_id, time_out, date)
                
                QMessageBox.information(self, "Success", "Attendance recorded!")
                self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")


class AttendancePage(QWidget):
    """
    Attendance management page with time-in/out and records view.
    """
    
    def __init__(self):
        super().__init__()
        # Initialize stat cards as None to prevent AttributeError
        self.present_card = None
        self.absent_card = None
        self.total_hours_card = None
        self.late_card = None
        
        self.init_ui()
        self.load_today_attendance()
    
    def init_ui(self):
        """Initialize the page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 12px 30px;
                margin-right: 5px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        
        # Time Clock Tab
        clock_tab = self.create_clock_tab()
        tabs.addTab(clock_tab, "⏰ Time Clock")
        
        # Records Tab
        records_tab = self.create_records_tab()
        tabs.addTab(records_tab, "Attendance Records")
        
        layout.addWidget(tabs)
    
    def create_clock_tab(self):
        """Create the time clock interface tab - Modern attendance tracking design"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(28)
        
        # Header Section - Left aligned
        header_section = QVBoxLayout()
        header_section.setSpacing(8)
        header_section.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Time Clock")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 38px;
                font-weight: 700;
                color: #111827;
                padding: 0;
                margin: 0;
            }
        """)
        
        subtitle_label = QLabel("Clock in and out, track breaks, and manage your work hours")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 400;
                color: #6B7280;
                padding: 0;
                margin: 0;
            }
        """)
        
        header_section.addWidget(title_label)
        header_section.addWidget(subtitle_label)
        layout.addLayout(header_section)
        
        # Employee Selection Section - Left aligned
        emp_section = QVBoxLayout()
        emp_section.setSpacing(12)
        emp_section.setContentsMargins(0, 0, 0, 0)
        
        emp_label = QLabel("Employee")
        emp_label.setStyleSheet("font-weight: 600; font-size: 15px; color: #374151; padding-bottom: 4px;")
        
        self.clock_employee = QComboBox()
        self.clock_employee.setMinimumHeight(56)
        self.clock_employee.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #D1D5DB;
                border-radius: 10px;
                padding: 16px 20px;
                font-size: 15px;
                font-weight: 500;
                color: #111827;
            }
            QComboBox:hover {
                border: 2px solid #9CA3AF;
                background-color: #FAFAFA;
            }
            QComboBox:focus {
                border: 2px solid #10B981;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 44px;
                padding-right: 14px;
            }
            QComboBox::drop-down:hover {
                background-color: #F3F4F6;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                selection-background-color: #EFF6FF;
                padding: 6px;
                font-size: 15px;
            }
        """)
        
        emp_section.addWidget(emp_label)
        emp_section.addWidget(self.clock_employee)
        
        layout.addLayout(emp_section)
        
        # Status Indicator - Centered
        self.status_indicator = QLabel("Select an employee")
        self.status_indicator.setStyleSheet("""
            QLabel {
                background-color: #FEF3C7;
                color: #92400E;
                border-radius: 10px;
                padding: 16px 28px;
                font-size: 15px;
                font-weight: 500;
                min-height: 48px;
            }
        """)
        self.status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_indicator)
        
        # Action Buttons Container
        self.btn_container = QWidget()
        btn_layout = QVBoxLayout(self.btn_container)
        btn_layout.setSpacing(14)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        # Clock In button (shown when not clocked in)
        self.clock_in_btn = QPushButton("🟢 Clock In")
        self.clock_in_btn.setMinimumHeight(60)
        self.clock_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clock_in_btn.clicked.connect(self.handle_time_in)
        self.clock_in_btn.setEnabled(False)
        self.clock_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 17px;
                font-weight: 600;
                padding: 18px 28px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #E5E7EB;
                color: #9CA3AF;
                border: none;
            }
        """)
        
        # Clock Out button (shown when clocked in)
        self.clock_out_btn = QPushButton("🔴 Clock Out")
        self.clock_out_btn.setMinimumHeight(56)
        self.clock_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clock_out_btn.clicked.connect(self.handle_time_out)
        self.clock_out_btn.setEnabled(False)
        self.clock_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                padding: 16px 26px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
            QPushButton:disabled {
                background-color: #E5E7EB;
                color: #9CA3AF;
                border: none;
            }
        """)
        
        # Initially show clock in button
        btn_layout.addWidget(self.clock_in_btn)
        self.clock_out_btn.hide()
        btn_layout.addWidget(self.clock_out_btn)
        
        layout.addWidget(self.btn_container)
        layout.addStretch()
        
        # Connect employee selection changes
        self.clock_employee.currentIndexChanged.connect(self.update_employee_status)
        self.load_clock_employees()
        
        return tab
    
    def create_stat_card(self, title, value, color, icon=""):
        """Create modern stat card widget with colored bracket"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }}
        """)
        card.setMinimumSize(180, 110)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Colored bracket/bar on the left
        bracket = QFrame()
        bracket.setFixedWidth(6)
        bracket.setStyleSheet(f"background-color: {color}; border-radius: 12px 0px 0px 12px;")
        layout.addWidget(bracket)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(8)
        
        # Icon and title row
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px;")
            title_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6B7280; font-size: 13px; font-weight: 500;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        content_layout.addLayout(title_layout)
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 700;")
        
        content_layout.addWidget(value_label)
        content_layout.addStretch()
        
        layout.addLayout(content_layout)
        
        return card
    
    def create_records_tab(self):
        """Create the attendance records tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Filter section - Grouped in a container
        filter_container = QFrame()
        filter_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                padding: 20px;
            }
        """)
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setSpacing(16)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)
        
        # Employee filter
        emp_label = QLabel("Employee:")
        emp_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #374151; min-width: 80px;")
        self.filter_employee = QComboBox()
        self.filter_employee.setMinimumHeight(42)
        self.filter_employee.addItem("All Employees", None)
        employees = employee_manager.get_active_employees()
        if employees:
            for emp in employees:
                name = f"{emp.get('employee_code')} - {emp.get('first_name')} {emp.get('last_name')}"
                self.filter_employee.addItem(name, emp.get('employee_id'))
        self.filter_employee.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 1.5px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                color: #111827;
            }
            QComboBox:focus {
                border: 1.5px solid #2563EB;
            }
        """)
        
        # Date range
        start_label = QLabel("From:")
        start_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #374151; min-width: 50px;")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        self.start_date.setMinimumHeight(42)
        self.start_date.setStyleSheet("""
            QDateEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 1.5px solid #2563EB;
            }
        """)
        
        end_label = QLabel("To:")
        end_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #374151; min-width: 50px;")
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setMinimumHeight(42)
        self.end_date.setStyleSheet("""
            QDateEdit {
                background-color: #FFFFFF;
                border: 1.5px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QDateEdit:focus {
                border: 1.5px solid #2563EB;
            }
        """)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.setMinimumHeight(42)
        search_btn.setMinimumWidth(100)
        search_btn.setStyleSheet(Styles.BTN_PRIMARY)
        search_btn.clicked.connect(self.search_attendance)
        
        filter_row.addWidget(emp_label)
        filter_row.addWidget(self.filter_employee)
        filter_row.addWidget(start_label)
        filter_row.addWidget(self.start_date)
        filter_row.addWidget(end_label)
        filter_row.addWidget(self.end_date)
        filter_row.addWidget(search_btn)
        filter_row.addStretch()
        
        filter_layout.addLayout(filter_row)
        
        # Action buttons row - Separated for clarity
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        
        add_btn = QPushButton("➕ Add Record")
        add_btn.setMinimumHeight(42)
        add_btn.setStyleSheet(Styles.BTN_SECONDARY)
        add_btn.clicked.connect(self.add_attendance)
        
        actions_row.addStretch()
        actions_row.addWidget(add_btn)
        
        filter_layout.addLayout(actions_row)
        layout.addWidget(filter_container)
        
        # Records table
        self.records_table = QTableWidget()
        self.setup_records_table()
        layout.addWidget(self.records_table, 1)
        
        return tab
    
    def setup_today_table(self):
        """Setup today's attendance table with modern styling"""
        columns = ["Code", "Employee Name", "Position", "Time In", "Time Out", "Hours", "Status"]
        
        self.today_table.setColumnCount(len(columns))
        self.today_table.setHorizontalHeaderLabels(columns)
        
        header = self.today_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.today_table.setColumnWidth(0, 100)
        self.today_table.setColumnWidth(3, 120)
        self.today_table.setColumnWidth(4, 120)
        self.today_table.setColumnWidth(5, 100)
        self.today_table.setColumnWidth(6, 120)
        
        self.today_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.today_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.today_table.setAlternatingRowColors(True)
        self.today_table.verticalHeader().setVisible(False)
        self.today_table.setShowGrid(True)
        
        # Modern table styling
        self.today_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                gridline-color: #F3F4F6;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px 4px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #1a237e;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
        """)
    
    def setup_records_table(self):
        """Setup attendance records table"""
        columns = ["Date", "Code", "Employee", "Time In", "Time Out", "Break", "Hours", "OT", "Late", "Status", "Actions"]
        
        self.records_table.setColumnCount(len(columns))
        self.records_table.setHorizontalHeaderLabels(columns)
        
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.records_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.records_table.setAlternatingRowColors(True)
        self.records_table.verticalHeader().setVisible(False)
        
        # Improved table styling
        self.records_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: white;
                gridline-color: #F3F4F6;
                font-size: 10px;
            }
            QTableWidget::item {
                padding: 8px 4px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #111827;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-weight: 600;
                font-size: 11px;
            }
        """)
        
        # Set Actions column width
        self.records_table.setColumnWidth(10, 150)
    
    def load_clock_employees(self):
        """Load employees for clock dropdown"""
        self.clock_employee.clear()
        employees = employee_manager.get_active_employees()
        
        if employees:
            for emp in employees:
                name = f"{emp.get('employee_code')} - {emp.get('first_name')} {emp.get('last_name')}"
                self.clock_employee.addItem(name, emp.get('employee_id'))
        
        # Update status for first employee (only if widgets exist)
        if self.clock_employee.count() > 0 and hasattr(self, 'status_indicator'):
            self.update_employee_status()
    
    def update_employee_status(self):
        """Update status indicator and button states for selected employee"""
        # Check if status_indicator exists (may not be initialized yet)
        if not hasattr(self, 'status_indicator') or self.status_indicator is None:
            return
        
        employee_id = self.clock_employee.currentData()
        if not employee_id:
            self.status_indicator.setText("Select an employee")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    background-color: #FEF3C7;
                    color: #92400E;
                    border-radius: 10px;
                    padding: 16px 28px;
                    font-size: 15px;
                    font-weight: 500;
                    min-height: 48px;
                }
            """)
            # Hide all buttons if no employee selected
            if hasattr(self, 'clock_in_btn'):
                self.clock_in_btn.setEnabled(False)
            if hasattr(self, 'clock_out_btn'):
                self.clock_out_btn.hide()
            if hasattr(self, 'clock_in_btn'):
                self.clock_in_btn.show()
            return
        
        try:
            today = datetime.now().date()
            attendance = attendance_manager.get_attendance(employee_id, today)
            
            if not attendance or not attendance.get('time_in'):
                # Not clocked in - Show "Not Clocked In" status and Clock In button
                self.status_indicator.setText("Not Clocked In")
                self.status_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #FEF3C7;
                        color: #92400E;
                        border-radius: 10px;
                        padding: 16px 28px;
                        font-size: 15px;
                        font-weight: 500;
                        min-height: 48px;
                    }
                """)
                # Show Clock In button, hide Clock Out button
                if hasattr(self, 'clock_in_btn'):
                    self.clock_in_btn.setEnabled(True)
                    self.clock_in_btn.show()
                if hasattr(self, 'clock_out_btn'):
                    self.clock_out_btn.hide()
                    
            elif attendance.get('time_in') and not attendance.get('time_out'):
                # Clocked in - Show "Currently Working" status and Break/Clock Out buttons
                time_in = attendance.get('time_in')
                if isinstance(time_in, timedelta):
                    total_seconds = int(time_in.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_str = str(time_in)[:5]
                
                self.status_indicator.setText("Currently Working")
                self.status_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #D1FAE5;
                        color: #065F46;
                        border-radius: 10px;
                        padding: 16px 28px;
                        font-size: 15px;
                        font-weight: 500;
                        min-height: 48px;
                    }
                """)
                # Hide Clock In button, show Clock Out button
                if hasattr(self, 'clock_in_btn'):
                    self.clock_in_btn.hide()
                if hasattr(self, 'clock_out_btn'):
                    self.clock_out_btn.show()
                    self.clock_out_btn.setEnabled(True)
                    
            else:
                # Already clocked out
                time_out = attendance.get('time_out')
                if isinstance(time_out, timedelta):
                    total_seconds = int(time_out.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_str = str(time_out)[:5]
                
                hours_worked = attendance.get('hours_worked', 0) or 0
                self.status_indicator.setText(f"Clocked Out - {hours_worked:.2f} hours worked")
                self.status_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #DBEAFE;
                        color: #1E40AF;
                        border-radius: 10px;
                        padding: 16px 28px;
                        font-size: 15px;
                        font-weight: 500;
                        min-height: 48px;
                    }
                """)
                # Hide all buttons if already clocked out
                if hasattr(self, 'clock_in_btn'):
                    self.clock_in_btn.hide()
                if hasattr(self, 'clock_out_btn'):
                    self.clock_out_btn.hide()
            
        except Exception as e:
            self.status_indicator.setText("Error loading status")
            self.status_indicator.setStyleSheet("""
                QLabel {
                    background-color: #FEE2E2;
                    color: #991B1B;
                    border-radius: 10px;
                    padding: 16px 28px;
                    font-size: 15px;
                    font-weight: 500;
                    min-height: 48px;
                }
            """)
    
    def load_today_attendance(self):
        """Load today's attendance records and update stats (table removed)"""
        try:
            records = attendance_manager.get_today_attendance()
            self.update_attendance_stats(records)
        except Exception as e:
            print(f"Error loading today's attendance: {e}")
    
    def update_attendance_stats(self, records):
        """Update attendance statistics cards"""
        try:
            present_count = 0
            absent_count = 0
            total_hours = 0.0
            late_count = 0
            
            if records:
                for rec in records:
                    status = rec.get('status', '')
                    if status == 'Present':
                        present_count += 1
                    elif status == 'Absent':
                        absent_count += 1
                    
                    hours = rec.get('hours_worked', 0) or 0
                    total_hours += float(hours)
                    
                    late_minutes = rec.get('late_minutes', 0) or 0
                    if late_minutes > 0:
                        late_count += 1
            
            # Update stat cards (only if they exist)
            if self.present_card:
                value_label = self.present_card.findChild(QLabel, "value")
                if value_label:
                    value_label.setText(str(present_count))
            
            if self.absent_card:
                value_label = self.absent_card.findChild(QLabel, "value")
                if value_label:
                    value_label.setText(str(absent_count))
            
            if self.total_hours_card:
                value_label = self.total_hours_card.findChild(QLabel, "value")
                if value_label:
                    value_label.setText(f"{total_hours:.1f}")
            
            if self.late_card:
                value_label = self.late_card.findChild(QLabel, "value")
                if value_label:
                    value_label.setText(str(late_count))
        except Exception as e:
            print(f"Error updating attendance stats: {e}")
    
    def populate_today_table(self, records):
        """Populate today's attendance table"""
        self.today_table.setRowCount(0)
        
        if not records:
            return
        
        for row, rec in enumerate(records):
            self.today_table.insertRow(row)
            
            self.today_table.setItem(row, 0, QTableWidgetItem(rec.get('employee_code', '')))
            self.today_table.setItem(row, 1, QTableWidgetItem(rec.get('full_name', '')))
            self.today_table.setItem(row, 2, QTableWidgetItem(rec.get('position', '')))
            
            # Time in
            time_in = rec.get('time_in')
            time_in_str = ''
            if time_in:
                if isinstance(time_in, timedelta):
                    total_seconds = int(time_in.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_in_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_in_str = str(time_in)[:5]
            self.today_table.setItem(row, 3, QTableWidgetItem(time_in_str))
            
            # Time out
            time_out = rec.get('time_out')
            time_out_str = ''
            if time_out:
                if isinstance(time_out, timedelta):
                    total_seconds = int(time_out.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_out_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_out_str = str(time_out)[:5]
            self.today_table.setItem(row, 4, QTableWidgetItem(time_out_str))
            
            # Hours
            hours = rec.get('hours_worked', 0) or 0
            self.today_table.setItem(row, 5, QTableWidgetItem(f"{hours:.2f}"))
            
            # Status - Modern badge
            status = rec.get('status', '') or '-'
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(5, 2, 5, 2)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_label = QLabel(status)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if status == 'Present':
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #10B981;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            elif status == 'Absent':
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #EF4444;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            elif status == 'Leave':
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #3B82F6;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            else:
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #6B7280;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            
            status_layout.addWidget(status_label)
            self.today_table.setCellWidget(row, 6, status_widget)
            
            self.today_table.setRowHeight(row, 60)
    
    def update_time(self):
        """Update the current time display"""
        if hasattr(self, 'time_label') and self.time_label:
            self.time_label.setText(datetime.now().strftime("%I:%M:%S %p"))
    
    def handle_time_in(self):
        """Handle time in button click with confirmation dialog and enhanced error handling"""
        employee_id = self.clock_employee.currentData()
        if not employee_id:
            from ui.components import show_toast
            show_toast(self, "Please select an employee", "warning")
            return
        
        # Check if button is disabled (already clocked in)
        if hasattr(self, 'clock_in_btn') and not self.clock_in_btn.isEnabled():
            from ui.components import show_toast
            show_toast(self, "Already clocked in today", "warning")
            return
        
        try:
            # Get employee name for confirmation
            employee = employee_manager.get_employee_by_id(employee_id)
            emp_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip() if employee else "Employee"
            emp_code = employee.get('employee_code', '') if employee else ''
            
            # Confirmation dialog
            current_time = datetime.now().strftime('%I:%M %p')
            current_date = datetime.now().strftime('%B %d, %Y')
            
            reply = QMessageBox.question(
                self,
                "Confirm Time In",
                f"Record Time In for:\n\n"
                f"Employee: {emp_code} - {emp_name}\n"
                f"Date: {current_date}\n"
                f"Time: {current_time}\n\n"
                f"Proceed with Time In?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Get current user for audit logging
            from modules.users import user_manager
            current_user = user_manager.get_current_user()
            user_id = current_user.get('user_id') if current_user else None
            
            # Check if employee already timed in today (double-check)
            today = datetime.now().date()
            existing = attendance_manager.get_attendance(employee_id, today)
            
            if existing and existing.get('time_in'):
                # Already timed in - show current status
                time_in = existing.get('time_in')
                if isinstance(time_in, timedelta):
                    total_seconds = int(time_in.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_in_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_in_str = str(time_in)[:5]
                
                from ui.components import show_toast
                show_toast(self, f"Already timed in at {time_in_str}", "warning", duration=4000)
                self.update_employee_status()
                return
            
            # Record time in
            result = attendance_manager.time_in(employee_id, user_id=user_id)
            
            if result:
                current_time_full = datetime.now().strftime('%I:%M:%S %p')
                
                # Check if late
                attendance_record = attendance_manager.get_attendance(employee_id, today)
                late_minutes = attendance_record.get('late_minutes', 0) if attendance_record else 0
                late_msg = ""
                if late_minutes and late_minutes > 0:
                    late_msg = f"\n⚠️ Late by {late_minutes} minutes"
                
                # Show success toast notification
                from ui.components import show_toast
                show_toast(
                    self, 
                    f"Time In recorded: {current_time_full}{late_msg}", 
                    "success",
                    duration=4000
                )
                
                # Refresh data and update display
                records = attendance_manager.get_today_attendance()
                self.update_attendance_stats(records)
                self.update_employee_status()
            else:
                from ui.components import show_toast
                show_toast(self, "Failed to record time in", "error", duration=4000)
                
        except Exception as e:
            from ui.components import show_toast
            show_toast(self, f"Error: {str(e)}", "error", duration=5000)
            QMessageBox.critical(
                self, 
                "System Error", 
                f"An error occurred while recording time in:\n\n{str(e)}\n\nPlease contact system administrator."
            )
    
    def handle_time_out(self):
        """Handle time out button click with confirmation dialog and enhanced error handling"""
        employee_id = self.clock_employee.currentData()
        if not employee_id:
            from ui.components import show_toast
            show_toast(self, "Please select an employee", "warning")
            return
        
        # Check if button is disabled (not clocked in)
        if hasattr(self, 'clock_out_btn') and not self.clock_out_btn.isEnabled():
            from ui.components import show_toast
            show_toast(self, "Please clock in first", "warning")
            return
        
        try:
            # Get current user for audit logging
            from modules.users import user_manager
            current_user = user_manager.get_current_user()
            user_id = current_user.get('user_id') if current_user else None
            
            # Check if employee has timed in today
            today = datetime.now().date()
            existing = attendance_manager.get_attendance(employee_id, today)
            
            if not existing or not existing.get('time_in'):
                from ui.components import show_toast
                show_toast(self, "No time in record found", "error", duration=4000)
                self.update_employee_status()
                return
            
            if existing.get('time_out'):
                # Already timed out
                time_out = existing.get('time_out')
                if isinstance(time_out, timedelta):
                    total_seconds = int(time_out.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_out_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_out_str = str(time_out)[:5]
                
                hours_worked = existing.get('hours_worked', 0) or 0
                from ui.components import show_toast
                show_toast(self, f"Already timed out at {time_out_str}", "warning", duration=4000)
                self.update_employee_status()
                return
            
            # Get employee info for confirmation
            employee = employee_manager.get_employee_by_id(employee_id)
            emp_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip() if employee else "Employee"
            emp_code = employee.get('employee_code', '') if employee else ''
            
            # Get time in for display
            time_in = existing.get('time_in')
            if isinstance(time_in, timedelta):
                total_seconds = int(time_in.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                time_in_str = f"{hours:02d}:{minutes:02d}"
            else:
                time_in_str = str(time_in)[:5]
            
            current_time = datetime.now().strftime('%I:%M %p')
            current_date = datetime.now().strftime('%B %d, %Y')
            
            # Confirmation dialog
            reply = QMessageBox.question(
                self,
                "Confirm Time Out",
                f"Record Time Out for:\n\n"
                f"Employee: {emp_code} - {emp_name}\n"
                f"Date: {current_date}\n"
                f"Time In: {time_in_str}\n"
                f"Time Out: {current_time}\n\n"
                f"Proceed with Time Out?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Record time out
            result = attendance_manager.time_out(employee_id, user_id=user_id)
            
            if result:
                current_time_full = datetime.now().strftime('%I:%M:%S %p')
                hours_worked = result.get('hours_worked', 0) or 0
                overtime_hours = result.get('overtime_hours', 0) or 0
                
                # Build toast message
                toast_msg = f"Time Out: {current_time_full} | Hours: {hours_worked:.2f}"
                if overtime_hours > 0:
                    toast_msg += f" | OT: {overtime_hours:.2f}h"
                elif hours_worked < 8:
                    undertime = 8 - hours_worked
                    toast_msg += f" | Undertime: {undertime:.2f}h"
                
                # Show success toast notification
                from ui.components import show_toast
                show_toast(self, toast_msg, "success", duration=5000)
                
                # Refresh data and update display
                records = attendance_manager.get_today_attendance()
                self.update_attendance_stats(records)
                self.update_employee_status()
            else:
                from ui.components import show_toast
                show_toast(self, "Failed to record time out", "error", duration=4000)
                
        except Exception as e:
            from ui.components import show_toast
            show_toast(self, f"Error: {str(e)}", "error", duration=5000)
            QMessageBox.critical(
                self, 
                "System Error", 
                f"An error occurred while recording time out:\n\n{str(e)}\n\nPlease contact system administrator."
            )
    
    def search_attendance(self):
        """Search attendance records"""
        employee_id = self.filter_employee.currentData()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        try:
            records = attendance_manager.get_attendance_by_date_range(employee_id, start, end)
            self.populate_records_table(records)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    def generate_attendance_report(self):
        """Generate and export attendance report"""
        employee_id = self.filter_employee.currentData()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        # Get report data
        try:
            report_data = report_manager.get_attendance_report(
                start_date=start,
                end_date=end,
                employee_id=employee_id
            )
            
            if not report_data:
                QMessageBox.warning(
                    self,
                    "No Data",
                    "No attendance records found for the selected criteria."
                )
                return
            
            # Prepare filename
            employee_name = ""
            if employee_id:
                emp = employee_manager.get_employee(employee_id)
                if emp:
                    employee_name = f"_{emp.get('employee_code', '')}"
            
            date_str = f"{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}"
            default_filename = f"attendance_report{employee_name}_{date_str}"
            
            # Export to PDF
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Attendance Report",
                default_filename + ".pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                    headers = [
                        "Date", "Code", "Employee", "Position", "Department",
                        "Time In", "Time Out", "Hours", "OT", "Late", "Status", "Notes"
                    ]
                    
                    # Format data for PDF
                    pdf_data = []
                    for record in report_data:
                        pdf_data.append([
                            record.get('attendance_date').strftime('%Y-%m-%d') if record.get('attendance_date') else '',
                            record.get('employee_code', ''),
                            record.get('employee_name', ''),
                            record.get('position', ''),
                            record.get('department', ''),
                            str(record.get('time_in', ''))[:5] if record.get('time_in') else '',
                            str(record.get('time_out', ''))[:5] if record.get('time_out') else '',
                            f"{record.get('hours_worked', 0) or 0:.2f}",
                            f"{record.get('overtime_hours', 0) or 0:.2f}",
                            str(record.get('late_minutes', 0) or 0),
                            record.get('status', ''),
                            record.get('remarks', '') or ''
                        ])
                    
                    title = f"Attendance Report ({start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')})"
                    if employee_id:
                        emp = employee_manager.get_employee(employee_id)
                        if emp:
                            title += f" - {emp.get('employee_code', '')}"
                    
                    result = report_manager.export_to_pdf(
                        title=title,
                        data=pdf_data,
                        headers=headers,
                        filename=filename,
                        orientation='landscape'
                    )
                    
                    if result:
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Attendance report exported successfully!\n\nFile: {filename}\n\nRecords: {len(pdf_data)}"
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            "Failed to export PDF. ReportLab library may not be installed.\n\nInstall with: pip install reportlab"
                        )
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def export_to_pdf(self):
        """Export current filtered attendance records to PDF"""
        try:
            employee_id = self.filter_employee.currentData()
            start = self.start_date.date().toPyDate()
            end = self.end_date.date().toPyDate()
            
            # Get report data
            report_data = report_manager.get_attendance_report(start, end, employee_id)
            
            if not report_data:
                from ui.components import show_toast
                show_toast(self, "No data to export", "warning")
                return
            
            # Get save location
            default_filename = f"attendance_{start}_{end}"
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Attendance to PDF",
                default_filename + ".pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                headers = [
                    "Date", "Code", "Employee", "Position", "Department",
                    "Time In", "Time Out", "Hours", "OT", "Late", "Status", "Notes"
                ]
                
                pdf_data = []
                for record in report_data:
                    pdf_data.append([
                        record.get('attendance_date').strftime('%Y-%m-%d') if record.get('attendance_date') else '',
                        record.get('employee_code', ''),
                        record.get('employee_name', ''),
                        record.get('position', ''),
                        record.get('department', ''),
                        str(record.get('time_in', ''))[:5] if record.get('time_in') else '',
                        str(record.get('time_out', ''))[:5] if record.get('time_out') else '',
                        f"{record.get('hours_worked', 0) or 0:.2f}",
                        f"{record.get('overtime_hours', 0) or 0:.2f}",
                        str(record.get('late_minutes', 0) or 0),
                        record.get('status', ''),
                        record.get('remarks', '') or ''
                    ])
                
                title = f"Attendance Report ({start} to {end})"
                result = report_manager.export_to_pdf(
                    title=title,
                    data=pdf_data,
                    headers=headers,
                    filename=filename,
                    orientation='landscape'
                )
                
                if result:
                    from ui.components import show_toast
                    show_toast(self, f"Exported {len(pdf_data)} records to PDF", "success", duration=4000)
                else:
                    from ui.components import show_toast
                    show_toast(self, "PDF export failed. Install ReportLab: pip install reportlab", "error", duration=5000)
                    
        except Exception as e:
            from ui.components import show_toast
            show_toast(self, f"Error: {str(e)}", "error", duration=5000)
    
    def send_daily_email_summary(self):
        """Send daily attendance summary via email"""
        try:
            from modules.email_service import email_service
            from modules.employees import employee_manager
            from PyQt6.QtWidgets import QInputDialog
            
            # Get recipient email
            email, ok = QInputDialog.getText(
                self,
                "Email Daily Summary",
                "Enter recipient email address:",
                text="admin@company.com"
            )
            
            if not ok or not email:
                return
            
            # Get today's attendance data
            today = datetime.now().date()
            records = attendance_manager.get_today_attendance()
            
            # Build summary data
            total_employees = len(employee_manager.get_all_employees())
            present_count = sum(1 for r in records if r.get('status') == 'Present')
            absent_count = sum(1 for r in records if r.get('status') == 'Absent')
            leave_count = sum(1 for r in records if r.get('status') == 'Leave')
            late_count = sum(1 for r in records if (r.get('late_minutes', 0) or 0) > 0)
            total_hours = sum((r.get('hours_worked', 0) or 0) for r in records)
            total_overtime = sum((r.get('overtime_hours', 0) or 0) for r in records)
            
            # Build attendance list
            attendance_list = []
            for record in records:
                employee = employee_manager.get_employee_by_id(record.get('employee_id'))
                emp_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip() if employee else "Unknown"
                
                attendance_list.append({
                    'employee_name': emp_name,
                    'status': record.get('status', 'Unknown'),
                    'time_in': record.get('time_in'),
                    'time_out': record.get('time_out'),
                    'hours_worked': record.get('hours_worked', 0) or 0
                })
            
            summary_data = {
                'total_employees': total_employees,
                'present_count': present_count,
                'absent_count': absent_count,
                'leave_count': leave_count,
                'late_count': late_count,
                'total_hours': total_hours,
                'total_overtime': total_overtime,
                'attendance_list': attendance_list
            }
            
            # Send email
            result = email_service.send_daily_attendance_summary(email, summary_data, today)
            
            if result:
                from ui.components import show_toast
                show_toast(self, f"Daily summary sent to {email}", "success", duration=4000)
            else:
                from ui.components import show_toast
                show_toast(
                    self, 
                    "Email failed. Configure SMTP settings (SENDER_EMAIL, SENDER_PASSWORD)", 
                    "error", 
                    duration=5000
                )
                
        except Exception as e:
            from ui.components import show_toast
            show_toast(self, f"Error: {str(e)}", "error", duration=5000)
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")
    
    def populate_records_table(self, records):
        """Populate attendance records table"""
        self.records_table.setRowCount(0)
        
        if not records:
            return
        
        for row, rec in enumerate(records):
            self.records_table.insertRow(row)
            
            # Date
            date = rec.get('attendance_date', '')
            if isinstance(date, datetime):
                date = date.strftime('%Y-%m-%d')
            self.records_table.setItem(row, 0, QTableWidgetItem(str(date)))
            
            self.records_table.setItem(row, 1, QTableWidgetItem(rec.get('employee_code', '')))
            self.records_table.setItem(row, 2, QTableWidgetItem(rec.get('full_name', '')))
            
            # Times
            time_in = rec.get('time_in')
            if time_in:
                if isinstance(time_in, timedelta):
                    total_seconds = int(time_in.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_in = f"{hours:02d}:{minutes:02d}"
                else:
                    time_in = str(time_in)[:5]
            self.records_table.setItem(row, 3, QTableWidgetItem(time_in or ''))
            
            time_out = rec.get('time_out')
            if time_out:
                if isinstance(time_out, timedelta):
                    total_seconds = int(time_out.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time_out = f"{hours:02d}:{minutes:02d}"
                else:
                    time_out = str(time_out)[:5]
            self.records_table.setItem(row, 4, QTableWidgetItem(time_out or ''))
            
            # Calculate break minutes (60 minutes if total hours > 4, otherwise 0)
            hours_worked = rec.get('hours_worked', 0) or 0
            break_minutes = 60 if hours_worked > 4 else 0
            self.records_table.setItem(row, 5, QTableWidgetItem(str(break_minutes)))
            
            self.records_table.setItem(row, 6, QTableWidgetItem(f"{hours_worked:.2f}"))
            self.records_table.setItem(row, 7, QTableWidgetItem(f"{rec.get('overtime_hours', 0) or 0:.2f}"))
            self.records_table.setItem(row, 8, QTableWidgetItem(str(rec.get('late_minutes', 0) or 0)))
            
            # Status - Modern badge widget
            status = rec.get('status', '')
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(5, 2, 5, 2)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_label = QLabel(status)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Modern badge styling based on status
            if status == 'Present':
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #10B981;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            elif status == 'Absent':
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #EF4444;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            elif status == 'Leave':
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #3B82F6;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            else:
                status_label.setStyleSheet("""
                    QLabel {
                        background-color: #F59E0B;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 70px;
                    }
                """)
            
            status_layout.addWidget(status_label)
            self.records_table.setCellWidget(row, 9, status_widget)
            
            # Actions - Improved with modern styling
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(8, 4, 8, 4)
            actions_layout.setSpacing(8)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # View/Details button
            view_btn = QPushButton("👁️ View")
            view_btn.setFixedSize(70, 32)
            view_btn.setToolTip("View Details")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0055FF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #0033CC;
                }
            """)
            view_btn.clicked.connect(lambda checked, r=rec: self.view_attendance_details(r))
            
            # Edit button
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setFixedSize(70, 32)
            edit_btn.setToolTip("Edit Record")
            edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #F59E0B;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #D97706;
                }
            """)
            edit_btn.clicked.connect(lambda checked, r=rec: self.edit_attendance(r))
            
            # Delete button
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedSize(80, 32)
            delete_btn.setToolTip("Delete Record")
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            """)
            delete_btn.clicked.connect(lambda checked, r=rec: self.delete_attendance(r))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.records_table.setCellWidget(row, 10, actions_widget)
            self.records_table.setRowHeight(row, 60)  # Increased for better spacing
    
    def add_attendance(self):
        """Open dialog to add attendance"""
        dialog = AttendanceDialog(self)
        if dialog.exec():
            self.search_attendance()
            # Update stats after adding attendance
            try:
                records = attendance_manager.get_today_attendance()
                self.update_attendance_stats(records)
            except Exception as e:
                print(f"Error updating stats: {e}")
    
    def view_attendance_details(self, record):
        """View attendance record details"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Attendance Details")
        dialog.setFixedSize(450, 400)
        dialog.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Attendance Record Details")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a237e; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Details form
        form = QFormLayout()
        form.setSpacing(12)
        
        # Format date
        date = record.get('attendance_date', '')
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
        
        # Format times
        time_in = record.get('time_in', '')
        time_out = record.get('time_out', '')
        if time_in:
            if isinstance(time_in, datetime):
                time_in = time_in.strftime('%I:%M %p')
            else:
                time_in = str(time_in)[:5]
        if time_out:
            if isinstance(time_out, datetime):
                time_out = time_out.strftime('%I:%M %p')
            else:
                time_out = str(time_out)[:5]
        
        form.addRow("Date:", QLabel(str(date)))
        form.addRow("Employee Code:", QLabel(record.get('employee_code', '')))
        form.addRow("Employee Name:", QLabel(record.get('employee_name', '')))
        form.addRow("Time In:", QLabel(time_in or 'N/A'))
        form.addRow("Time Out:", QLabel(time_out or 'N/A'))
        form.addRow("Hours Worked:", QLabel(f"{record.get('hours_worked', 0) or 0:.2f}"))
        form.addRow("Overtime Hours:", QLabel(f"{record.get('overtime_hours', 0) or 0:.2f}"))
        form.addRow("Late Minutes:", QLabel(str(record.get('late_minutes', 0) or 0)))
        
        # Status with color
        status_label = QLabel(record.get('status', ''))
        status = record.get('status', '')
        if status == 'Present':
            status_label.setStyleSheet("color: #10B981; font-weight: bold;")
        elif status == 'Absent':
            status_label.setStyleSheet("color: #EF4444; font-weight: bold;")
        else:
            status_label.setStyleSheet("color: #F59E0B; font-weight: bold;")
        form.addRow("Status:", status_label)
        
        remarks = record.get('remarks', '') or 'None'
        remarks_label = QLabel(remarks)
        remarks_label.setWordWrap(True)
        form.addRow("Remarks:", remarks_label)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setStyleSheet(Styles.BTN_PRIMARY)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def edit_attendance(self, record):
        """Open dialog to edit attendance"""
        dialog = AttendanceDialog(self, record)
        if dialog.exec():
            self.search_attendance()
            # Update stats after adding attendance
            try:
                records = attendance_manager.get_today_attendance()
                self.update_attendance_stats(records)
            except Exception as e:
                print(f"Error updating stats: {e}")
    
    def delete_attendance(self, record):
        """Delete attendance record"""
        # Format date for display
        date = record.get('attendance_date', '')
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')
        elif hasattr(date, 'strftime'):
            date = date.strftime('%Y-%m-%d')
        
        employee_name = record.get('employee_name') or record.get('full_name', 'Unknown')
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this attendance record?\n\n"
            f"Date: {date}\n"
            f"Employee: {employee_name}\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                attendance_id = record.get('attendance_id')
                if attendance_id:
                    # Use attendance manager to delete (includes audit logging)
                    from modules.users import user_manager
                    current_user = user_manager.get_current_user()
                    user_id = current_user.get('user_id') if current_user else None
                    
                    result = attendance_manager.delete_attendance(attendance_id, user_id)
                    
                    if result:
                        QMessageBox.information(self, "Success", "Attendance record deleted successfully.")
                        self.search_attendance()
                        self.load_today_attendance()
                    else:
                        QMessageBox.warning(self, "Error", "Failed to delete record.")
                else:
                    QMessageBox.warning(self, "Error", "Cannot delete: Invalid record ID.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {str(e)}")

