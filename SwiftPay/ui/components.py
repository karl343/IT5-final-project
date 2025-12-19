"""
SwiftPay UI Components
Reusable UI components for the application
"""

import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QMenu, QCheckBox, QLineEdit, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QPainterPath

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ToastNotification(QWidget):
    """Toast notification widget with animation"""
    
    def __init__(self, message, notification_type="info", parent=None, duration=3000):
        super().__init__(parent)
        self.notification_type = notification_type
        self.duration = duration
        self.init_ui(message)
        self.setup_animation()
    
    def init_ui(self, message):
        """Initialize the toast UI"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Icon/Type indicator
        type_colors = {
            "success": "#10B981",
            "error": "#EF4444",
            "warning": "#F59E0B",
            "info": "#3B82F6"
        }
        
        type_icons = {
            "success": "[OK]",
            "error": "[X]",
            "warning": "[!]",
            "info": "[i]"
        }
        
        icon_label = QLabel(type_icons.get(self.notification_type, "[i]"))
        icon_label.setStyleSheet(f"""
            color: {type_colors.get(self.notification_type, '#3B82F6')};
            font-size: 16px;
            font-weight: bold;
        """)
        
        # Message
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            color: #1A1A1A;
            font-size: 14px;
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        
        # Close button
        close_btn = QPushButton("X")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6B7280;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #1A1A1A;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # Style the container
        container = QFrame()
        container.setObjectName("toastContainer")
        container.setStyleSheet("""
            QFrame#toastContainer {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
            }
        """)
        
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addLayout(layout)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        # Auto-close timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(self.duration)
    
    def setup_animation(self):
        """Setup show/hide animations"""
        # Animation setup - opacity would require QGraphicsOpacityEffect
        # For now, we'll use simple show/hide without opacity animation
        pass
    
    def showEvent(self, event):
        """Animate in on show"""
        super().showEvent(event)
        # Simple show without fade animation for now
        self.show()
    
    def closeEvent(self, event):
        """Animate out on close"""
        event.accept()


class DarkModeToggle(QPushButton):
    """Dark mode toggle button"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None, initial_state=False):
        super().__init__(parent)
        self.is_dark = initial_state
        self.setFixedSize(50, 28)
        self.setCheckable(True)
        self.setChecked(self.is_dark)
        self.clicked.connect(self.toggle_mode)
        self.update_style()
    
    def toggle_mode(self):
        """Toggle dark mode"""
        self.is_dark = not self.is_dark
        self.update_style()
        self.toggled.emit(self.is_dark)
    
    def update_style(self):
        """Update button style based on state"""
        if self.is_dark:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0055FF;
                    border: none;
                    border-radius: 14px;
                }
                QPushButton::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background-color: white;
                    left: 25px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #D1D5DB;
                    border: none;
                    border-radius: 14px;
                }
                QPushButton::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    background-color: white;
                    left: 5px;
                }
            """)


class NotificationButton(QPushButton):
    """Notification bell button with badge - Modern custom icon"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self.setObjectName("notificationBtn")
        self.badge_count = 0
        self.setStyleSheet("""
            QPushButton#notificationBtn {
                background-color: transparent;
                border: none;
                border-radius: 10px;
            }
            QPushButton#notificationBtn:hover {
                background-color: #F3F4F6;
            }
        """)
        
        # Create menu
        self.menu = QMenu(self)
        self.setMenu(self.menu)
    
    def set_badge_count(self, count):
        """Set notification badge count"""
        self.badge_count = count
        self.update()
    
    def paintEvent(self, event):
        """Draw custom bell icon and badge"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw bell icon
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        painter.setPen(QPen(QColor("#6B7280"), 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Bell body (simplified arc shape)
        bell_width = 16
        bell_height = 14
        bell_x = center_x - bell_width / 2
        bell_y = center_y - bell_height / 2
        
        # Draw bell as rounded shape
        bell_path = QPainterPath()
        bell_path.moveTo(bell_x + 4, bell_y)
        bell_path.arcTo(bell_x, bell_y, bell_width, bell_height * 1.4, 0, 180)
        bell_path.lineTo(bell_x + 4, bell_y)
        painter.drawPath(bell_path)
        
        # Bell clapper (small circle at bottom)
        clapper_y = bell_y + bell_height + 1
        painter.setBrush(QColor("#6B7280"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - 2.5), int(clapper_y), 5, 5)
        
        # Bell handle (small rounded rectangle at top)
        handle_x = center_x - 3
        handle_y = bell_y - 3
        painter.setBrush(QColor("#6B7280"))
        painter.drawRoundedRect(int(handle_x), int(handle_y), 6, 3, 1.5, 1.5)
        
        # Draw badge if count > 0
        if self.badge_count > 0:
            badge_x = self.width() - 18
            badge_y = 6
            badge_size = 18
            
            # Badge shadow
            painter.setBrush(QColor(0, 0, 0, 30))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(badge_x + 1, badge_y + 1, badge_size, badge_size)
            
            # Badge circle
            painter.setBrush(QColor("#EF4444"))
            painter.drawEllipse(badge_x, badge_y, badge_size, badge_size)
            
            # Badge text
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            count_text = str(self.badge_count) if self.badge_count < 100 else "99+"
            painter.drawText(badge_x, badge_y, badge_size, badge_size, Qt.AlignmentFlag.AlignCenter, count_text)


class DarkModeToggleButton(QPushButton):
    """Dark mode toggle button with custom sun/moon icon"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
        self.setCheckable(True)
        self.setObjectName("darkModeToggle")
        self.setStyleSheet("""
            QPushButton#darkModeToggle {
                background-color: #F3F4F6;
                border: none;
                border-radius: 10px;
            }
            QPushButton#darkModeToggle:hover {
                background-color: #E5E7EB;
            }
            QPushButton#darkModeToggle:checked {
                background-color: #0055FF;
            }
        """)
    
    def paintEvent(self, event):
        """Draw custom sun/moon icon"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        if self.isChecked():
            # Moon icon (dark mode) - white crescent
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
            painter.setBrush(QColor("#FFFFFF"))
            
            # Moon shape (crescent)
            moon_path = QPainterPath()
            moon_path.addEllipse(center_x - 8, center_y - 8, 16, 16)
            moon_inner = QPainterPath()
            moon_inner.addEllipse(center_x - 2, center_y - 8, 16, 16)
            moon_path = moon_path.subtracted(moon_inner)
            painter.fillPath(moon_path, QColor("#FFFFFF"))
        else:
            # Light mode - simple circle icon
            painter.setPen(QPen(QColor("#6B7280"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Simple circle
            painter.drawEllipse(int(center_x - 8), int(center_y - 8), 16, 16)


class PasswordToggleButton(QPushButton):
    """Password visibility toggle button"""
    
    def __init__(self, line_edit, parent=None):
        super().__init__(parent)
        self.line_edit = line_edit
        self.is_visible = False
        self.setFixedSize(40, 40)
        self.setText("Show")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                padding: 0;
            }
            QPushButton:hover {
                opacity: 0.7;
            }
        """)
        self.clicked.connect(self.toggle_visibility)
    
    def toggle_visibility(self):
        """Toggle password visibility"""
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.setText("Hide")
        else:
            self.line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.setText("Show")


def show_toast(parent, message, notification_type="info", duration=3000):
    """Show a toast notification"""
    toast = ToastNotification(message, notification_type, parent, duration)
    
    # Position toast (top-right corner)
    if parent:
        parent_geometry = parent.geometry()
        toast.move(
            parent_geometry.right() - toast.width() - 20,
            parent_geometry.top() + 80
        )
    else:
        toast.move(500, 100)
    
    toast.show()
    return toast

