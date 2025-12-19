import sys
import os

# Add project root to path if running directly
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QFrame, QApplication)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from views.admin_dashboard import AdminDashboardView
from views.customer_dashboard import CustomerDashboardView
from views.room_view import RoomView
from views.reservation_view import ReservationView
from views.users_view import UsersView
from views.reports_view import ReportsView

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.logging_out = False # Flag to track logout
        self.setWindowTitle("STAYEASE Hotel Management")
        self.resize(1200, 800)
        self.init_ui()

    def logout(self):
        self.logging_out = True
        self.close()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(10)

        # App Logo/Title
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 10, 0, 20)
        
        logo_icon = QLabel()
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_icon.setPixmap(pixmap.scaledToWidth(180, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_icon.setText("STAYEASE")
            logo_icon.setObjectName("LogoText")
            logo_icon.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff;") # Override for dark sidebar
            
        logo_layout.addWidget(logo_icon)
        
        sidebar_layout.addWidget(logo_container)

        # Navigation Buttons
        self.nav_buttons = []
        self.add_nav_button("📊 Dashboard", 0, sidebar_layout)
        
        if self.user.role in ['Admin', 'Receptionist']:
            self.add_nav_button("🛏️ Rooms", 1, sidebar_layout)
            self.add_nav_button("📅 Reservations", 2, sidebar_layout)
        
        if self.user.role == 'Customer':
            self.add_nav_button("📅 My Bookings", 2, sidebar_layout)

        if self.user.role == 'Admin':
            self.add_nav_button("👥 Users", 3, sidebar_layout)
            self.add_nav_button("📈 Reports", 4, sidebar_layout)

        sidebar_layout.addStretch()
        
        # User Info
        user_card = QFrame()
        user_card.setObjectName("UserCard") # Added ID for styling
        user_layout = QVBoxLayout(user_card)
        user_layout.setSpacing(5)
        
        user_name = QLabel(self.user.username)
        user_name.setObjectName("UserName") # Added ID for styling
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_layout.addWidget(user_name)
        
        user_role = QLabel(self.user.role)
        user_role.setObjectName("UserRole") # Added ID for styling
        user_role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_layout.addWidget(user_role)
        
        sidebar_layout.addWidget(user_card)

        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("DangerButton")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(self.sidebar)

        # Content Area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        self.header = QWidget()
        self.header.setObjectName("Header")
        self.header.setFixedHeight(70)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.header_title = QLabel("Dashboard")
        self.header_title.setObjectName("HeaderTitle")
        header_layout.addWidget(self.header_title)
        
        header_layout.addStretch()
        
        # Date/Time placeholder or notifications could go here
        date_lbl = QLabel("Today")
        date_lbl.setStyleSheet("color: #78909c; font-weight: 600;")
        header_layout.addWidget(date_lbl)
        
        content_layout.addWidget(self.header)

        # Stacked Widget for Pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)

        # Initialize Pages
        if self.user.role in ['Admin', 'Receptionist']:
            self.dashboard_view = AdminDashboardView(self.user)
            self.stacked_widget.addWidget(self.dashboard_view)
            
            self.room_view = RoomView(self.user)
            self.stacked_widget.addWidget(self.room_view)
            
            self.reservation_view = ReservationView(self.user)
            self.stacked_widget.addWidget(self.reservation_view)
            
        elif self.user.role == 'Customer':
             self.dashboard_view = CustomerDashboardView(self.user)
             self.stacked_widget.addWidget(self.dashboard_view)
             
             # Customer might see rooms differently, but reusing RoomView for now
             self.room_view = RoomView(self.user) 
             self.stacked_widget.addWidget(self.room_view)
             
             self.reservation_view = ReservationView(self.user)
             self.stacked_widget.addWidget(self.reservation_view)

        # Admin only pages
        if self.user.role == 'Admin':
            self.users_view = UsersView(self.user)
            self.stacked_widget.addWidget(self.users_view)
            
            self.reports_view = ReportsView(self.user)
            self.stacked_widget.addWidget(self.reports_view)

        main_layout.addWidget(content_area)

    def add_nav_button(self, text, index, layout):
        btn = QPushButton(text)
        btn.setObjectName("SidebarButton")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.switch_page(index, text, btn))
        layout.addWidget(btn)
        self.nav_buttons.append(btn)
        if index == 0:
            btn.setChecked(True)

    def switch_page(self, index, title, sender_btn):
        self.stacked_widget.setCurrentIndex(index)
        self.header_title.setText(title)
        
        for btn in self.nav_buttons:
            btn.setChecked(False)
        sender_btn.setChecked(True)
        
        # Refresh data if needed
        if index == 0:
            self.dashboard_view.refresh_data()
        elif index == 1:
            if hasattr(self, 'room_view'): self.room_view.refresh_data()
        elif index == 2:
            if hasattr(self, 'reservation_view'): self.reservation_view.refresh_data()
        elif index == 3:
            if hasattr(self, 'users_view'): self.users_view.refresh_data()
        elif index == 4:
            if hasattr(self, 'reports_view'): self.reports_view.load_reservations()

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
            
    # Load stylesheet if available
    style_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())

    try:
        window = MainWindow(MockUser())
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error running view: {e}")
