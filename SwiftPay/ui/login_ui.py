"""
SwiftPay Login Window
Clean, professional authentication interface with registration
"""

import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
    QDialog, QComboBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QPolygon, QPen

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.users import user_manager


class SwiftPayLogo(QWidget):
    """Custom SwiftPay logo widget - scalable version"""
    
    def __init__(self, parent=None, white_text=False, size=None):
        super().__init__(parent)
        self.white_text = white_text
        if size:
            self.setFixedSize(size[0], size[1])
        else:
            self.setFixedSize(300, 85)
        self.setStyleSheet("background: transparent;")
    
    def paintEvent(self, event):
        """Paint the SwiftPay logo - enhanced with shadows and better styling"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions for scaling
        widget_width = self.width()
        widget_height = self.height()
        scale = widget_width / 300.0  # Base width is 300
        
        # Colors - use white/light colors if on blue background
        if self.white_text:
            square_color = QColor("#ffffff")
            text_color = QColor("#ffffff")
            dollar_color = QColor("#000000")  # Black dollar sign on white square
            shadow_color = QColor(0, 0, 0, 20)  # Subtle shadow for white square
        else:
            square_color = QColor("#ffffff")
            text_color = QColor("#1a237e")
            dollar_color = QColor("#000000")
            shadow_color = QColor(0, 0, 0, 15)  # Subtle shadow
        
        orange = QColor("#F59E0B")  # Updated to brighter orange
        
        # Calculate scaled dimensions
        square_size = int(55 * scale)
        square_y = int(15 * scale)
        square_rect = QRect(0, square_y, square_size, square_size)
        corner_radius = int(12 * scale)  # Slightly more rounded
        
        # Draw shadow for white square (subtle depth)
        shadow_offset = int(2 * scale)
        shadow_rect = QRect(shadow_offset, square_y + shadow_offset, square_size, square_size)
        painter.setBrush(shadow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, corner_radius, corner_radius)
        
        # Draw white rounded square with subtle border
        painter.setBrush(square_color)
        painter.setPen(QPen(QColor("#E5E7EB"), int(1 * scale)))  # Subtle border
        painter.drawRoundedRect(square_rect, corner_radius, corner_radius)
        
        # Draw black dollar sign inside the white square (better centered)
        painter.setPen(dollar_color)
        font_size = int(38 * scale)  # Slightly larger
        dollar_font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
        painter.setFont(dollar_font)
        
        # Better centering for dollar sign
        dollar_rect = QRect(square_rect)
        dollar_rect.adjust(int(2 * scale), int(2 * scale), int(-2 * scale), int(-2 * scale))
        painter.drawText(dollar_rect, Qt.AlignmentFlag.AlignCenter, "$")
        
        # Draw orange equals sign (two horizontal bars) - improved spacing
        bar_width = int(32 * scale)  # Slightly wider
        bar_height = int(5.5 * scale)  # Slightly thicker
        bar_spacing = int(6 * scale)  # Better spacing
        start_x = square_size + int(14 * scale)  # Better spacing from square
        bar_y = int(28 * scale)
        
        # First orange bar (top) with shadow
        bar1_shadow = QRect(start_x + 1, bar_y + 1, bar_width, bar_height)
        painter.setBrush(QColor(245, 124, 0, 100))  # Shadow
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bar1_shadow, int(3 * scale), int(3 * scale))
        
        bar1_rect = QRect(start_x, bar_y, bar_width, bar_height)
        painter.setBrush(orange)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bar1_rect, int(3 * scale), int(3 * scale))
        
        # Second orange bar (bottom) with shadow
        bar2_shadow = QRect(start_x + 1, bar_y + bar_height + bar_spacing + 1, bar_width, bar_height)
        painter.setBrush(QColor(245, 124, 0, 100))  # Shadow
        painter.drawRoundedRect(bar2_shadow, int(3 * scale), int(3 * scale))
        
        bar2_rect = QRect(start_x, bar_y + bar_height + bar_spacing, bar_width, bar_height)
        painter.setBrush(orange)
        painter.drawRoundedRect(bar2_rect, int(3 * scale), int(3 * scale))
        
        # Draw "SwiftPay" text with improved typography
        painter.setPen(text_color)
        text_font_size = int(30 * scale)  # Slightly larger
        text_font = QFont("Segoe UI", text_font_size, QFont.Weight.Bold)
        painter.setFont(text_font)
        text_x = start_x + bar_width + int(18 * scale)  # Better spacing
        text_y = int(18 * scale)  # Better vertical alignment
        text_width = int(170 * scale)
        text_height = int(55 * scale)
        text_rect = QRect(text_x, text_y, text_width, text_height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "SwiftPay")


class FocusLineEdit(QLineEdit):
    """Line edit that notifies parent of focus changes"""
    
    focus_changed = pyqtSignal(bool)
    
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.focus_changed.emit(True)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focus_changed.emit(False)


class IconLineEdit(QFrame):
    """Custom input field with icon"""
    
    def __init__(self, icon_text, placeholder="", is_password=False, parent=None):
        super().__init__(parent)
        self.setObjectName("iconLineEdit")
        self._set_normal_style()
        self.setMinimumHeight(48)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(14)
        
        # Icon
        self.icon_label = QLabel(icon_text)
        self.icon_label.setFont(QFont("Segoe UI", 16))
        self.icon_label.setStyleSheet("color: #9ca3af;")
        self.icon_label.setFixedWidth(24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Input field
        self.line_edit = FocusLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        if is_password:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.line_edit.setFont(QFont("Segoe UI", 13))
        self.line_edit.setStyleSheet("""
            QLineEdit {
                border: none;
                background: transparent;
                color: #1f2937;
                padding: 0;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        self.line_edit.focus_changed.connect(self._on_focus_changed)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.line_edit, 1)
    
    def _set_normal_style(self):
        self.setStyleSheet("""
            QFrame#iconLineEdit {
                background-color: #ffffff;
                border: 2px solid #E5E7EB;
                border-radius: 12px;
            }
            QFrame#iconLineEdit:hover {
                border-color: #D1D5DB;
                background-color: #FAFAFA;
            }
        """)
    
    def _set_focus_style(self):
        self.setStyleSheet("""
            QFrame#iconLineEdit {
                background-color: #ffffff;
                border: 2px solid #2563eb;
                border-radius: 12px;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            }
        """)
    
    def _on_focus_changed(self, focused):
        if focused:
            self._set_focus_style()
        else:
            self._set_normal_style()
    
    def text(self):
        return self.line_edit.text()
    
    def clear(self):
        self.line_edit.clear()
    
    def setFocus(self):
        self.line_edit.setFocus()


