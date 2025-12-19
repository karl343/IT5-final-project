"""
SwiftPay Payroll Processing Page
Payroll generation, computation, and payslip management
"""

import sys
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QDateEdit, QSpinBox,
    QMessageBox, QHeaderView, QScrollArea, QTabWidget,
    QAbstractItemView, QGroupBox, QFileDialog, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles
from modules.payroll import payroll_manager
from modules.employees import employee_manager
from modules.reports import report_manager


class PayslipDialog(QDialog):
    """
    Dialog to display employee payslip.
    """
    
    def __init__(self, parent, payslip_data):
        super().__init__(parent)
        self.payslip_data = payslip_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize the payslip dialog"""
        self.setWindowTitle("Employee Payslip")
        self.setFixedSize(550, 700)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #1a237e; border-radius: 10px; padding: 20px;")
        header_layout = QVBoxLayout(header)
        
        title = QLabel("SwiftPay")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("PAYSLIP")
        subtitle.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        content_layout.addWidget(header)
        
        # Employee Info
        info_group = QGroupBox("Employee Information")
        info_layout = QFormLayout(info_group)
        
        info_items = [
            ("Employee Code:", self.payslip_data.get('employee_code', '')),
            ("Employee Name:", self.payslip_data.get('employee_name', '')),
            ("Position:", self.payslip_data.get('position', '')),
            ("Department:", self.payslip_data.get('department', '')),
            ("Pay Period:", self.payslip_data.get('payroll_period', '')),
        ]
        
        for label_text, value in info_items:
            label = QLabel(label_text)
            label.setStyleSheet("font-weight: bold;")
            value_label = QLabel(str(value))
            info_layout.addRow(label, value_label)
        
        content_layout.addWidget(info_group)
        
        # Earnings
        earnings_group = QGroupBox("Earnings")
        earnings_group.setStyleSheet("QGroupBox { font-weight: bold; color: #2e7d32; }")
        earnings_layout = QFormLayout(earnings_group)
        
        basic = self.payslip_data.get('basic_pay', 0)
        ot = self.payslip_data.get('overtime_pay', 0)
        allowance = self.payslip_data.get('allowance', 0)
        gross = self.payslip_data.get('gross_pay', 0)
        
        earnings_items = [
            ("Basic Pay:", f"₱ {basic:,.2f}"),
            ("Overtime Pay:", f"₱ {ot:,.2f}"),
            ("Allowance:", f"₱ {allowance:,.2f}"),
        ]
        
        for label_text, value in earnings_items:
            earnings_layout.addRow(QLabel(label_text), QLabel(value))
        
        # Gross total
        gross_label = QLabel("GROSS PAY:")
        gross_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        gross_value = QLabel(f"₱ {gross:,.2f}")
        gross_value.setStyleSheet("font-weight: bold; font-size: 14px; color: #2e7d32;")
        earnings_layout.addRow(gross_label, gross_value)
        
        content_layout.addWidget(earnings_group)
        
        # Deductions
        deductions_group = QGroupBox("Deductions")
        deductions_group.setStyleSheet("QGroupBox { font-weight: bold; color: #c62828; }")
        deductions_layout = QFormLayout(deductions_group)
        
        sss = self.payslip_data.get('sss_deduction', 0)
        philhealth = self.payslip_data.get('philhealth_deduction', 0)
        pagibig = self.payslip_data.get('pagibig_deduction', 0)
        tax = self.payslip_data.get('tax_deduction', 0)
        late = self.payslip_data.get('late_deduction', 0)
        absence = self.payslip_data.get('absence_deduction', 0)
        total_ded = self.payslip_data.get('total_deductions', 0)
        
        deduction_items = [
            ("SSS:", f"₱ {sss:,.2f}"),
            ("PhilHealth:", f"₱ {philhealth:,.2f}"),
            ("Pag-IBIG:", f"₱ {pagibig:,.2f}"),
            ("Tax:", f"₱ {tax:,.2f}"),
            ("Late Deduction:", f"₱ {late:,.2f}"),
            ("Absence Deduction:", f"₱ {absence:,.2f}"),
        ]
        
        for label_text, value in deduction_items:
            deductions_layout.addRow(QLabel(label_text), QLabel(value))
        
        # Total deductions
        total_label = QLabel("TOTAL DEDUCTIONS:")
        total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        total_value = QLabel(f"₱ {total_ded:,.2f}")
        total_value.setStyleSheet("font-weight: bold; font-size: 14px; color: #c62828;")
        deductions_layout.addRow(total_label, total_value)
        
        content_layout.addWidget(deductions_group)
        
        # Net Pay
        net_group = QFrame()
        net_group.setStyleSheet("background-color: #1a237e; border-radius: 10px; padding: 20px;")
        net_layout = QHBoxLayout(net_group)
        
        net_label = QLabel("NET PAY:")
        net_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        net_pay = self.payslip_data.get('net_pay', 0)
        net_value = QLabel(f"₱ {net_pay:,.2f}")
        net_value.setStyleSheet("color: #4caf50; font-size: 24px; font-weight: bold;")
        
        net_layout.addWidget(net_label)
        net_layout.addStretch()
        net_layout.addWidget(net_value)
        
        content_layout.addWidget(net_group)
        
        # Work Summary
        work_group = QGroupBox("Work Summary")
        work_layout = QFormLayout(work_group)
        
        work_items = [
            ("Days Worked:", str(self.payslip_data.get('days_worked', 0))),
            ("Hours Worked:", f"{self.payslip_data.get('hours_worked', 0):.2f}"),
            ("Overtime Hours:", f"{self.payslip_data.get('overtime_hours', 0):.2f}"),
            ("Late Minutes:", str(self.payslip_data.get('late_minutes', 0))),
            ("Absences:", str(self.payslip_data.get('absences', 0))),
        ]
        
        for label_text, value in work_items:
            work_layout.addRow(QLabel(label_text), QLabel(value))
        
        content_layout.addWidget(work_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        export_btn = QPushButton("📄 Export PDF")
        export_btn.setMinimumHeight(42)
        export_btn.setStyleSheet(Styles.BTN_SECONDARY)
        export_btn.clicked.connect(self.export_pdf)
        
        close_btn = QPushButton("❌ Close")
        close_btn.setMinimumHeight(42)
        close_btn.setStyleSheet(Styles.BTN_OUTLINE)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def export_pdf(self):
        """Export payslip to PDF"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Payslip",
            f"payslip_{self.payslip_data.get('employee_code', 'unknown')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if filename:
            try:
                result = report_manager.generate_payslip_pdf(
                    self.payslip_data.get('payroll_id'),
                    self.payslip_data.get('employee_id'),
                    filename
                )
                
                if result:
                    QMessageBox.information(self, "Success", f"Payslip exported to:\n{filename}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to export payslip.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")


