"""
SwiftPay User Management Page
Admin-only user account management
"""

import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QComboBox, QMessageBox, QHeaderView,
    QAbstractItemView, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles
from modules.users import user_manager


class UserDialog(QDialog):
    """
    Dialog for adding/editing user accounts.
    """
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit = user_data is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_user_data()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        title = "Edit User" if self.is_edit else "Add New User"
        self.setWindowTitle(title)
        self.setFixedSize(400, 400)
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
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.username.setEnabled(not self.is_edit)
        form_layout.addRow("Username:", self.username)
        
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Enter full name")
        form_layout.addRow("Full Name:", self.full_name)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password" if not self.is_edit else "Leave blank to keep current")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Password:", self.password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirm password")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Confirm:", self.confirm_password)
        
        self.role = QComboBox()
        self.role.addItems(["Staff", "Admin"])
        form_layout.addRow("Role:", self.role)
        
        self.status = QComboBox()
        self.status.addItems(["Active", "Inactive"])
        form_layout.addRow("Status:", self.status)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(42)
        cancel_btn.setStyleSheet(Styles.BTN_OUTLINE)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("💾 Save User")
        save_btn.setMinimumHeight(42)
        save_btn.setStyleSheet(Styles.BTN_PRIMARY)
        save_btn.clicked.connect(self.save_user)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def load_user_data(self):
        """Load existing user data"""
        if not self.user_data:
            return
        
        self.username.setText(self.user_data.get('username', ''))
        self.full_name.setText(self.user_data.get('full_name', ''))
        self.role.setCurrentText(self.user_data.get('role', 'Staff'))
        self.status.setCurrentText(self.user_data.get('status', 'Active'))
    
    def save_user(self):
        """Validate and save user"""
        username = self.username.text().strip()
        full_name = self.full_name.text().strip()
        password = self.password.text()
        confirm = self.confirm_password.text()
        role = self.role.currentText()
        status = self.status.currentText()
        
        # Validation
        if not self.is_edit:
            if not username:
                QMessageBox.warning(self, "Error", "Username is required.")
                return
            if not password:
                QMessageBox.warning(self, "Error", "Password is required.")
                return
        
        if not full_name:
            QMessageBox.warning(self, "Error", "Full name is required.")
            return
        
        if password and password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        
        if password and len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return
        
        try:
            if self.is_edit:
                # Update user
                result = user_manager.update_user(
                    self.user_data['user_id'],
                    full_name=full_name,
                    role=role,
                    status=status
                )
                
                if password:
                    user_manager.reset_password(self.user_data['user_id'], password)
                
                if result >= 0:
                    QMessageBox.information(self, "Success", "User updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update user.")
            else:
                # Create new user
                result = user_manager.create_user(username, password, full_name, role)
                
                if result:
                    QMessageBox.information(self, "Success", "User created successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Username already exists.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class UsersPage(QWidget):
    """
    User management page for administrators.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Initialize the page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)
        
        # Header section with title and subtitle
        header_section = QVBoxLayout()
        header_section.setSpacing(5)
        
        title_label = QLabel("User Management")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #1a237e;")
        header_section.addWidget(title_label)
        
        subtitle_label = QLabel("Manage system users and permissions.")
        subtitle_label.setStyleSheet("font-size: 14px; color: #757575; margin-bottom: 10px;")
        header_section.addWidget(subtitle_label)
        
        layout.addLayout(header_section)
        
        # Top bar with buttons
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        
        # Add user button
        add_btn = QPushButton("➕ Add User")
        add_btn.setMinimumHeight(45)
        add_btn.setMinimumWidth(160)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a237e;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0d1b5e;
            }
        """)
        add_btn.clicked.connect(self.add_user)
        top_bar.addWidget(add_btn)
        
        layout.addLayout(top_bar)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.total_card = self.create_stat_card("Total Users", "0", "#0055FF")
        self.admin_card = self.create_stat_card("Admins", "0", "#EF4444")
        self.staff_card = self.create_stat_card("Staff", "0", "#10B981")
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.admin_card)
        stats_layout.addWidget(self.staff_card)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # White card container for table
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Card header with search
        card_header = QHBoxLayout()
        
        users_label = QLabel("Users")
        users_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #212121;")
        card_header.addWidget(users_label)
        card_header.addStretch()
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search users...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #1a237e;
                background-color: white;
            }
        """)
        self.search_input.textChanged.connect(self.filter_users)
        card_header.addWidget(self.search_input)
        
        card_layout.addLayout(card_header)
        
        # Table
        self.table = QTableWidget()
        self.setup_table()
        card_layout.addWidget(self.table, 1)
        
        layout.addWidget(card, 1)
    
    def create_stat_card(self, title, value, color):
        """Create modern stat card widget with colored bracket"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }}
        """)
        card.setMinimumSize(180, 100)
        
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
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #6B7280; font-size: 13px; font-weight: 500;")
        
        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 700;")
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(value_label)
        content_layout.addStretch()
        
        layout.addLayout(content_layout)
        
        return card
    
    def setup_table(self):
        """Setup users table with modern styling"""
        columns = ["ID", "Username", "Full Name", "Role", "Status", "Created", "Actions"]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 180)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        
        # Modern table styling
        self.table.setStyleSheet("""
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
    
    def load_users(self):
        """Load all users"""
        try:
            users = user_manager.get_all_users(include_inactive=True)
            self.populate_table(users)
            self.update_stats(users)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
    
    def populate_table(self, users):
        """Populate table with user data"""
        self.table.setRowCount(0)
        
        if not users:
            return
        
        for row, user in enumerate(users):
            self.table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(user.get('user_id', '')))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)
            
            # Username
            self.table.setItem(row, 1, QTableWidgetItem(user.get('username', '')))
            
            # Full Name
            self.table.setItem(row, 2, QTableWidgetItem(user.get('full_name', '')))
            
            # Role - Modern badge
            role = user.get('role', 'Staff')
            role_widget = QWidget()
            role_layout = QHBoxLayout(role_widget)
            role_layout.setContentsMargins(5, 2, 5, 2)
            role_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            role_label = QLabel(role)
            role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if role == 'Admin':
                role_label.setStyleSheet("""
                    QLabel {
                        background-color: #EF4444;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 60px;
                    }
                """)
            else:
                role_label.setStyleSheet("""
                    QLabel {
                        background-color: #10B981;
                        color: white;
                        border-radius: 12px;
                        padding: 6px 14px;
                        font-size: 11px;
                        font-weight: 600;
                        min-width: 60px;
                    }
                """)
            role_layout.addWidget(role_label)
            self.table.setCellWidget(row, 3, role_widget)
            
            # Status - Modern badge
            status = user.get('status', 'Active')
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(5, 2, 5, 2)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_label = QLabel(status)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if status == 'Active':
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
            self.table.setCellWidget(row, 4, status_widget)
            
            # Created
            created = user.get('created_at', '')
            if hasattr(created, 'strftime'):
                created = created.strftime('%Y-%m-%d')
            self.table.setItem(row, 5, QTableWidgetItem(str(created) if created else ''))
            
            # Actions - Modern icon buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(8, 4, 8, 4)
            actions_layout.setSpacing(8)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Edit button
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setFixedSize(70, 32)
            edit_btn.setToolTip("Edit User")
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
            edit_btn.clicked.connect(lambda checked, u=user: self.edit_user(u))
            
            # Reset password button
            reset_btn = QPushButton("🔑 Reset")
            reset_btn.setFixedSize(80, 32)
            reset_btn.setToolTip("Reset Password")
            reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            reset_btn.clicked.connect(lambda checked, u=user: self.reset_password(u))
            
            # Delete button
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setFixedSize(80, 32)
            delete_btn.setToolTip("Delete User")
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
            delete_btn.clicked.connect(lambda checked, u=user: self.delete_user(u))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(reset_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.table.setCellWidget(row, 6, actions_widget)
            self.table.setRowHeight(row, 60)
    
    def update_stats(self, users):
        """Update statistics"""
        if not users:
            return
        
        total = len(users)
        admins = sum(1 for u in users if u.get('role') == 'Admin')
        staff = sum(1 for u in users if u.get('role') == 'Staff')
        
        self.total_card.findChild(QLabel, "value").setText(str(total))
        self.admin_card.findChild(QLabel, "value").setText(str(admins))
        self.staff_card.findChild(QLabel, "value").setText(str(staff))
    
    def filter_users(self, text):
        """Filter users by search text"""
        search = text.lower()
        
        for row in range(self.table.rowCount()):
            show = False
            for col in range(self.table.columnCount() - 1):
                item = self.table.item(row, col)
                if item and search in item.text().lower():
                    show = True
                    break
            self.table.setRowHidden(row, not show)
    
    def add_user(self):
        """Open dialog to add user"""
        dialog = UserDialog(self)
        if dialog.exec():
            self.load_users()
    
    def edit_user(self, user):
        """Open dialog to edit user"""
        dialog = UserDialog(self, user)
        if dialog.exec():
            self.load_users()
    
    def reset_password(self, user):
        """Reset user password"""
        dialog = ResetPasswordDialog(self, user)
        dialog.exec()
    
    def delete_user(self, user):
        """Delete user with confirmation"""
        username = user.get('username', 'Unknown')
        full_name = user.get('full_name', '')
        user_id = user.get('user_id')
        
        # Prevent deleting yourself
        current_user = user_manager.get_current_user()
        if current_user and current_user.get('user_id') == user_id:
            QMessageBox.warning(self, "Error", "You cannot delete your own account!")
            return
        
        # Create custom confirmation dialog
        reply = QMessageBox(self)
        reply.setWindowTitle("Delete User")
        reply.setIcon(QMessageBox.Icon.Warning)
        reply.setText(f"Delete User")
        reply.setInformativeText(
            f"Are you sure you want to deactivate this user?\n\n"
            f"Username: {username}\n"
            f"Full Name: {full_name}\n\n"
            f"This will set the user status to 'Inactive'."
        )
        
        # Add buttons
        delete_btn = reply.addButton("🗑️ Deactivate User", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = reply.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        reply.setDefaultButton(cancel_btn)
        reply.exec()
        
        clicked_button = reply.clickedButton()
        
        if clicked_button == delete_btn:
            try:
                result = user_manager.delete_user(user_id)
                if result > 0:
                    QMessageBox.information(self, "Success", f"User '{username}' has been deactivated.")
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", "Failed to deactivate user.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class ResetPasswordDialog(QDialog):
    """
    Dialog for resetting user password.
    """
    
    def __init__(self, parent, user):
        super().__init__(parent)
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog"""
        self.setWindowTitle("Reset Password")
        self.setFixedSize(350, 250)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel(f"Reset Password for {self.user.get('username', '')}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a237e;")
        layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        form.setSpacing(10)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("Enter new password")
        form.addRow("New Password:", self.new_password)
        
        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm.setPlaceholderText("Confirm password")
        form.addRow("Confirm:", self.confirm)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet(Styles.BTN_OUTLINE)
        cancel_btn.clicked.connect(self.reject)
        
        reset_btn = QPushButton("🔑 Reset Password")
        reset_btn.setStyleSheet(Styles.BTN_PRIMARY)
        reset_btn.clicked.connect(self.reset)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(reset_btn)
        
        layout.addLayout(btn_layout)
    
    def reset(self):
        """Reset the password"""
        password = self.new_password.text()
        confirm = self.confirm.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Password is required.")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Error", "Password must be at least 6 characters.")
            return
        
        result = user_manager.reset_password(self.user['user_id'], password)
        
        if result:
            QMessageBox.information(self, "Success", "Password reset successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to reset password.")