class RegisterDialog(QDialog):
    """Registration dialog for creating new accounts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Account")
        self.setFixedSize(450, 580)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)
        
        # Header
        title = QLabel("Create Account")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("color: #111827;")
        
        subtitle = QLabel("Fill in your details to get started")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: #6b7280;")
        subtitle.setContentsMargins(0, 8, 0, 0)
        
        # Full Name
        fullname_container = QWidget()
        fullname_container.setStyleSheet("background: transparent;")
        fullname_layout = QVBoxLayout(fullname_container)
        fullname_layout.setContentsMargins(0, 30, 0, 0)
        fullname_layout.setSpacing(8)
        
        fullname_label = QLabel("Full Name")
        fullname_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        fullname_label.setStyleSheet("color: #374151;")
        
        self.fullname_input = IconLineEdit("", "Enter your full name")
        
        fullname_layout.addWidget(fullname_label)
        fullname_layout.addWidget(self.fullname_input)
        
        # Username
        username_container = QWidget()
        username_container.setStyleSheet("background: transparent;")
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 20, 0, 0)
        username_layout.setSpacing(8)
        
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        username_label.setStyleSheet("color: #374151;")
        
        self.username_input = IconLineEdit("📧", "Choose a username")
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Password
        password_container = QWidget()
        password_container.setStyleSheet("background: transparent;")
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 20, 0, 0)
        password_layout.setSpacing(8)
        
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        password_label.setStyleSheet("color: #374151;")
        
        self.password_input = IconLineEdit("", "Create a password", is_password=True)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # Confirm Password
        confirm_container = QWidget()
        confirm_container.setStyleSheet("background: transparent;")
        confirm_layout = QVBoxLayout(confirm_container)
        confirm_layout.setContentsMargins(0, 20, 0, 0)
        confirm_layout.setSpacing(8)
        
        confirm_label = QLabel("Confirm Password")
        confirm_label.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        confirm_label.setStyleSheet("color: #374151;")
        
        self.confirm_input = IconLineEdit("", "Confirm your password", is_password=True)
        
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setFont(QFont("Segoe UI", 11))
        self.error_label.setStyleSheet("""
            color: #dc2626;
            background-color: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 10px;
        """)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setContentsMargins(0, 15, 0, 0)
        self.error_label.hide()
        
        # Success label
        self.success_label = QLabel()
        self.success_label.setFont(QFont("Segoe UI", 11))
        self.success_label.setStyleSheet("""
            color: #16a34a;
            background-color: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            padding: 10px;
        """)
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_label.setContentsMargins(0, 15, 0, 0)
        self.success_label.hide()
        
        # Create Account Button
        btn_container = QWidget()
        btn_container.setStyleSheet("background: transparent;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 25, 0, 0)
        
        self.create_btn = QPushButton("➕ Create Account")
        self.create_btn.setMinimumHeight(52)
        self.create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.create_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: white;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #15803d;
            }
            QPushButton:pressed {
                background-color: #166534;
            }
            QPushButton:disabled {
                background-color: #86efac;
            }
        """)
        self.create_btn.clicked.connect(self.handle_register)
        
        # Add shadow
        btn_shadow = QGraphicsDropShadowEffect(self)
        btn_shadow.setBlurRadius(20)
        btn_shadow.setColor(QColor(22, 163, 74, 80))
        btn_shadow.setOffset(0, 6)
        self.create_btn.setGraphicsEffect(btn_shadow)
        
        btn_layout.addWidget(self.create_btn)
        
        # Back to login link
        back_container = QWidget()
        back_container.setStyleSheet("background: transparent;")
        back_layout = QHBoxLayout(back_container)
        back_layout.setContentsMargins(0, 20, 0, 0)
        back_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        back_label = QLabel("Already have an account?")
        back_label.setFont(QFont("Segoe UI", 12))
        back_label.setStyleSheet("color: #6b7280;")
        
        back_btn = QPushButton("🔐 Sign In")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #2563eb;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                color: #1d4ed8;
            }
        """)
        back_btn.clicked.connect(self.close)
        
        back_layout.addWidget(back_label)
        back_layout.addWidget(back_btn)
        
        # Add all widgets
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(fullname_container)
        layout.addWidget(username_container)
        layout.addWidget(password_container)
        layout.addWidget(confirm_container)
        layout.addWidget(self.error_label)
        layout.addWidget(self.success_label)
        layout.addWidget(btn_container)
        layout.addWidget(back_container)
        layout.addStretch()
        
        # Focus on first input
        self.fullname_input.setFocus()
    
    def handle_register(self):
        """Handle registration"""
        fullname = self.fullname_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        # Validate
        self.error_label.hide()
        self.success_label.hide()
        
        if not fullname or not username or not password or not confirm:
            self.show_error("Please fill in all fields")
            return
        
        if len(username) < 3:
            self.show_error("Username must be at least 3 characters")
            return
        
        if len(password) < 6:
            self.show_error("Password must be at least 6 characters")
            return
        
        if password != confirm:
            self.show_error("Passwords do not match")
            return
        
        # Attempt registration
        self.create_btn.setEnabled(False)
        self.create_btn.setText("Creating...")
        
        try:
            result = user_manager.create_user(
                username=username,
                password=password,
                full_name=fullname,
                role='Staff'
            )
            
            if result:
                self.success_label.setText("Account created successfully! You can now sign in.")
                self.success_label.show()
                self.error_label.hide()
                
                # Clear form
                self.fullname_input.clear()
                self.username_input.clear()
                self.password_input.clear()
                self.confirm_input.clear()
            else:
                self.show_error("Username already exists. Please choose another.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")
        finally:
            self.create_btn.setEnabled(True)
            self.create_btn.setText("Create Account")
    
    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        self.success_label.hide()


class LoginWindow(QMainWindow):
    """
    Clean, professional login window for SwiftPay application.
    Two-panel design with blue branding and white form.
    """
    
    login_success = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the login window UI"""
        self.setWindowTitle("SwiftPay - Login")
        self.setFixedSize(1050, 700)
        self.setStyleSheet("QMainWindow { background-color: #ffffff; }")
        
        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #ffffff;")
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left panel - Blue branding (1/3 width)
        left_panel = self._create_left_panel()
        left_panel.setFixedWidth(400)
        
        # Right panel - Login form (2/3 width)
        right_panel = self._create_right_panel()
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
    
    def _create_left_panel(self):
        """Create the blue branding panel with gradient"""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2563eb, stop:1 #1e40af);
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo
        logo_container = QWidget()
        logo_container.setStyleSheet("background: transparent;")
        logo_container.setMinimumHeight(120)
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.setSpacing(0)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create custom SwiftPay logo (white for blue background)
        logo_widget = SwiftPayLogo(white_text=True)
        logo_widget.setStyleSheet("background: transparent;")
        logo_widget.setMinimumSize(300, 85)
        
        logo_layout.addStretch()
        logo_layout.addWidget(logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        logo_layout.addStretch()
        
        # Tagline
        tagline = QLabel("Payroll Management System")
        tagline.setFont(QFont("Segoe UI", 17, QFont.Weight.Medium))
        tagline.setStyleSheet("color: rgba(255, 255, 255, 0.95); background: transparent;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setContentsMargins(0, 30, 0, 0)
        
        # Features list
        features_container = QWidget()
        features_container.setStyleSheet("background: transparent;")
        features_layout = QVBoxLayout(features_container)
        features_layout.setContentsMargins(0, 60, 0, 0)
        features_layout.setSpacing(24)
        features_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        features = [
            "Enterprise-grade Security",
            "Accurate Payroll Computation",
            "Advanced Analytics & Reports",
        ]
        
        for feature_text in features:
            feature_row = QWidget()
            feature_row.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(feature_row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(16)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
            # Checkmark icon with background circle
            check_container = QFrame()
            check_container.setFixedSize(32, 32)
            check_container.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 16px;
                }
            """)
            check_layout = QVBoxLayout(check_container)
            check_layout.setContentsMargins(0, 0, 0, 0)
            
            check_icon = QLabel("✓")
            check_icon.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            check_icon.setStyleSheet("color: #ffffff; background: transparent;")
            check_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            check_layout.addWidget(check_icon)
            
            feature_label = QLabel(feature_text)
            feature_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
            feature_label.setStyleSheet("color: #ffffff; background: transparent;")
            
            row_layout.addWidget(check_container)
            row_layout.addWidget(feature_label)
            row_layout.addStretch()
            
            features_layout.addWidget(feature_row)
        
        # Assemble layout
        layout.addStretch()
        layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)
        layout.addWidget(features_container)
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self):
        """Create the white login form panel"""
        panel = QWidget()
        panel.setStyleSheet("background-color: #ffffff;")
        
        main_layout = QVBoxLayout(panel)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Center container
        center_container = QWidget()
        center_container.setStyleSheet("background: transparent;")
        center_container.setFixedWidth(420)
        
        form_layout = QVBoxLayout(center_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Welcome header
        welcome_label = QLabel("Welcome Back")
        welcome_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #111827; background: transparent;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Subtitle
        subtitle_label = QLabel("Sign in to continue to your dashboard")
        subtitle_label.setFont(QFont("Segoe UI", 15))
        subtitle_label.setStyleSheet("color: #6B7280; background: transparent; font-weight: 400;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        subtitle_label.setContentsMargins(0, 12, 0, 0)
        
        # Username field
        username_container = QWidget()
        username_container.setStyleSheet("background: transparent;")
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(0, 48, 0, 0)
        username_layout.setSpacing(12)
        
        username_label = QLabel("Username or Email")
        username_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        username_label.setStyleSheet("color: #374151; background: transparent;")
        
        self.username_input = IconLineEdit("👤", "Enter your username or email")
        
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        
        # Password field
        password_container = QWidget()
        password_container.setStyleSheet("background: transparent;")
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 28, 0, 0)
        password_layout.setSpacing(12)
        
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        password_label.setStyleSheet("color: #374151; background: transparent;")
        
        self.password_input = IconLineEdit("🔒", "Enter your password", is_password=True)
        
        # Password toggle button
        from ui.components import PasswordToggleButton
        toggle_btn = PasswordToggleButton(self.password_input.line_edit)
        password_input_layout = QHBoxLayout()
        password_input_layout.setContentsMargins(0, 0, 0, 0)
        password_input_layout.addWidget(self.password_input, 1)
        password_input_layout.addWidget(toggle_btn)
        
        password_widget = QWidget()
        password_widget.setLayout(password_input_layout)
        
        password_layout.addWidget(password_label)
        password_layout.addWidget(password_widget)
        
        # Remember me
        remember_forgot_container = QWidget()
        remember_forgot_container.setStyleSheet("background: transparent;")
        remember_forgot_layout = QHBoxLayout(remember_forgot_container)
        remember_forgot_layout.setContentsMargins(0, 20, 0, 0)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setFont(QFont("Segoe UI", 13))
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #374151;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #D1D5DB;
                border-radius: 5px;
            }
            QCheckBox::indicator:checked {
                background-color: #2563eb;
                border-color: #2563eb;
            }
            QCheckBox::indicator:hover {
                border-color: #9CA3AF;
            }
        """)
        
        remember_forgot_layout.addWidget(self.remember_checkbox)
        remember_forgot_layout.addStretch()
        
        # Error message
        self.error_label = QLabel()
        self.error_label.setFont(QFont("Segoe UI", 13))
        self.error_label.setStyleSheet("""
            color: #DC2626;
            background-color: #FEF2F2;
            border: 1px solid #FECACA;
            border-radius: 10px;
            padding: 14px 16px;
        """)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setContentsMargins(0, 20, 0, 0)
        self.error_label.hide()
        self.error_label.setWordWrap(True)
        
        # Sign in button
        button_container = QWidget()
        button_container.setStyleSheet("background: transparent;")
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 32, 0, 0)
        
        self.login_btn = QPushButton("🔐 Sign In")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #93c5fd;
                color: #E5E7EB;
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        
        # Add shadow to button
        btn_shadow = QGraphicsDropShadowEffect(self)
        btn_shadow.setBlurRadius(24)
        btn_shadow.setColor(QColor(37, 99, 235, 100))
        btn_shadow.setOffset(0, 8)
        self.login_btn.setGraphicsEffect(btn_shadow)
        
        button_layout.addWidget(self.login_btn)
        
        # Add all to form layout (removed default credentials hint for security)
        form_layout.addWidget(welcome_label)
        form_layout.addWidget(subtitle_label)
        form_layout.addWidget(username_container)
        form_layout.addWidget(password_container)
        form_layout.addWidget(remember_forgot_container)
        form_layout.addWidget(self.error_label)
        form_layout.addWidget(button_container)
        form_layout.addStretch()
        
        # Center the form in the panel
        main_layout.addStretch()
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(center_container)
        h_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()
        
        # Connect enter key
        self.username_input.line_edit.returnPressed.connect(self.handle_login)
        self.password_input.line_edit.returnPressed.connect(self.handle_login)
        
        # Focus on username
        self.username_input.setFocus()
        
        return panel
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate input
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Attempt login
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Signing in...")
        
        try:
            user = user_manager.login(username, password)
            
            if user:
                self.error_label.hide()
                self.login_success.emit(user)
                self.close()
            else:
                self.show_error("Invalid username or password")
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            self.show_error(f"Login error: {str(e)}")
        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Sign In")
    
    def show_error(self, message):
        """Display error message"""
        self.error_label.setText(message)
        self.error_label.show()
    
    def clear_form(self):
        """Clear the login form"""
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.hide()
        self.username_input.setFocus()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)