class GeneratePayrollDialog(QDialog):
    """
    Dialog for generating a new payroll.
    """
    
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog"""
        self.setWindowTitle("Generate Payroll")
        self.setFixedSize(450, 350)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Generate New Payroll")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a237e;")
        layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        form.setSpacing(15)
        
        # Period name
        self.period_name = QLineEdit()
        self.period_name.setPlaceholderText("e.g., November 2024 - Period 1")
        form.addRow("Period Name:", self.period_name)
        
        # Start date
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-15))
        self.start_date.setCalendarPopup(True)
        self.start_date.dateChanged.connect(self.update_period_name)
        form.addRow("Start Date:", self.start_date)
        
        # End date
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.dateChanged.connect(self.update_period_name)
        form.addRow("End Date:", self.end_date)
        
        layout.addLayout(form)
        
        # Info
        info_label = QLabel(
            "This will calculate payroll for all active employees\n"
            "based on their attendance records for the selected period."
        )
        info_label.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(42)
        cancel_btn.setStyleSheet(Styles.BTN_OUTLINE)
        cancel_btn.clicked.connect(self.reject)
        
        generate_btn = QPushButton("⚙️ Generate Payroll")
        generate_btn.setMinimumHeight(42)
        generate_btn.setStyleSheet(Styles.BTN_PRIMARY)
        generate_btn.clicked.connect(self.generate)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(generate_btn)
        
        layout.addLayout(btn_layout)
        
        # Set initial period name
        self.update_period_name()
    
    def update_period_name(self):
        """Update period name based on dates"""
        start = self.start_date.date()
        end = self.end_date.date()
        name = f"{start.toString('MMMM d')} - {end.toString('MMMM d, yyyy')}"
        self.period_name.setText(name)
    
    def generate(self):
        """Generate the payroll"""
        period = self.period_name.text().strip()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        if not period:
            QMessageBox.warning(self, "Error", "Please enter a period name.")
            return
        
        if start > end:
            QMessageBox.warning(self, "Error", "Start date must be before end date.")
            return
        
        try:
            payroll_id = payroll_manager.generate_payroll(
                start, end, period,
                self.user_data.get('user_id')
            )
            
            if payroll_id:
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Payroll generated successfully!\nPayroll ID: {payroll_id}"
                )
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to generate payroll.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Generation failed: {str(e)}")


class PayrollPage(QWidget):
    """
    Payroll processing page with generation and payslip features.
    """
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        self.load_payrolls()
    
    def init_ui(self):
        """Initialize the page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Generate button
        generate_btn = QPushButton("⚙️ Generate Payroll")
        generate_btn.setMinimumHeight(45)
        generate_btn.setMinimumWidth(180)
        generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        generate_btn.setStyleSheet(Styles.BTN_PRIMARY)
        generate_btn.clicked.connect(self.generate_payroll)
        
        header_layout.addWidget(generate_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_card = self.create_stat_card("Total Payrolls", "0", "#0055FF", "📊")
        self.processed_card = self.create_stat_card("This Month", "₱0", "#10B981", "💰")
        self.pending_card = self.create_stat_card("Pending", "0", "#F59E0B", "⏳")
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.processed_card)
        stats_layout.addWidget(self.pending_card)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Payroll list
        list_label = QLabel("Payroll Records")
        list_label.setStyleSheet("""
            font-size: 18px; 
            font-weight: 600; 
            color: #111827;
            margin-top: 10px;
            margin-bottom: 5px;
        """)
        layout.addWidget(list_label)
        
        self.payroll_table = QTableWidget()
        self.setup_payroll_table()
        layout.addWidget(self.payroll_table, 1)
    
    def create_stat_card(self, title, value, color, icon=""):
        """Create a modern stat card widget with improved styling"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                padding: 0px;
            }}
            QFrame#statCard:hover {{
                border-color: {color};
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
        """)
        card.setMinimumSize(220, 100)
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
            icon_label.setStyleSheet(f"color: {color}; font-size: 20px;")
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
            font-size: 28px;
            font-weight: bold;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        content_layout.addWidget(value_label)
        content_layout.addStretch()
        
        main_layout.addLayout(content_layout)
        
        return card
    
    def setup_payroll_table(self):
        """Setup the payroll table"""
        columns = [
            "ID", "Period", "Start Date", "End Date", "Employees",
            "Gross Pay", "Deductions", "Net Pay", "Actions"
        ]
        
        self.payroll_table.setColumnCount(len(columns))
        self.payroll_table.setHorizontalHeaderLabels(columns)
        
        header = self.payroll_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.payroll_table.setColumnWidth(0, 50)
        self.payroll_table.setColumnWidth(2, 100)
        self.payroll_table.setColumnWidth(3, 100)
        self.payroll_table.setColumnWidth(4, 80)
        self.payroll_table.setColumnWidth(5, 120)
        self.payroll_table.setColumnWidth(6, 120)
        self.payroll_table.setColumnWidth(7, 120)
        self.payroll_table.setColumnWidth(8, 180)
        
        self.payroll_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.payroll_table.setAlternatingRowColors(True)
        self.payroll_table.verticalHeader().setVisible(False)
        
        # Improved table styling
        self.payroll_table.setStyleSheet("""
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
    
    def load_payrolls(self):
        """Load payroll records"""
        try:
            payrolls = payroll_manager.get_all_payrolls()
            self.populate_table(payrolls)
            self.update_stats()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load payrolls: {str(e)}")
    
    def populate_table(self, payrolls):
        """Populate the payroll table"""
        self.payroll_table.setRowCount(0)
        
        if not payrolls:
            return
        
        for row, pr in enumerate(payrolls):
            self.payroll_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(pr.get('payroll_id', '')))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.payroll_table.setItem(row, 0, id_item)
            
            # Period
            self.payroll_table.setItem(row, 1, QTableWidgetItem(pr.get('payroll_period', '')))
            
            # Dates
            start = pr.get('start_date', '')
            if hasattr(start, 'strftime'):
                start = start.strftime('%Y-%m-%d')
            self.payroll_table.setItem(row, 2, QTableWidgetItem(str(start)))
            
            end = pr.get('end_date', '')
            if hasattr(end, 'strftime'):
                end = end.strftime('%Y-%m-%d')
            self.payroll_table.setItem(row, 3, QTableWidgetItem(str(end)))
            
            # Employees
            emp_item = QTableWidgetItem(str(pr.get('total_employees', 0)))
            emp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.payroll_table.setItem(row, 4, emp_item)
            
            # Amounts - Improved formatting with better fonts
            gross = QTableWidgetItem(f"₱{float(pr.get('total_gross_pay', 0)):,.2f}")
            gross.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            gross.setFont(QFont("Segoe UI", 10))
            self.payroll_table.setItem(row, 5, gross)
            
            ded = QTableWidgetItem(f"₱{float(pr.get('total_deductions', 0)):,.2f}")
            ded.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            ded.setFont(QFont("Segoe UI", 10))
            ded.setForeground(QColor("#F59E0B"))  # Orange for deductions
            self.payroll_table.setItem(row, 6, ded)
            
            net = QTableWidgetItem(f"₱{float(pr.get('total_net_pay', 0)):,.2f}")
            net.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            net.setForeground(QColor("#10B981"))  # Modern green
            net.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
            self.payroll_table.setItem(row, 7, net)
            
            # Get status for conditional button display
            status = pr.get('status', 'Draft')
            
            # Actions - Improved button styling
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(8)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            view_btn = QPushButton("👁️ View")
            view_btn.setFixedSize(75, 32)
            view_btn.setToolTip("View Details")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0055FF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 10px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0033CC;
                }
            """)
            view_btn.clicked.connect(lambda checked, p=pr: self.view_payroll(p))
            
            
            if status == 'Draft':
                approve_btn = QPushButton("✅ Approve")
                approve_btn.setFixedSize(90, 32)
                approve_btn.setToolTip("Mark as Paid")
                approve_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                approve_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #F59E0B;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-size: 10px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: #D97706;
                    }
                """)
                approve_btn.clicked.connect(lambda checked, p=pr: self.mark_paid(p))
                actions_layout.addWidget(approve_btn)
            
            actions_layout.addWidget(view_btn)
            actions_layout.addStretch()
            
            self.payroll_table.setCellWidget(row, 8, actions_widget)
            self.payroll_table.setRowHeight(row, 60)  # Increased for better spacing
    
    def update_stats(self):
        """Update statistics cards with real data"""
        try:
            # Total Payrolls - count all payrolls (all time, excluding Draft)
            # Get all payrolls without limit to count properly
            all_payrolls = payroll_manager.get_all_payrolls(limit=None)
            # Count only Paid, Approved, or Processed payrolls (exclude Draft)
            total_count = len([p for p in all_payrolls if p.get('status') in ['Paid', 'Approved', 'Processed']]) if all_payrolls else 0
            self.total_card.findChild(QLabel, "value").setText(str(total_count))
            
            # This Month - get current month's payroll total (only Paid/Approved)
            monthly_summary = payroll_manager.get_payroll_summary(
                datetime.now().year,
                datetime.now().month
            )
            monthly_total = monthly_summary.get('total_net', 0)
            self.processed_card.findChild(QLabel, "value").setText(f"₱{monthly_total:,.2f}")
            
            # Pending - count Draft payrolls
            pending_payrolls = payroll_manager.get_all_payrolls('Draft', limit=None)
            pending = len(pending_payrolls) if pending_payrolls else 0
            self.pending_card.findChild(QLabel, "value").setText(str(pending))
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_payroll(self):
        """Open generate payroll dialog"""
        dialog = GeneratePayrollDialog(self, self.user_data)
        if dialog.exec():
            self.load_payrolls()
    
    def view_payroll(self, payroll):
        """View payroll details"""
        payroll_id = payroll.get('payroll_id')
        details = payroll_manager.get_payroll_details(payroll_id)
        
        if not details:
            QMessageBox.warning(self, "No Data", "No payroll details found.")
            return
        
        # Show details dialog
        dialog = PayrollDetailsDialog(self, payroll, details)
        dialog.exec()
    
    def mark_paid(self, payroll):
        """Mark payroll as paid"""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Mark this payroll as Paid?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            result = payroll_manager.update_payroll_status(
                payroll.get('payroll_id'),
                'Paid'
            )
            
            if result > 0:
                QMessageBox.information(self, "Success", "Payroll marked as Paid!")
                self.load_payrolls()
            else:
                QMessageBox.warning(self, "Error", "Failed to update status.")


class PayrollDetailsDialog(QDialog):
    """
    Dialog showing payroll details for all employees.
    """
    
    def __init__(self, parent, payroll, details):
        super().__init__(parent)
        self.payroll = payroll
        self.details = details
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog"""
        self.setWindowTitle(f"Payroll Details - {self.payroll.get('payroll_period', '')}")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header info
        info_layout = QHBoxLayout()
        
        period_label = QLabel(f"Period: {self.payroll.get('payroll_period', '')}")
        period_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        total_label = QLabel(f"Total Net Pay: ₱{float(self.payroll.get('total_net_pay', 0)):,.2f}")
        total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2e7d32;")
        
        info_layout.addWidget(period_label)
        info_layout.addStretch()
        info_layout.addWidget(total_label)
        
        layout.addLayout(info_layout)
        
        # Table
        self.table = QTableWidget()
        columns = [
            "Code", "Employee", "Position", "Hours", "Basic", "OT Pay",
            "Gross", "Deductions", "Net Pay", "Payslip"
        ]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        
        # Populate table
        for row, det in enumerate(self.details):
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(det.get('employee_code', '')))
            self.table.setItem(row, 1, QTableWidgetItem(det.get('employee_name', '')))
            self.table.setItem(row, 2, QTableWidgetItem(det.get('position', '')))
            self.table.setItem(row, 3, QTableWidgetItem(f"{det.get('hours_worked', 0):.2f}"))
            
            basic = QTableWidgetItem(f"₱{float(det.get('basic_pay', 0)):,.2f}")
            basic.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 4, basic)
            
            ot = QTableWidgetItem(f"₱{float(det.get('overtime_pay', 0)):,.2f}")
            ot.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 5, ot)
            
            gross = QTableWidgetItem(f"₱{float(det.get('gross_pay', 0)):,.2f}")
            gross.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 6, gross)
            
            ded = QTableWidgetItem(f"₱{float(det.get('total_deductions', 0)):,.2f}")
            ded.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 7, ded)
            
            net = QTableWidgetItem(f"₱{float(det.get('net_pay', 0)):,.2f}")
            net.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            net.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 8, net)
            
            # Payslip button
            payslip_btn = QPushButton("👁️ View")
            payslip_btn.setStyleSheet(Styles.BTN_OUTLINE)
            payslip_btn.clicked.connect(lambda checked, d=det: self.view_payslip(d))
            self.table.setCellWidget(row, 9, payslip_btn)
            
            self.table.setRowHeight(row, 40)
        
        layout.addWidget(self.table, 1)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setMinimumHeight(42)
        close_btn.setStyleSheet(Styles.BTN_PRIMARY)
        close_btn.clicked.connect(self.accept)
        
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
    
    def view_payslip(self, detail):
        """View individual payslip"""
        # Add payroll info to detail
        detail['payroll_id'] = self.payroll.get('payroll_id')
        detail['payroll_period'] = self.payroll.get('payroll_period')
        
        dialog = PayslipDialog(self, detail)
        dialog.exec()

