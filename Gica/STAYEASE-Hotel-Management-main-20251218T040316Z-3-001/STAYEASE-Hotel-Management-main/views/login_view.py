from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QDialog, QFormLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QPixmap, QColor, QIcon
from PyQt6.QtCore import Qt, QSize
from controllers.auth_controller import AuthController

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STAYEASE - Login")
        self.setFixedSize(450, 550) # Increased size for the card background
        self.auth_controller = AuthController()
        self.user = None
        self.init_ui()

    def init_ui(self):
        self.setObjectName("LoginWindow")
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Login Card
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setFixedSize(380, 480)
        
        # Add Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(40, 40, 40, 40)

        # Logo / Title Area
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setMinimumHeight(120)
        
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(280, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("STAYEASE") # Fallback
            logo_label.setObjectName("LogoText")
            logo_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2c3e50;")
        
        card_layout.addWidget(logo_label)

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(45)
        card_layout.addWidget(self.username_input)

        # Password Field with Toggle
        password_container = QFrame()
        password_container.setFixedHeight(45)
        password_container.setObjectName("PasswordContainer")
        password_container.setStyleSheet("""
            QFrame#PasswordContainer {
                background-color: #F5F5F5;
                border: 1px solid #dcdcdc;
                border-radius: 6px;
            }
            QFrame#PasswordContainer:focus-within {
                border: 1px solid #3498db;
            }
        """)
        pass_layout = QHBoxLayout(password_container)
        pass_layout.setContentsMargins(0, 0, 5, 0)
        pass_layout.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                padding-left: 10px;
            }
        """)
        pass_layout.addWidget(self.password_input)

        # Prepare Icons
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_view = QIcon(os.path.join(base_dir, "assets", "view.png"))
        self.icon_hide = QIcon(os.path.join(base_dir, "assets", "hide.png"))

        self.toggle_pass_btn = QPushButton()
        self.toggle_pass_btn.setIcon(self.icon_view)
        self.toggle_pass_btn.setIconSize(QSize(20, 20))
        self.toggle_pass_btn.setFixedSize(30, 30)
        self.toggle_pass_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_pass_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.toggle_pass_btn.setStyleSheet("background: transparent; border: none;")
        self.toggle_pass_btn.clicked.connect(self.toggle_password_visibility)
        pass_layout.addWidget(self.toggle_pass_btn)

        card_layout.addWidget(password_container)

        # Login Button
        login_btn = QPushButton("Log In")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setFixedHeight(45)
        # Specific Facebook-like blue for this button
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #1877f2; 
                font-size: 20px; 
                font-weight: bold;
                border-radius: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(login_btn)

        # Separator (Optional but good for spacing)
        # line = QFrame()
        # line.setFrameShape(QFrame.Shape.HLine)
        # line.setFrameShadow(QFrame.Shadow.Sunken)
        # line.setStyleSheet("background-color: #dadde1; margin-top: 5px; margin-bottom: 5px;")
        # card_layout.addWidget(line)

        # Create Account Button (Green)
        create_account_btn = QPushButton("Create new account")
        create_account_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_account_btn.setFixedHeight(45)
        create_account_btn.setStyleSheet("""
            QPushButton {
                background-color: #42b72a;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 6px;
                padding: 0 16px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #36a420;
            }
        """)
        create_account_btn.clicked.connect(self.show_register_dialog)
        card_layout.addWidget(create_account_btn)
        
        card_layout.addStretch()
        
        main_layout.addWidget(card)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return

        success, message = self.auth_controller.login(username, password)
        if success:
            self.user = self.auth_controller.get_current_user()
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", message)

    def get_user(self):
        return self.user

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_pass_btn.setIcon(self.icon_hide)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_pass_btn.setIcon(self.icon_view)
    def show_register_dialog(self):
        dialog = RegisterDialog(self.auth_controller, self)
        dialog.exec()

class RegisterDialog(QDialog):
    def __init__(self, auth_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")
        self.setFixedSize(400, 550)
        self.auth_controller = auth_controller
        self.init_ui()

    def init_ui(self):
        self.setObjectName("LoginWindow") # Reuse white background style
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Join STAYEASE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        self.username_input = self.create_input("Username")
        layout.addWidget(self.username_input)
        
        self.password_input = self.create_input("Password", password=True)
        layout.addWidget(self.password_input)
        
        self.fullname_input = self.create_input("Full Name")
        layout.addWidget(self.fullname_input)
        
        self.email_input = self.create_input("Email Address")
        layout.addWidget(self.email_input)
        
        self.phone_input = self.create_input("Phone Number")
        layout.addWidget(self.phone_input)

        register_btn = QPushButton("REGISTER")
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setFixedHeight(45)
        # register_btn.setStyleSheet("font-size: 14px; letter-spacing: 1px; margin-top: 10px;") # Handled by global css now
        register_btn.clicked.connect(self.handle_register)
        layout.addWidget(register_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFlat(True)
        cancel_btn.setObjectName("LinkButton") # Use link style
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        layout.addStretch()
        self.setLayout(layout)

    def create_input(self, placeholder, password=False):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(40)
        if password:
            inp.setEchoMode(QLineEdit.EchoMode.Password)
        return inp

    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        fullname = self.fullname_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()

        if not all([username, password, fullname, email]):
            QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return

        success, message = self.auth_controller.register(username, password, fullname, email, phone)
        if success:
            QMessageBox.information(self, "Success", "Registration successful! Please login.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)
