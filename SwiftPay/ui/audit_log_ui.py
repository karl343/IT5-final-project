"""
SwiftPay Audit Log Page
View and filter system audit logs
"""

import sys
import os
import json
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView,
    QDateEdit, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles
from modules.audit_log import audit_logger, AuditLogger


class AuditLogPage(QWidget):
    """
    Page for viewing and filtering audit logs.
    Admin-only access.
    """
    
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        # Verify user has admin access
        if self.user_data.get('role') != 'Admin':
            self.show_access_denied()
            return
        
        # Pagination variables
        self.current_page = 1
        self.page_size = 10  # Show 10 items per page
        self.total_logs = 0
        
        self.init_ui()
        # Load logs with error handling - don't fail page creation if logs can't load
        try:
            self.load_logs()
        except Exception as e:
            print(f"Warning: Could not load audit logs on initialization: {e}")
            # Show empty table with error message
            self.table.setRowCount(0)
            self.stats_label.setText(f"Error loading logs: {str(e)}. Please try refreshing.")
    
    def show_access_denied(self):
        """Show access denied message for non-admin users"""
        # Initialize attributes to avoid errors
        self.table = None
        self.stats_label = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        error_label = QLabel("Access Denied")
        error_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #c62828;")
        
        message_label = QLabel(
            "You do not have permission to access the Audit Log.\n\n"
            "Only Administrators can view audit logs."
        )
        message_label.setStyleSheet("font-size: 14px; color: #424242; padding: 20px;")
        
        layout.addStretch()
        layout.addWidget(error_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
    
    def init_ui(self):
        """Initialize the audit log page UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Audit Log")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1a237e;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Filters section - horizontal layout
        filters_group = QGroupBox("Filters")
        filters_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
                font-weight: bold;
                color: #1a237e;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        filters_layout = QVBoxLayout()
        filters_layout.setSpacing(15)
        
        # Horizontal filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        
        # Start Date
        start_label = QLabel("Start Date:")
        start_label.setStyleSheet("color: #212121; font-size: 13px;")
        start_label.setMinimumWidth(70)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("MM/dd/yyyy")
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 6px 35px 6px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-width: 140px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #ddd;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #f5f5f5;
            }
            QDateEdit::drop-down:hover {
                background-color: #1a237e;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #666;
                width: 0px;
                height: 0px;
                margin-right: 3px;
            }
            QDateEdit::down-arrow:hover {
                border-top-color: white;
            }
        """)
        filter_row.addWidget(start_label)
        filter_row.addWidget(self.start_date)
        
        # End Date
        end_label = QLabel("End Date:")
        end_label.setStyleSheet("color: #212121; font-size: 13px;")
        end_label.setMinimumWidth(70)
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("MM/dd/yyyy")
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 6px 35px 6px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-width: 140px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #ddd;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #f5f5f5;
            }
            QDateEdit::drop-down:hover {
                background-color: #1a237e;
            }
            QDateEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #666;
                width: 0px;
                height: 0px;
                margin-right: 3px;
            }
            QDateEdit::down-arrow:hover {
                border-top-color: white;
            }
        """)
        filter_row.addWidget(end_label)
        filter_row.addWidget(self.end_date)
        
        # Action type filter
        action_label = QLabel("Action Type:")
        action_label.setStyleSheet("color: #212121; font-size: 13px;")
        action_label.setMinimumWidth(80)
        self.action_filter = QComboBox()
        self.action_filter.addItems([
            "All Actions",
            "LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE",
            "VIEW", "EXPORT", "APPROVE", "REJECT",
            "PASSWORD_CHANGE", "PASSWORD_RESET",
            "TIME_IN", "TIME_OUT", "GENERATE"
        ])
        self.action_filter.setStyleSheet(Styles.INPUT_STYLE)
        self.action_filter.setMinimumWidth(130)
        filter_row.addWidget(action_label)
        filter_row.addWidget(self.action_filter)
        
        # Entity type filter
        entity_label = QLabel("Entity Type:")
        entity_label.setStyleSheet("color: #212121; font-size: 13px;")
        entity_label.setMinimumWidth(80)
        self.entity_filter = QComboBox()
        self.entity_filter.addItems([
            "All Entities",
            "USER", "EMPLOYEE", "ATTENDANCE", "PAYROLL", "REPORT", "SYSTEM"
        ])
        self.entity_filter.setStyleSheet(Styles.INPUT_STYLE)
        self.entity_filter.setMinimumWidth(120)
        filter_row.addWidget(entity_label)
        filter_row.addWidget(self.entity_filter)
        
        # Search
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #212121; font-size: 13px;")
        search_label.setMinimumWidth(60)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in description...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 1px solid #1a237e;
            }
        """)
        filter_row.addWidget(search_label)
        filter_row.addWidget(self.search_input)
        
        filter_row.addStretch()
        
        filters_layout.addLayout(filter_row)
        
        # Filter buttons
        filter_btn_layout = QHBoxLayout()
        filter_btn_layout.addStretch()
        
        apply_btn = QPushButton("✅ Apply Filters")
        apply_btn.setMinimumHeight(40)
        apply_btn.setMinimumWidth(120)
        apply_btn.setStyleSheet(Styles.BTN_PRIMARY)
        apply_btn.clicked.connect(self.apply_filters)
        
        clear_btn = QPushButton("🗑️ Clear Filters")
        clear_btn.setMinimumHeight(40)
        clear_btn.setMinimumWidth(120)
        clear_btn.setStyleSheet(Styles.BTN_OUTLINE)
        clear_btn.clicked.connect(self.clear_filters)
        
        filter_btn_layout.addWidget(apply_btn)
        filter_btn_layout.addWidget(clear_btn)
        
        filters_layout.addLayout(filter_btn_layout)
        filters_group.setLayout(filters_layout)
        
        layout.addWidget(filters_group)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("font-size: 12px; color: #666; padding: 10px;")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Timestamp", "User", "Action", "Entity", "Entity ID", "Description", "Details"
        ])
        self.table.setStyleSheet(Styles.TABLE_STYLE)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(6, 150)  # Fixed width for Details column
        
        # Center align the Details column header
        details_header = QTableWidgetItem("Details")
        details_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setHorizontalHeaderItem(6, details_header)
        
        # Set minimum row height to ensure buttons are visible
        self.table.verticalHeader().setDefaultSectionSize(50)
        
        layout.addWidget(self.table)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(10)
        
        # Page info
        self.page_info_label = QLabel("Showing 0-0 of 0 entries")
        self.page_info_label.setStyleSheet("font-size: 13px; color: #666; font-weight: normal;")
        pagination_layout.addWidget(self.page_info_label)
        pagination_layout.addStretch()
        
        # Previous button
        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.setMinimumHeight(35)
        self.prev_btn.setMinimumWidth(100)
        self.prev_btn.setStyleSheet(Styles.BTN_OUTLINE)
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_btn)
        
        # Page number display
        self.page_label = QLabel("Page 1 of 1")
        self.page_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold;
            color: #1a237e; 
            padding: 8px 20px;
            background-color: #f5f5f5;
            border-radius: 6px;
            min-width: 120px;
        """)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pagination_layout.addWidget(self.page_label)
        
        # Next button
        self.next_btn = QPushButton("Next ▶")
        self.next_btn.setMinimumHeight(35)
        self.next_btn.setMinimumWidth(100)
        self.next_btn.setStyleSheet(Styles.BTN_OUTLINE)
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_btn)
        
        layout.addLayout(pagination_layout)
    
    def load_logs(self):
        """Load audit logs into the table with pagination"""
        try:
            # Get filter values - convert QDate to Python date
            start_qdate = self.start_date.date()
            start_date = datetime(start_qdate.year(), start_qdate.month(), start_qdate.day()).date()
            end_qdate = self.end_date.date()
            end_date = datetime(end_qdate.year(), end_qdate.month(), end_qdate.day()).date()
            
            action_type = None
            if self.action_filter.currentText() != "All Actions":
                action_type = self.action_filter.currentText()
            
            entity_type = None
            if self.entity_filter.currentText() != "All Entities":
                entity_type = self.entity_filter.currentText()
            
            # Get all logs for filtering (we'll paginate after filtering)
            all_logs = audit_logger.get_logs(
                action_type=action_type,
                entity_type=entity_type,
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Get a large number to filter
            )
            
            # Filter by search term if provided
            search_term = self.search_input.text().strip().lower()
            if search_term and all_logs:
                all_logs = [log for log in all_logs if search_term in (log.get('action_description') or '').lower()]
            
            # Calculate pagination
            self.total_logs = len(all_logs) if all_logs else 0
            
            # Only paginate if there are more than 10 items
            if self.total_logs > 10:
                total_pages = (self.total_logs + self.page_size - 1) // self.page_size if self.total_logs > 0 else 1
                
                # Ensure current_page is valid
                if self.current_page > total_pages:
                    self.current_page = total_pages if total_pages > 0 else 1
                if self.current_page < 1:
                    self.current_page = 1
                
                # Get logs for current page
                start_idx = (self.current_page - 1) * self.page_size
                end_idx = start_idx + self.page_size
                logs = all_logs[start_idx:end_idx] if all_logs else []
            else:
                # Show all items if 10 or fewer
                logs = all_logs if all_logs else []
                total_pages = 1
            
            # Populate table
            self.table.setRowCount(len(logs) if logs else 0)
            
            if logs:
                for row, log in enumerate(logs):
                    # Timestamp
                    timestamp = log.get('created_at')
                    if isinstance(timestamp, str):
                        try:
                            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        except:
                            pass
                    if isinstance(timestamp, datetime):
                        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        timestamp_str = str(timestamp) if timestamp else ""
                    
                    self.table.setItem(row, 0, QTableWidgetItem(timestamp_str))
                    
                    # User
                    user_name = log.get('user_name') or log.get('username') or "System"
                    self.table.setItem(row, 1, QTableWidgetItem(user_name))
                    
                    # Action
                    action = log.get('action_type', '')
                    action_item = QTableWidgetItem(action)
                    # Color code actions
                    if action == 'LOGIN':
                        action_item.setForeground(Qt.GlobalColor.darkGreen)
                    elif action == 'LOGOUT':
                        action_item.setForeground(Qt.GlobalColor.darkBlue)
                    elif action == 'CREATE':
                        action_item.setForeground(Qt.GlobalColor.blue)
                    elif action == 'UPDATE':
                        action_item.setForeground(Qt.GlobalColor.darkYellow)
                    elif action == 'DELETE':
                        action_item.setForeground(Qt.GlobalColor.red)
                    self.table.setItem(row, 2, action_item)
                    
                    # Entity
                    self.table.setItem(row, 3, QTableWidgetItem(log.get('entity_type', '')))
                    
                    # Entity ID
                    entity_id = log.get('entity_id')
                    self.table.setItem(row, 4, QTableWidgetItem(str(entity_id) if entity_id else ""))
                    
                    # Description
                    description = log.get('action_description', '')
                    self.table.setItem(row, 5, QTableWidgetItem(description))
                    
                    # Details button - centered in cell
                    details_btn = QPushButton("👁️ View Details")
                    details_btn.setStyleSheet("""
                        QPushButton {
                            background-color: white;
                            color: #1a237e;
                            border: 2px solid #1a237e;
                            border-radius: 6px;
                            padding: 6px 12px;
                            font-size: 12px;
                            font-weight: bold;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #1a237e;
                            color: white;
                        }
                    """)
                    details_btn.setMinimumWidth(100)
                    details_btn.setMinimumHeight(30)
                    details_btn.clicked.connect(lambda checked, l=log: self.show_details(l))
                    
                    # Create a widget container to center the button
                    btn_widget = QWidget()
                    btn_widget.setStyleSheet("background-color: transparent;")
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.setContentsMargins(5, 5, 5, 5)
                    btn_layout.addWidget(details_btn)
                    btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    self.table.setCellWidget(row, 6, btn_widget)
                    
                    # Set row height to ensure button is visible
                    self.table.setRowHeight(row, 50)
            
            # Update pagination controls
            self.update_pagination(total_pages)
            
            # Update statistics
            self.update_statistics(all_logs)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load audit logs: {str(e)}")
    
    def update_pagination(self, total_pages):
        """Update pagination controls"""
        # Only show pagination if there are more than 10 items
        if self.total_logs > 10:
            # Update page label
            self.page_label.setText(f"Page {self.current_page} of {total_pages}")
            self.page_label.setVisible(True)
            
            # Update page info
            start_idx = (self.current_page - 1) * self.page_size + 1
            end_idx = min(self.current_page * self.page_size, self.total_logs)
            self.page_info_label.setText(f"Showing {start_idx}-{end_idx} of {self.total_logs} entries")
            
            # Enable/disable navigation buttons
            self.prev_btn.setEnabled(self.current_page > 1)
            self.prev_btn.setVisible(True)
            self.next_btn.setEnabled(self.current_page < total_pages)
            self.next_btn.setVisible(True)
        else:
            # Hide pagination controls when 10 or fewer items
            self.page_label.setVisible(False)
            self.prev_btn.setVisible(False)
            self.next_btn.setVisible(False)
            
            # Update page info to show all items
            if self.total_logs > 0:
                self.page_info_label.setText(f"Showing all {self.total_logs} entries")
            else:
                self.page_info_label.setText("No entries found")
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_logs()
    
    def next_page(self):
        """Go to next page"""
        total_pages = (self.total_logs + self.page_size - 1) // self.page_size if self.total_logs > 0 else 1
        if self.current_page < total_pages:
            self.current_page += 1
            self.load_logs()
    
    def apply_filters(self):
        """Apply filters and reload logs"""
        self.current_page = 1  # Reset to first page when applying filters
        self.load_logs()
    
    def clear_filters(self):
        """Clear all filters"""
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.end_date.setDate(QDate.currentDate())
        self.action_filter.setCurrentIndex(0)
        self.entity_filter.setCurrentIndex(0)
        self.search_input.clear()
        self.current_page = 1  # Reset to first page when clearing filters
        self.load_logs()
    
    def show_details(self, log):
        """Show detailed information about a log entry"""
        from PyQt6.QtWidgets import QDialog, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Audit Log Details")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Audit Log Entry Details")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a237e;")
        layout.addWidget(title)
        
        # Details text
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 11px;")
        
        details = []
        details.append(f"Log ID: {log.get('log_id', 'N/A')}")
        details.append(f"Timestamp: {log.get('created_at', 'N/A')}")
        details.append(f"User: {log.get('user_name') or log.get('username') or 'System'}")
        details.append(f"Action Type: {log.get('action_type', 'N/A')}")
        details.append(f"Entity Type: {log.get('entity_type', 'N/A')}")
        details.append(f"Entity ID: {log.get('entity_id', 'N/A')}")
        details.append(f"Description: {log.get('action_description', 'N/A')}")
        
        # Old values
        old_values = log.get('old_values')
        if old_values:
            try:
                if isinstance(old_values, str):
                    old_values = json.loads(old_values)
                details.append("\nOld Values:")
                details.append(json.dumps(old_values, indent=2))
            except:
                details.append(f"\nOld Values: {old_values}")
        
        # New values
        new_values = log.get('new_values')
        if new_values:
            try:
                if isinstance(new_values, str):
                    new_values = json.loads(new_values)
                details.append("\nNew Values:")
                details.append(json.dumps(new_values, indent=2))
            except:
                details.append(f"\nNew Values: {new_values}")
        
        details_text.setPlainText("\n".join(details))
        layout.addWidget(details_text)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setMinimumHeight(40)
        close_btn.setStyleSheet(Styles.BTN_PRIMARY)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def update_statistics(self, logs):
        """Update statistics label"""
        if logs:
            total = len(logs)
            # Convert QDate to Python date
            start_qdate = self.start_date.date()
            start_date = datetime(start_qdate.year(), start_qdate.month(), start_qdate.day()).date()
            end_qdate = self.end_date.date()
            end_date = datetime(end_qdate.year(), end_qdate.month(), end_qdate.day()).date()
            
            stats = audit_logger.get_log_statistics(
                start_date=start_date,
                end_date=end_date
            )
            self.stats_label.setText(
                f"Showing {total} log entries | "
                f"Total: {stats.get('total_logs', 0)} | "
                f"Creates: {stats.get('creates', 0)} | "
                f"Updates: {stats.get('updates', 0)} | "
                f"Deletes: {stats.get('deletes', 0)} | "
                f"Logins: {stats.get('logins', 0)}"
            )
        else:
            self.stats_label.setText("No log entries found")

