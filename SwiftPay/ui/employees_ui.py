"""
SwiftPay Employees Management Page
CRUD interface for employee records
"""

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QDateEdit, QDoubleSpinBox,
    QMessageBox, QHeaderView, QScrollArea, QSpacerItem, QSizePolicy,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate, QRegularExpression
from PyQt6.QtGui import QFont, QColor, QRegularExpressionValidator

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles
from modules.employees import employee_manager


class EmployeeDialog(QDialog):
    """
    Dialog for adding/editing employee records.
    """
    
    def __init__(self, parent=None, employee_data=None):
        super().__init__(parent)
        self.employee_data = employee_data
        self.is_edit = employee_data is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_employee_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        title = "Edit Employee" if self.is_edit else "Add New Employee"
        self.setWindowTitle(title)
        self.setFixedSize(600, 700)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a237e;")
        layout.addWidget(title_label)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Personal Information section
        section1 = QLabel("Personal Information")
        section1.setStyleSheet("font-weight: bold; color: #1a237e; font-size: 14px; margin-top: 10px;")
        form_layout.addRow(section1)
        
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Enter first name")
        form_layout.addRow("First Name *:", self.first_name)
        
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Enter last name")
        form_layout.addRow("Last Name *:", self.last_name)
        
        self.email = QLineEdit()
        self.email.setPlaceholderText("email@example.com")
        form_layout.addRow("Email:", self.email)
        
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("09XX XXX XXXX")
        self.phone.setMaxLength(11)
        # Only allow digits (0-9), max 11 characters
        phone_regex = QRegularExpression("^[0-9]{0,11}$")
        phone_validator = QRegularExpressionValidator(phone_regex, self)
        self.phone.setValidator(phone_validator)
        form_layout.addRow("Phone:", self.phone)
        
        self.address = QLineEdit()
        self.address.setPlaceholderText("Enter address")
        form_layout.addRow("Address:", self.address)
        
        # Employment Information section
        section2 = QLabel("Employment Information")
        section2.setStyleSheet("font-weight: bold; color: #1a237e; font-size: 14px; margin-top: 20px;")
        form_layout.addRow(section2)
        
        self.position = QLineEdit()
        self.position.setPlaceholderText("Enter position/job title")
        form_layout.addRow("Position *:", self.position)
        
        self.department = QComboBox()
        self.department.setEditable(True)
        self.department.addItems([
            "", "IT Department", "Human Resources", "Finance",
            "Operations", "Sales", "Marketing", "Admin"
        ])
        form_layout.addRow("Department:", self.department)
        
        self.date_hired = QDateEdit()
        self.date_hired.setDate(QDate.currentDate())
        self.date_hired.setCalendarPopup(True)
        form_layout.addRow("Date Hired:", self.date_hired)
        
        self.status = QComboBox()
        self.status.addItems(["Active", "Inactive"])
        self.status.setCurrentText("Active")  # Default to Active for new employees
        form_layout.addRow("Status *:", self.status)
        
        # Compensation section
        section3 = QLabel("Compensation")
        section3.setStyleSheet("font-weight: bold; color: #1a237e; font-size: 14px; margin-top: 20px;")
        form_layout.addRow(section3)
        
        self.rate_per_hour = QDoubleSpinBox()
        self.rate_per_hour.setRange(0, 99999.99)
        self.rate_per_hour.setDecimals(2)
        self.rate_per_hour.setPrefix("₱ ")
        self.rate_per_hour.valueChanged.connect(self.calculate_daily_rate)
        form_layout.addRow("Rate/Hour *:", self.rate_per_hour)
        
        self.daily_rate = QDoubleSpinBox()
        self.daily_rate.setRange(0, 999999.99)
        self.daily_rate.setDecimals(2)
        self.daily_rate.setPrefix("₱ ")
        form_layout.addRow("Daily Rate:", self.daily_rate)
        
        self.allowance = QDoubleSpinBox()
        self.allowance.setRange(0, 999999.99)
        self.allowance.setDecimals(2)
        self.allowance.setPrefix("₱ ")
        form_layout.addRow("Allowance:", self.allowance)
        
        # Deductions section
        section4 = QLabel("Deductions")
        section4.setStyleSheet("font-weight: bold; color: #1a237e; font-size: 14px; margin-top: 20px;")
        form_layout.addRow(section4)
        
        self.sss = QDoubleSpinBox()
        self.sss.setRange(0, 99999.99)
        self.sss.setDecimals(2)
        self.sss.setPrefix("₱ ")
        form_layout.addRow("SSS:", self.sss)
        
        self.philhealth = QDoubleSpinBox()
        self.philhealth.setRange(0, 99999.99)
        self.philhealth.setDecimals(2)
        self.philhealth.setPrefix("₱ ")
        form_layout.addRow("PhilHealth:", self.philhealth)
        
        self.pagibig = QDoubleSpinBox()
        self.pagibig.setRange(0, 99999.99)
        self.pagibig.setDecimals(2)
        self.pagibig.setPrefix("₱ ")
        form_layout.addRow("Pag-IBIG:", self.pagibig)
        
        self.tax = QDoubleSpinBox()
        self.tax.setRange(0, 99999.99)
        self.tax.setDecimals(2)
        self.tax.setPrefix("₱ ")
        form_layout.addRow("Tax:", self.tax)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setStyleSheet(Styles.BTN_OUTLINE)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("💾 Save Employee")
        save_btn.setMinimumHeight(45)
        save_btn.setStyleSheet(Styles.BTN_PRIMARY)
        save_btn.clicked.connect(self.save_employee)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def calculate_daily_rate(self, value):
        """Auto-calculate daily rate based on hourly rate (8 hours/day)"""
        self.daily_rate.setValue(value * 8)
    
    def load_employee_data(self):
        """Load existing employee data into form"""
        if not self.employee_data:
            return
        
        self.first_name.setText(self.employee_data.get('first_name', ''))
        self.last_name.setText(self.employee_data.get('last_name', ''))
        self.email.setText(self.employee_data.get('email', ''))
        self.phone.setText(self.employee_data.get('phone', ''))
        self.address.setText(self.employee_data.get('address', ''))
        self.position.setText(self.employee_data.get('position', ''))
        self.department.setCurrentText(self.employee_data.get('department', ''))
        
        if self.employee_data.get('date_hired'):
            date = self.employee_data['date_hired']
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            self.date_hired.setDate(QDate(date.year, date.month, date.day))
        
        self.status.setCurrentText(self.employee_data.get('status', 'Active'))
        self.rate_per_hour.setValue(float(self.employee_data.get('rate_per_hour', 0)))
        self.daily_rate.setValue(float(self.employee_data.get('daily_rate', 0)))
        self.allowance.setValue(float(self.employee_data.get('allowance', 0)))
        self.sss.setValue(float(self.employee_data.get('sss_deduction', 0)))
        self.philhealth.setValue(float(self.employee_data.get('philhealth_deduction', 0)))
        self.pagibig.setValue(float(self.employee_data.get('pagibig_deduction', 0)))
        self.tax.setValue(float(self.employee_data.get('tax_deduction', 0)))
    
    def get_form_data(self):
        """Get all form data as dictionary"""
        return {
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'email': self.email.text().strip(),
            'phone': self.phone.text().strip(),
            'address': self.address.text().strip(),
            'position': self.position.text().strip(),
            'department': self.department.currentText().strip(),
            'date_hired': self.date_hired.date().toPyDate(),
            'status': self.status.currentText(),
            'rate_per_hour': self.rate_per_hour.value(),
            'daily_rate': self.daily_rate.value(),
            'allowance': self.allowance.value(),
            'sss_deduction': self.sss.value(),
            'philhealth_deduction': self.philhealth.value(),
            'pagibig_deduction': self.pagibig.value(),
            'tax_deduction': self.tax.value()
        }
    
    def save_employee(self):
        """Validate and save employee data"""
        data = self.get_form_data()
        
        # Validate required fields
        is_valid, error = employee_manager.validate_employee_data(data, self.is_edit)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error)
            return
        
        try:
            if self.is_edit:
                result = employee_manager.update_employee(
                    self.employee_data['employee_id'],
                    data
                )
                if result >= 0:
                    QMessageBox.information(self, "Success", "Employee updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update employee.")
            else:
                result = employee_manager.create_employee(data)
                if result:
                    QMessageBox.information(self, "Success", "Employee added successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add employee.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class EmployeesPage(QWidget):
    """
    Employee management page with table view and CRUD operations.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_employees()
    
    def init_ui(self):
        """Initialize the page UI"""
        # Set background color for the page
        self.setStyleSheet("background-color: #F8F9FA;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)
        
        # Header section with title, subtitle, and action buttons
        header_container = QFrame()
        header_container.setStyleSheet("background-color: transparent;")
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        # Title and subtitle row
        title_row = QHBoxLayout()
        title_row.setSpacing(15)
        
        title_section = QVBoxLayout()
        title_section.setSpacing(6)
        
        title_label = QLabel("Employee Management")
        title_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: 700; 
            color: #111827;
            letter-spacing: -0.5px;
        """)
        title_section.addWidget(title_label)
        
        subtitle_label = QLabel("Manage your workforce efficiently")
        subtitle_label.setStyleSheet("""
            font-size: 15px; 
            color: #6B7280;
            font-weight: 400;
        """)
        title_section.addWidget(subtitle_label)
        
        title_row.addLayout(title_section)
        title_row.addStretch()
        
        # Action buttons
        add_btn = QPushButton("➕ Add Employee")
        add_btn.setMinimumHeight(48)
        add_btn.setMinimumWidth(170)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a237e;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #0d1b5e;
            }
            QPushButton:pressed {
                background-color: #0a1647;
            }
        """)
        add_btn.clicked.connect(self.add_employee)
        title_row.addWidget(add_btn)
        
        header_layout.addLayout(title_row)
        layout.addWidget(header_container)
        
        # White card container for employee list with shadow effect
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #E5E7EB;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(20)
        
        # Card header with employee count and search
        card_header = QHBoxLayout()
        card_header.setSpacing(15)
        
        self.employee_count_label = QLabel("Employees (0)")
        self.employee_count_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: 700; 
            color: #111827;
            letter-spacing: -0.3px;
        """)
        card_header.addWidget(self.employee_count_label)
        card_header.addStretch()
        
        # Enhanced search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search employees by name, email, or department...")
        self.search_input.setMinimumWidth(380)
        self.search_input.setMinimumHeight(44)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #F9FAFB;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
                color: #111827;
            }
            QLineEdit:focus {
                border: 2px solid #1a237e;
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
        """)
        self.search_input.textChanged.connect(self.filter_employees)
        card_header.addWidget(self.search_input)
        
        card_layout.addLayout(card_header)
        
        # Table with improved styling
        self.table = QTableWidget()
        self.setup_table()
        card_layout.addWidget(self.table, 1)
        
        # Add empty state message (will be shown/hidden based on data)
        self.empty_state_label = QLabel("No employees found. Click 'Add Employee' to get started.")
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setStyleSheet("""
            QLabel {
                color: #9CA3AF;
                font-size: 15px;
                padding: 40px;
                background-color: #F9FAFB;
                border-radius: 12px;
                border: 2px dashed #E5E7EB;
            }
        """)
        self.empty_state_label.hide()
        card_layout.addWidget(self.empty_state_label)
    
        layout.addWidget(card, 1)
    
    def setup_table(self):
        """Setup the employees table"""
        columns = [
            "#", "Name", "Email", "Department", "Position", "Salary", "Status", "Actions"
        ]
        
        self.table.setColumnCount(len(columns))
        
        # Create header items with proper alignment and uppercase text for visibility
        alignments = [
            Qt.AlignmentFlag.AlignCenter,  # #
            Qt.AlignmentFlag.AlignLeft,    # Name
            Qt.AlignmentFlag.AlignLeft,    # Email
            Qt.AlignmentFlag.AlignLeft,    # Department
            Qt.AlignmentFlag.AlignLeft,    # Position
            Qt.AlignmentFlag.AlignRight,   # Salary
            Qt.AlignmentFlag.AlignCenter,  # Status
            Qt.AlignmentFlag.AlignCenter   # Actions
        ]
        
        for col, (col_name, alignment) in enumerate(zip(columns, alignments)):
            # Create header item with proper styling
            header_item = QTableWidgetItem(col_name)
            header_item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
            # Set font to make it bold and larger
            font = QFont("Segoe UI", 12, QFont.Weight.Bold)
            header_item.setFont(font)
            self.table.setHorizontalHeaderItem(col, header_item)
        
        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # # column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Email
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Department
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Position
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Salary
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Status
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)  # Actions
        
        self.table.setColumnWidth(0, 50)   # # column
        self.table.setColumnWidth(5, 120)  # Salary
        self.table.setColumnWidth(6, 100)  # Status
        self.table.setColumnWidth(7, 150)  # Actions
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)  # Enable alternating colors
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)  # Show grid for better visibility
        
        # Set header height to make it more visible
        header = self.table.horizontalHeader()
        header.setDefaultSectionSize(50)  # Make header taller
        header.setMinimumHeight(50)
        header.setVisible(True)  # Ensure header is visible
        
        # Simple and clean table styling
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                background-color: white;
                gridline-color: #F3F4F6;
                font-size: 13px;
                selection-background-color: #EFF6FF;
                selection-color: #1E40AF;
            }
            QTableWidget::item {
                padding: 14px 10px;
                border: none;
                border-bottom: 1px solid #F3F4F6;
            }
            QTableWidget::item:selected {
                background-color: #EFF6FF;
                color: #1E40AF;
            }
            QTableWidget::item:hover {
                background-color: #F9FAFB;
            }
            QHeaderView {
                background-color: #F8F9FA;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                color: #374151;
                padding: 12px 10px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                border-right: 1px solid #E5E7EB;
                font-weight: 600;
                font-size: 11px;
            }
            QHeaderView::section:first {
                border-left: none;
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-right: none;
                border-top-right-radius: 10px;
            }
            QHeaderView::section:hover {
                background-color: #F1F5F9;
            }
        """)
    
    def load_employees(self):
        """Load employees from database"""
        try:
            employees = employee_manager.get_all_employees()
            self.populate_table(employees)
            self.update_employee_count(len(employees))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load employees: {str(e)}")
    
    def update_employee_count(self, count):
        """Update the employee count label"""
        self.employee_count_label.setText(f"Employees ({count})")
    
    def populate_table(self, employees):
        """Populate table with employee data"""
        self.table.setRowCount(0)
        
        # Show/hide empty state
        if not employees:
            self.empty_state_label.show()
            self.table.hide()
            return
        else:
            self.empty_state_label.hide()
            self.table.show()
        
        for row, emp in enumerate(employees):
            self.table.insertRow(row)
            
            # Row number
            row_num_item = QTableWidgetItem(str(row + 1))
            row_num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            row_num_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            row_num_item.setForeground(QColor("#6B7280"))
            self.table.setItem(row, 0, row_num_item)
            
            # Name
            name = emp.get('full_name', f"{emp.get('first_name', '')} {emp.get('last_name', '')}")
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
            name_item.setForeground(QColor("#111827"))
            self.table.setItem(row, 1, name_item)
            
            # Email
            email = emp.get('email', '')
            email_item = QTableWidgetItem(email if email else 'N/A')
            email_item.setForeground(QColor("#6B7280"))
            email_item.setFont(QFont("Segoe UI", 11))
            self.table.setItem(row, 2, email_item)
            
            # Department
            dept = emp.get('department', '')
            dept_item = QTableWidgetItem(dept if dept else 'N/A')
            dept_item.setFont(QFont("Segoe UI", 11))
            dept_item.setForeground(QColor("#374151"))
            self.table.setItem(row, 3, dept_item)
            
            # Position
            position = emp.get('position', '')
            pos_item = QTableWidgetItem(position if position else 'N/A')
            pos_item.setFont(QFont("Segoe UI", 11))
            pos_item.setForeground(QColor("#374151"))
            self.table.setItem(row, 4, pos_item)
            
            # Salary (using daily_rate * 22 working days as monthly estimate)
            daily_rate = float(emp.get('daily_rate', 0))
            monthly_salary = daily_rate * 22  # Approximate monthly salary
            salary_item = QTableWidgetItem(f"₱{monthly_salary:,.0f}")
            salary_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            salary_item.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
            salary_item.setForeground(QColor("#059669"))
            self.table.setItem(row, 5, salary_item)
            
            # Status - Simple colored square badge (no text)
            status = emp.get('status', 'Active')
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_indicator = QLabel("")
            status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Simple square badge - Green for Active, Orange for Inactive
            if status == 'Active':
                status_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #10B981;
                        border-radius: 4px;
                        min-width: 20px;
                        max-width: 20px;
                        min-height: 20px;
                        max-height: 20px;
                    }
                """)
            else:
                status_indicator.setStyleSheet("""
                    QLabel {
                        background-color: #F59E0B;
                        border-radius: 4px;
                        min-width: 20px;
                        max-width: 20px;
                        min-height: 20px;
                        max-height: 20px;
                    }
                """)
            status_indicator.setToolTip(status)  # Show status on hover
            status_layout.addWidget(status_indicator)
            
            self.table.setCellWidget(row, 6, status_widget)
            
            # Actions - Simple and clean text buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(6, 4, 6, 4)
            actions_layout.setSpacing(6)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # View button - Simple text button
            view_btn = QPushButton("👁️ View")
            view_btn.setFixedSize(50, 28)
            view_btn.setToolTip("View Employee Details")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #1D4ED8;
                }
                QPushButton:pressed {
                    background-color: #1E40AF;
                }
            """)
            view_btn.clicked.connect(lambda checked, e=emp: self.view_employee_details(e))
            
            # Edit button - Simple text button
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setFixedSize(50, 28)
            edit_btn.setToolTip("Edit Employee")
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
                QPushButton:pressed {
                    background-color: #B45309;
                }
            """)
            edit_btn.clicked.connect(lambda checked, e=emp: self.edit_employee(e))
            
            # Delete button - Simple text button
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedSize(50, 28)
            delete_btn.setToolTip("Delete Employee")
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
                QPushButton:pressed {
                    background-color: #B91C1C;
                }
            """)
            delete_btn.clicked.connect(lambda checked, e=emp: self.delete_employee(e))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 7, actions_widget)
            
            # Set row height for better spacing
            self.table.setRowHeight(row, 64)
    
    
    def filter_employees(self):
        """Filter employees based on search"""
        search_term = self.search_input.text().strip()
        
        employees = employee_manager.get_all_employees(
            search_term=search_term if search_term else None
        )
        self.populate_table(employees)
        self.update_employee_count(len(employees))
    
    def add_employee(self):
        """Open dialog to add new employee"""
        dialog = EmployeeDialog(self)
        if dialog.exec():
            self.load_employees()
    
    def edit_employee(self, employee):
        """Open dialog to edit employee"""
        # Get full employee data
        emp_data = employee_manager.get_employee_by_id(employee['employee_id'])
        if emp_data:
            dialog = EmployeeDialog(self, emp_data)
            if dialog.exec():
                self.load_employees()
    
    def view_employee_details(self, employee):
        """View employee details in a modern dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QScrollArea
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Employee Details")
        dialog.setFixedSize(650, 700)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }
        """)
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 1px solid #E5E7EB;
            }
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 25, 30, 25)
        header_layout.setSpacing(8)
        
        title = QLabel("Employee Information")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: 700; 
            color: #111827;
            letter-spacing: -0.5px;
        """)
        header_layout.addWidget(title)
        
        # Employee name and code
        name_code_layout = QHBoxLayout()
        name_code_layout.setSpacing(12)
        
        full_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip()
        name_label = QLabel(full_name)
        name_label.setStyleSheet("""
            font-size: 16px; 
            font-weight: 600; 
            color: #6B7280;
        """)
        name_code_layout.addWidget(name_label)
        
        employee_code = employee.get('employee_code', '')
        if employee_code:
            code_label = QLabel(f"• {employee_code}")
            code_label.setStyleSheet("""
                font-size: 14px; 
                color: #9CA3AF;
            """)
            name_code_layout.addWidget(code_label)
        
        name_code_layout.addStretch()
        
        # Status badge - Pill-shaped matching table design
        status = employee.get('status', 'Active')
        status_label = QLabel(status)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if status == 'Active':
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #10B981;
                    color: white;
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 60px;
                    max-width: 80px;
                }
            """)
        else:
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #F59E0B;
                    color: white;
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 60px;
                    max-width: 80px;
                }
            """)
        name_code_layout.addWidget(status_label)
        
        header_layout.addLayout(name_code_layout)
        main_layout.addWidget(header)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #F8F9FA;
            }
            QScrollBar:vertical {
                border: none;
                background: #F3F4F6;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Helper function to create info section
        def create_section(title_text, items):
            section_frame = QFrame()
            section_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #E5E7EB;
                }
            """)
            section_layout = QVBoxLayout(section_frame)
            section_layout.setContentsMargins(20, 18, 20, 18)
            section_layout.setSpacing(16)
            
            section_title = QLabel(title_text)
            section_title.setStyleSheet("""
                font-size: 14px;
                font-weight: 600;
                color: #111827;
                margin-bottom: 4px;
            """)
            section_layout.addWidget(section_title)
            
            form = QFormLayout()
            form.setSpacing(12)
            form.setContentsMargins(0, 0, 0, 0)
            
            for label, value in items:
                label_widget = QLabel(label)
                label_widget.setStyleSheet("""
                    color: #6B7280;
                    font-size: 13px;
                    font-weight: 500;
                """)
                
                value_widget = QLabel(str(value))
                value_widget.setStyleSheet("""
                    color: #111827;
                    font-size: 14px;
                    font-weight: 600;
                """)
                value_widget.setWordWrap(True)
                
                form.addRow(label_widget, value_widget)
            
            section_layout.addLayout(form)
            return section_frame
        
        # Personal Information Section
        personal_items = [
            ("Employee Code:", employee.get('employee_code', 'N/A')),
            ("First Name:", employee.get('first_name', 'N/A')),
            ("Last Name:", employee.get('last_name', 'N/A')),
            ("Email:", employee.get('email', 'N/A')),
            ("Phone:", employee.get('phone', '') or 'N/A'),
            ("Address:", employee.get('address', '') or 'N/A'),
        ]
        content_layout.addWidget(create_section("👤 Personal Information", personal_items))
        
        # Employment Information Section
        date_hired = employee.get('date_hired', '')
        if date_hired:
            if hasattr(date_hired, 'strftime'):
                date_hired_str = date_hired.strftime('%Y-%m-%d')
            else:
                date_hired_str = str(date_hired)
        else:
            date_hired_str = 'N/A'
        
        employment_items = [
            ("Department:", employee.get('department', 'N/A')),
            ("Position:", employee.get('position', 'N/A')),
            ("Status:", employee.get('status', 'Active')),
            ("Date Hired:", date_hired_str),
        ]
        content_layout.addWidget(create_section("💼 Employment Information", employment_items))
        
        # Compensation Section
        daily_rate = float(employee.get('daily_rate', 0))
        rate_per_hour = float(employee.get('rate_per_hour', 0))
        monthly_estimate = daily_rate * 22
        
        compensation_items = [
            ("Rate per Hour:", f"₱{rate_per_hour:,.2f}"),
            ("Daily Rate:", f"₱{daily_rate:,.2f}"),
            ("Monthly Estimate:", f"₱{monthly_estimate:,.2f}"),
        ]
        content_layout.addWidget(create_section("💰 Compensation", compensation_items))
        
        # Benefits & Deductions Section
        allowance = float(employee.get('allowance', 0))
        sss = float(employee.get('sss_deduction', 0) or employee.get('sss', 0))
        philhealth = float(employee.get('philhealth_deduction', 0) or employee.get('philhealth', 0))
        pagibig = float(employee.get('pagibig_deduction', 0) or employee.get('pagibig', 0))
        tax = float(employee.get('tax_deduction', 0) or employee.get('tax', 0))
        
        benefits_items = [
            ("Allowance:", f"₱{allowance:,.2f}"),
            ("SSS:", f"₱{sss:,.2f}"),
            ("PhilHealth:", f"₱{philhealth:,.2f}"),
            ("Pag-IBIG:", f"₱{pagibig:,.2f}"),
            ("Tax:", f"₱{tax:,.2f}"),
        ]
        content_layout.addWidget(create_section("📋 Benefits & Deductions", benefits_items))
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll, 1)
        
        # Footer with close button
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-top: 1px solid #E5E7EB;
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 20, 30, 20)
        footer_layout.addStretch()
        
        close_btn = QPushButton("❌ Close")
        close_btn.setMinimumHeight(45)
        close_btn.setMinimumWidth(120)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #0055FF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background-color: #0033CC;
            }
            QPushButton:pressed {
                background-color: #0022AA;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        footer_layout.addWidget(close_btn)
        
        main_layout.addWidget(footer)
        
        dialog.exec()
    
    def delete_employee(self, employee):
        """Delete employee with confirmation"""
        name = employee.get('full_name', f"{employee.get('first_name', '')} {employee.get('last_name', '')}")
        employee_code = employee.get('employee_code', '')
        
        # Create custom confirmation dialog
        reply = QMessageBox(self)
        reply.setWindowTitle("Delete Employee")
        reply.setIcon(QMessageBox.Icon.Warning)
        reply.setText(f"Delete Employee")
        reply.setInformativeText(
            f"Are you sure you want to permanently delete this employee?\n\n"
            f"Name: {name}\n"
            f"Employee Code: {employee_code}\n\n"
            f"This action cannot be undone!"
        )
        
        # Add buttons
        delete_btn = reply.addButton("🗑️ Delete Permanently", QMessageBox.ButtonRole.DestructiveRole)
        deactivate_btn = reply.addButton("⚠️ Deactivate Only", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = reply.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        reply.setDefaultButton(cancel_btn)
        reply.exec()
        
        clicked_button = reply.clickedButton()
        
        if clicked_button == delete_btn:
            # Hard delete - permanently remove from database
            result = employee_manager.delete_employee(employee['employee_id'], hard_delete=True)
            if result > 0:
                QMessageBox.information(self, "Success", f"Employee '{name}' has been permanently deleted!")
                self.load_employees()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete employee.")
        elif clicked_button == deactivate_btn:
            # Soft delete - set status to Inactive
            result = employee_manager.delete_employee(employee['employee_id'], hard_delete=False)
            if result > 0:
                QMessageBox.information(self, "Success", f"Employee '{name}' has been deactivated.")
                self.load_employees()
            else:
                QMessageBox.warning(self, "Error", "Failed to deactivate employee.")

