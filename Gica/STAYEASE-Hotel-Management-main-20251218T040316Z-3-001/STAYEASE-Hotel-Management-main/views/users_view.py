import sys
import os

# Add project root to path if running directly
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QHeaderView, QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox, QApplication)
from PyQt6.QtCore import Qt
from models.user_model import UserModel

class UsersView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Top Bar
        top_layout = QHBoxLayout()
        title = QLabel("User Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        add_btn = QPushButton("+ Add User")
        add_btn.clicked.connect(self.add_user)
        top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Role", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)
        
        # Actions
        action_layout = QHBoxLayout()
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_user)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self.delete_user)
        
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.setLayout(layout)
        self.refresh_data()

    def refresh_data(self):
        self.users = UserModel.get_all_users()
        self.table.setRowCount(len(self.users))
        for i, u in enumerate(self.users):
            self.table.setItem(i, 0, QTableWidgetItem(str(u.id)))
            self.table.setItem(i, 1, QTableWidgetItem(u.username))
            self.table.setItem(i, 2, QTableWidgetItem(u.full_name))
            self.table.setItem(i, 3, QTableWidgetItem(u.role))
            self.table.setItem(i, 4, QTableWidgetItem(u.email))

    def add_user(self):
        dialog = UserDialog(parent=self)
        if dialog.exec():
            self.refresh_data()

    def edit_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        user = self.users[selected]
        dialog = UserDialog(user, self)
        if dialog.exec():
            self.refresh_data()

    def delete_user(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        user = self.users[selected]
        
        if user.id == self.user.id:
            QMessageBox.warning(self, "Error", "You cannot delete your own account.")
            return

        confirm = QMessageBox.question(self, "Confirm", f"Are you sure you want to delete user {user.username}?")
        if confirm == QMessageBox.StandardButton.Yes:
            user.delete()
            self.refresh_data()

class UserDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Add User" if not user else "Edit User")
        self.setFixedSize(350, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Set dialog background to white smoke
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QLabel {
                color: #2c3e50;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setContentsMargins(0, 10, 0, 10)

        self.username_input = QLineEdit()
        self.fullname_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Customer", "Receptionist", "Admin"])
        
        # Password field (only for new users or password reset)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Leave blank to keep unchanged" if self.user else "Required")

        if self.user:
            self.username_input.setText(self.user.username)
            self.fullname_input.setText(self.user.full_name or "")
            self.email_input.setText(self.user.email or "")
            self.phone_input.setText(self.user.phone or "")
            self.role_combo.setCurrentText(self.user.role)

        form.addRow("Username:", self.username_input)
        form.addRow("Full Name:", self.fullname_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Phone:", self.phone_input)
        form.addRow("Role:", self.role_combo)
        form.addRow("Password:", self.password_input)

        layout.addLayout(form)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save(self):
        username = self.username_input.text().strip()
        fullname = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        role = self.role_combo.currentText()
        password = self.password_input.text()

        # Validation
        if not username or not fullname:
            QMessageBox.warning(self, "Invalid Input", "Username and Full Name are required.")
            return

        if not self.user and not password:
            QMessageBox.warning(self, "Invalid Input", "Password is required for new users.")
            return

        if self.user:
            self.user.username = username
            self.user.full_name = fullname
            self.user.email = email
            self.user.phone = phone
            self.user.role = role
            # Only update password if provided
            if password:
                self.user.password_hash = password  # In production, hash this!
            
            if self.user.save():
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update user. Please try again.")
        else:
            new_user = UserModel(
                username=username,
                password_hash=password,  # In production, hash this!
                role=role,
                full_name=fullname,
                email=email,
                phone=phone
            )
            if new_user.save():
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to create user. Please try again.")

if __name__ == "__main__":
    # Test block
    app = QApplication(sys.argv)
    
    # Mock user
    class MockUser:
        def __init__(self):
            self.id = 1
            self.username = "admin"
            self.role = "Admin"
            self.full_name = "Administrator"
            self.email = "admin@example.com"
            self.phone = "1234567890"
            
    try:
        window = UsersView(MockUser())
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error running view: {e}")
