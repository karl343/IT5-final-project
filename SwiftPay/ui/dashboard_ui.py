"""
SwiftPay Dashboard Window
Main application window with sidebar navigation
"""

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget, QSizePolicy, QSpacerItem,
    QMessageBox, QScrollArea, QMenu, QGridLayout, QTableWidget,
    QTableWidgetItem, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QColor

# Import matplotlib with error handling
try:
    import matplotlib
    # Use QtAgg backend for PyQt6 compatibility
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    print(f"Warning: matplotlib not available: {e}")
    MATPLOTLIB_AVAILABLE = False
    # Create dummy classes if matplotlib is not available
    class FigureCanvas:
        def __init__(self, *args, **kwargs):
            pass
        def draw(self):
            pass
    class Figure:
        def __init__(self, *args, **kwargs):
            pass
        def clear(self):
            pass
        def add_subplot(self, *args, **kwargs):
            class DummyAxes:
                def bar(self, *args, **kwargs):
                    return []
                def pie(self, *args, **kwargs):
                    return [], [], []
                def set_xlabel(self, *args, **kwargs):
                    pass
                def set_ylabel(self, *args, **kwargs):
                    pass
                def set_title(self, *args, **kwargs):
                    pass
                def set_xticks(self, *args, **kwargs):
                    pass
                def set_xticklabels(self, *args, **kwargs):
                    pass
                def set_ylim(self, *args, **kwargs):
                    pass
                def legend(self, *args, **kwargs):
                    pass
                def grid(self, *args, **kwargs):
                    pass
            return DummyAxes()
        def tight_layout(self):
            pass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.styles import Styles
from ui.login_ui import SwiftPayLogo
from modules.reports import report_manager


class StatCard(QFrame):
    """
    Modern, interactive statistics card widget for dashboard.
    """
    
    def __init__(self, title, value, subtitle="", color="primary", icon=""):
        super().__init__()
        self.color = color
        self.setup_ui(title, value, subtitle, color, icon)
    
    def setup_ui(self, title, value, subtitle, color, icon):
        """Setup the card UI with modern design"""
        colors = {
            'primary': ('#0055FF', '#0033CC', 'white'),
            'success': ('#10B981', '#059669', 'white'),
            'warning': ('#F59E0B', '#D97706', 'white'),
            'info': ('#0277BD', '#01579B', 'white'),
            'secondary': ('#6B7280', '#4B5563', 'white')
        }
        
        bg_color, hover_color, text_color = colors.get(color, colors['primary'])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 16px;
                padding: 0px;
                border: none;
            }}
            QFrame:hover {{
                background-color: {hover_color};
                transform: translateY(-2px);
            }}
        """)
        self.setMinimumSize(260, 160)
        self.setMaximumHeight(180)
        
        # Main layout with accent bar
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left accent bar
        accent_bar = QFrame()
        accent_bar.setFixedWidth(6)
        accent_bar.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.3);
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }}
        """)
        main_layout.addWidget(accent_bar)
        
        # Content layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 20)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"color: rgba(255, 255, 255, 0.95); font-size: 26px;")
            icon_label.setFixedWidth(36)
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: rgba(255, 255, 255, 0.95); font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: {text_color}; font-size: 38px; font-weight: 700; margin-top: 4px; letter-spacing: -1px;")
        
        # Subtitle
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"color: rgba(255, 255, 255, 0.8); font-size: 12px; margin-top: 2px;")
        
        layout.addWidget(self.value_label)
        if subtitle:
            layout.addWidget(self.subtitle_label)
        layout.addStretch()
        
        main_layout.addLayout(layout)
    
    def update_value(self, value):
        """Update the displayed value"""
        self.value_label.setText(str(value))
    
    def update_subtitle(self, subtitle):
        """Update the subtitle text"""
        self.subtitle_label.setText(subtitle)


class DashboardWindow(QMainWindow):
    """
    Main dashboard window for SwiftPay application.
    Contains sidebar navigation and main content area.
    """
    
    def darken_color(self, hex_color, factor=0.15):
        """Darken a hex color by a factor"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            # Darken
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    logout_requested = pyqtSignal()
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.current_page = None
        self.nav_buttons = {}
        self.dark_mode = False
        self.init_ui()
        self.load_dashboard_stats()
    
    def init_ui(self):
        """Initialize the dashboard UI"""
        # Window settings
        self.setWindowTitle("SwiftPay - Payroll Management System")
        self.setMinimumSize(1400, 800)
        self.setStyleSheet(Styles.MAIN_STYLE)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f8f9fa;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header
        self.header = self.create_header()
        content_layout.addWidget(self.header)
        
        # Stacked widget for pages
        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages)
        
        # Add pages
        self.create_pages()
        
        main_layout.addWidget(content_widget, 1)
        
        # Navigate to dashboard
        self.navigate_to("dashboard")
    
    def create_sidebar(self):
        """Create the sidebar navigation"""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(Styles.SIDEBAR_STYLE)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo section
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(15, 25, 15, 20)
        logo_layout.setSpacing(10)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create SwiftPay logo (white text for dark sidebar)
        logo = SwiftPayLogo(white_text=True)
        # Scale down for sidebar
        logo.setFixedSize(220, 62)  # Scaled down from 300x85
        
        # Subtitle below logo
        subtitle = QLabel("Payroll Management")
        subtitle.setObjectName("sidebarSubtitle")
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 11px; margin-top: 5px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_widget)
        
        # Navigation buttons
        nav_items = [
            ("dashboard", "Dashboard"),
            ("employees", "Employees"),
            ("attendance", "Attendance"),
            ("payroll", "Payroll"),
            ("reports", "Reports"),
        ]
        
        # Add admin-only items
        if self.user_data.get('role') == 'Admin':
            nav_items.append(("users", "Users"))
            nav_items.append(("audit_log", "Audit Log"))
        
        for page_id, label in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("sidebarBtn")
            btn.setCheckable(True)
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, p=page_id: self.navigate_to(p))
            self.nav_buttons[page_id] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        
        return sidebar
    
    def create_header(self):
        """Create the top header bar with dark mode toggle and notifications"""
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid #E5E7EB;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        layout.setSpacing(15)
        
        # Page title
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet("font-size: 22px; font-weight: 600; color: #1A1A1A;")
        
        layout.addWidget(self.page_title)
        layout.addStretch()
        
        # Date/Time - Modern styling
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("""
            color: #6B7280; 
            font-size: 14px; 
            font-weight: 500;
            padding: 8px 16px;
            background-color: #f9fafb;
            border-radius: 8px;
        """)
        self.update_datetime()
        layout.addWidget(self.datetime_label)
        
        # Dark mode toggle with custom icon
        from ui.components import DarkModeToggleButton
        dark_toggle = DarkModeToggleButton()
        dark_toggle.setChecked(self.dark_mode)
        dark_toggle.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(dark_toggle)
        
        # User profile section - Top right corner
        user_container = QWidget()
        user_container.setStyleSheet("background: transparent;")
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(12)
        
        # User info (name and role)
        user_info = QWidget()
        user_info.setStyleSheet("background: transparent;")
        user_info_layout = QVBoxLayout(user_info)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)
        user_info_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        user_name = QLabel(self.user_data.get('full_name', 'User'))
        user_name.setStyleSheet("""
            color: #111827; 
            font-weight: 600; 
            font-size: 14px;
        """)
        user_name.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        user_role = QLabel(self.user_data.get('role', 'Staff'))
        user_role.setStyleSheet("""
            color: #6B7280; 
            font-size: 12px;
        """)
        user_role.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        user_info_layout.addWidget(user_name)
        user_info_layout.addWidget(user_role)
        
        # Logout button
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setFixedSize(80, 36)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        
        user_layout.addWidget(user_info)
        user_layout.addWidget(logout_btn)
        
        layout.addWidget(user_container)
        
        return header
    
    def toggle_dark_mode(self):
        """Toggle dark mode"""
        self.dark_mode = not self.dark_mode
        # TODO: Apply dark mode styles
        # This would update all widgets with dark mode colors
        # For now, just toggle the button icon
        sender = self.sender()
        sender.setText("☀️" if self.dark_mode else "🌙")
        # Emit signal for future dark mode implementation
        # self.dark_mode_toggled.emit(self.dark_mode)
    
    def update_datetime(self):
        """Update the datetime display with auto-refresh"""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%A, %B %d, %Y | %I:%M %p"))
        
        # Auto-update every minute
        from PyQt6.QtCore import QTimer
        if not hasattr(self, '_datetime_timer_initialized'):
            self._datetime_timer_initialized = True
            self.datetime_timer = QTimer(self)
            self.datetime_timer.timeout.connect(self.update_datetime)
            self.datetime_timer.start(60000)  # Update every 60 seconds
    
    def create_pages(self):
        """Create all page widgets"""
        # Store page mapping dynamically
        self.page_indices = {}
        
        # Dashboard page
        self.dashboard_page = self.create_dashboard_page()
        self.pages.addWidget(self.dashboard_page)
        self.page_indices['dashboard'] = 0
        
        # Import and create other pages
        from ui.employees_ui import EmployeesPage
        from ui.attendance_ui import AttendancePage
        from ui.payroll_ui import PayrollPage
        from ui.reports_ui import ReportsPage
        
        self.employees_page = EmployeesPage()
        self.pages.addWidget(self.employees_page)
        self.page_indices['employees'] = 1
        
        self.attendance_page = AttendancePage()
        self.pages.addWidget(self.attendance_page)
        self.page_indices['attendance'] = 2
        
        self.payroll_page = PayrollPage(self.user_data)
        self.pages.addWidget(self.payroll_page)
        self.page_indices['payroll'] = 3
        
        self.reports_page = ReportsPage()
        self.pages.addWidget(self.reports_page)
        self.page_indices['reports'] = 4
        
        # Users page (admin only)
        if self.user_data.get('role') == 'Admin':
            from ui.users_ui import UsersPage
            from ui.audit_log_ui import AuditLogPage
            self.users_page = UsersPage()
            self.pages.addWidget(self.users_page)
            self.page_indices['users'] = 5
            
            try:
                self.audit_log_page = AuditLogPage(self.user_data)
                self.pages.addWidget(self.audit_log_page)
                self.page_indices['audit_log'] = 6
            except Exception as e:
                print(f"Error creating audit log page: {e}")
                # Create a placeholder page if audit log fails to load
                error_page = QWidget()
                error_layout = QVBoxLayout(error_page)
                error_label = QLabel(f"Error loading audit log: {str(e)}")
                error_label.setStyleSheet("color: red; font-size: 14px; padding: 20px;")
                error_layout.addWidget(error_label)
                self.pages.addWidget(error_page)
                self.page_indices['audit_log'] = 6
    
    def create_dashboard_page(self):
        """Create the dashboard overview page"""
        page = QWidget()
        page.setStyleSheet("background-color: #f8f9fa;")
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header section - Clean and modern
        header_label = QLabel("Dashboard")
        header_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: 700; 
            color: #111827;
            margin-bottom: 8px;
        """)
        layout.addWidget(header_label)
        
        subtitle = QLabel("Welcome back! Here's what's happening with your payroll system.")
        subtitle.setStyleSheet("""
            font-size: 14px; 
            color: #6B7280; 
            margin-bottom: 32px;
            font-weight: 400;
        """)
        layout.addWidget(subtitle)
        
        # Statistics cards row - Modern KPI cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.emp_card = StatCard("Total Employees", "0", "", "primary", "👥")
        self.attendance_card = StatCard("Present Today", "0", "", "success", "✅")
        self.payroll_card = StatCard("Monthly Payroll", "₱0", "", "warning", "💰")
        self.pending_card = StatCard("Pending Approvals", "0", "", "info", "⏳")
        
        stats_layout.addWidget(self.emp_card)
        stats_layout.addWidget(self.attendance_card)
        stats_layout.addWidget(self.payroll_card)
        stats_layout.addWidget(self.pending_card)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # KPI Section - Two columns layout
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left column - Recent Payrolls
        recent_payrolls_card = self.create_recent_payrolls_section()
        kpi_layout.addWidget(recent_payrolls_card, 1)
        
        # Right column - Top Employees & Quick Actions
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(20)
        
        top_employees_card = self.create_top_employees_section()
        quick_actions_card = self.create_quick_actions_section()
        
        right_layout.addWidget(top_employees_card, 1)
        right_layout.addWidget(quick_actions_card)
        
        kpi_layout.addWidget(right_column, 1)
        
        layout.addLayout(kpi_layout)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_content)
        
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
        return page
    
    def create_recent_payrolls_section(self):
        """Create recent payrolls table section"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid #E5E7EB;
            }
            QFrame:hover {
                border-color: #0055FF40;
                box-shadow: 0px 4px 16px rgba(0, 85, 255, 0.08);
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header with improved styling
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)
        
        # Icon container with background
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QFrame {
                background-color: #0055FF15;
                border-radius: 10px;
                border: 1px solid #0055FF30;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("💰")
        icon.setStyleSheet("font-size: 22px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon)
        
        title = QLabel("Recent Payrolls")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; letter-spacing: -0.3px;")
        
        header.addWidget(icon_container)
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Table
        self.recent_payrolls_table = QTableWidget()
        self.recent_payrolls_table.setColumnCount(4)
        self.recent_payrolls_table.setHorizontalHeaderLabels(["Period", "Employees", "Net Pay", "Date"])
        self.recent_payrolls_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.recent_payrolls_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.recent_payrolls_table.verticalHeader().setVisible(False)
        self.recent_payrolls_table.setMaximumHeight(300)
        self.recent_payrolls_table.setWordWrap(True)  # Enable word wrapping
        self.recent_payrolls_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: transparent;
                selection-background-color: #EFF6FF;
                selection-color: #111827;
            }
            QTableWidget::item {
                padding: 16px 12px;
                border-bottom: 1px solid #F3F4F6;
                font-size: 13px;
            }
            QTableWidget::item:hover {
                background-color: #F9FAFB;
            }
            QTableWidget::item:selected {
                background-color: #0055FF15;
                color: #111827;
                border-left: 3px solid #0055FF;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #374151;
                padding: 14px 12px;
                border: none;
                border-bottom: 2px solid #0055FF;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)
        
        header_view = self.recent_payrolls_table.horizontalHeader()
        # Set minimum widths to prevent text cutoff
        header_view.setMinimumSectionSize(100)
        # Period column gets more space, others are sized to content
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set minimum column widths
        self.recent_payrolls_table.setColumnWidth(0, 200)  # Period - wider for full text
        self.recent_payrolls_table.setColumnWidth(1, 90)   # Employees
        self.recent_payrolls_table.setColumnWidth(2, 120)  # Net Pay
        self.recent_payrolls_table.setColumnWidth(3, 110)  # Date
        
        layout.addWidget(self.recent_payrolls_table)
        
        return card
    
    def create_top_employees_section(self):
        """Create top employees by attendance section"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid #E5E7EB;
            }
            QFrame:hover {
                border-color: #10B98140;
                box-shadow: 0px 4px 16px rgba(16, 185, 129, 0.08);
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header with improved styling
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)
        
        # Icon container with background
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QFrame {
                background-color: #10B98115;
                border-radius: 10px;
                border: 1px solid #10B98130;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("🏆")
        icon.setStyleSheet("font-size: 22px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon)
        
        title = QLabel("Top Employees This Month")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; letter-spacing: -0.3px;")
        
        header.addWidget(icon_container)
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Employee list
        self.top_employees_list = QWidget()
        self.top_employees_layout = QVBoxLayout(self.top_employees_list)
        self.top_employees_layout.setContentsMargins(0, 0, 0, 0)
        self.top_employees_layout.setSpacing(12)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.top_employees_list)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F3F4F6;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
        """)
        scroll.setMaximumHeight(250)
        
        layout.addWidget(scroll)
        
        return card
    
    def create_quick_actions_section(self):
        """Create quick actions section"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid #E5E7EB;
            }
            QFrame:hover {
                border-color: #F59E0B40;
                box-shadow: 0px 4px 16px rgba(245, 158, 11, 0.08);
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header with improved styling
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)
        
        # Icon container with background
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QFrame {
                background-color: #F59E0B15;
                border-radius: 10px;
                border: 1px solid #F59E0B30;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("🚀")
        icon.setStyleSheet("font-size: 22px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon)
        
        title = QLabel("Quick Actions")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827; letter-spacing: -0.3px;")
        
        header.addWidget(icon_container)
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Action buttons grid
        actions_grid = QGridLayout()
        actions_grid.setSpacing(12)
        
        actions = [
            ("➕ Add Employee", "employees", "#0055FF"),
            ("🕐 Clock In/Out", "attendance", "#10B981"),
            ("⚙️ Generate Payroll", "payroll", "#F59E0B"),
            ("📊 View Reports", "reports", "#3B82F6"),
        ]
        
        for idx, (text, page, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setMinimumHeight(56)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Calculate darker hover color
            hover_color = self.darken_color(color, 0.15)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 600;
                    padding: 14px;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 0.25)};
                    transform: translateY(0px);
                }}
            """)
            btn.clicked.connect(lambda checked, p=page: self.navigate_to(p))
            actions_grid.addWidget(btn, idx // 2, idx % 2)
        
        layout.addLayout(actions_grid)
        
        return card
    
    def create_performance_metrics_section(self):
        """Create performance metrics section"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid #E5E7EB;
            }
            QFrame:hover {
                border-color: #D1D5DB;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        
        icon = QLabel("📈")
        icon.setStyleSheet("font-size: 20px;")
        icon.setFixedSize(32, 32)
        
        title = QLabel("Performance Metrics")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #111827;")
        
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(20)
        
        self.metric_cards = {}
        metrics = [
            ("Total Hours This Week", "total_hours", "⏰", "#0055FF"),
            ("Net Pay This Month", "net_pay", "💰", "#10B981"),
            ("Average Attendance Rate", "attendance_rate", "📈", "#F59E0B"),
            ("Pending Tasks", "pending_tasks", "⏳", "#EF4444"),
        ]
        
        for idx, (label, key, emoji, color) in enumerate(metrics):
            metric_card = QFrame()
            metric_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}10;
                    border: 2px solid {color}40;
                    border-radius: 12px;
                    padding: 20px;
                }}
                QFrame:hover {{
                    background-color: {color}20;
                    border-color: {color};
                    box-shadow: 0px 4px 12px {color}30;
                }}
            """)
            metric_layout = QVBoxLayout(metric_card)
            metric_layout.setSpacing(12)
            metric_layout.setContentsMargins(16, 16, 16, 16)
            
            metric_header = QHBoxLayout()
            metric_header.setContentsMargins(0, 0, 0, 0)
            metric_header.setSpacing(10)
            metric_icon = QLabel(emoji)
            metric_icon.setStyleSheet("font-size: 24px;")
            metric_icon.setFixedSize(32, 32)
            metric_label = QLabel(label)
            metric_label.setStyleSheet("color: #6B7280; font-size: 13px; font-weight: 500;")
            metric_header.addWidget(metric_icon)
            metric_header.addWidget(metric_label)
            metric_header.addStretch()
            
            value_label = QLabel("0")
            value_label.setObjectName("value")
            value_label.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: 700; margin-top: 4px;")
            self.metric_cards[key] = value_label
            
            metric_layout.addLayout(metric_header)
            metric_layout.addWidget(value_label)
            metric_layout.addStretch()
            
            metrics_grid.addWidget(metric_card, idx // 2, idx % 2)
        
        layout.addLayout(metrics_grid)
        
        return card
    
    def load_recent_payrolls(self):
        """Load recent payrolls into table"""
        try:
            from modules.payroll import payroll_manager
            payrolls = payroll_manager.get_all_payrolls(limit=5)
            
            if not hasattr(self, 'recent_payrolls_table'):
                return
                
            self.recent_payrolls_table.setRowCount(0)
            
            for row, pr in enumerate(payrolls):
                self.recent_payrolls_table.insertRow(row)
                
                # Format period text to be more compact
                period = pr.get('payroll_period', 'N/A')
                # Shorten period text if too long (e.g., "Dec 1 - Dec 16" instead of "December 1 - December 16")
                if period and period != 'N/A':
                    # Try to shorten month names
                    period_short = period.replace('January', 'Jan').replace('February', 'Feb').replace('March', 'Mar')
                    period_short = period_short.replace('April', 'Apr').replace('May', 'May').replace('June', 'Jun')
                    period_short = period_short.replace('July', 'Jul').replace('August', 'Aug').replace('September', 'Sep')
                    period_short = period_short.replace('October', 'Oct').replace('November', 'Nov').replace('December', 'Dec')
                    period = period_short
                
                employees = str(pr.get('total_employees', 0))
                net_val = float(pr.get('total_net_pay', 0))
                net_pay = f"₱{net_val:,.2f}"
                
                start_date = pr.get('start_date', '')
                if hasattr(start_date, 'strftime'):
                    date_str = start_date.strftime('%Y-%m-%d')
                else:
                    date_str = str(start_date)
                
                # Period column - ensure full text is visible
                period_item = QTableWidgetItem(period)
                period_item.setForeground(QColor("#111827"))
                period_item.setToolTip(pr.get('payroll_period', period))  # Show original full text on hover
                period_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.recent_payrolls_table.setItem(row, 0, period_item)
                
                # Employees column
                emp_item = QTableWidgetItem(f"👥 {employees}")
                emp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                emp_item.setForeground(QColor("#6B7280"))
                self.recent_payrolls_table.setItem(row, 1, emp_item)
                
                # Net Pay column - color code based on value
                net_item = QTableWidgetItem(net_pay)
                net_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if net_val < 0:
                    net_item.setForeground(QColor("#EF4444"))  # Red for negative (system color)
                else:
                    net_item.setForeground(QColor("#10B981"))  # Green for positive (system color)
                self.recent_payrolls_table.setItem(row, 2, net_item)
                
                # Date column
                date_item = QTableWidgetItem(f"📅 {date_str}")
                date_item.setForeground(QColor("#6B7280"))
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.recent_payrolls_table.setItem(row, 3, date_item)
                
                # Set row height for better spacing
                self.recent_payrolls_table.setRowHeight(row, 50)
        except Exception as e:
            print(f"Error loading recent payrolls: {e}")
    
    def load_top_employees(self):
        """Load top employees by attendance"""
        try:
            from modules.attendance import attendance_manager
            from modules.employees import employee_manager
            from datetime import datetime, timedelta
            
            if not hasattr(self, 'top_employees_layout'):
                return
                
            # Clear existing
            for i in reversed(range(self.top_employees_layout.count())):
                item = self.top_employees_layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
            
            # Get employees and their attendance this month
            employees = employee_manager.get_active_employees()
            start_date = datetime.now().replace(day=1).date()
            end_date = datetime.now().date()
            
            employee_stats = []
            for emp in employees[:10]:  # Top 10
                emp_id = emp.get('employee_id')
                try:
                    attendance_records = attendance_manager.get_attendance_by_date_range(emp_id, start_date, end_date)
                    if attendance_records:
                        present_count = sum(1 for rec in attendance_records if rec.get('status') == 'Present')
                        total_hours = sum(float(rec.get('hours_worked', 0) or 0) for rec in attendance_records)
                    else:
                        present_count = 0
                        total_hours = 0
                except:
                    present_count = 0
                    total_hours = 0
                
                employee_stats.append({
                    'employee': emp,
                    'present': present_count,
                    'hours': total_hours
                })
            
            # Sort by present days
            employee_stats.sort(key=lambda x: x['present'], reverse=True)
            
            # Display top 5
            for stat in employee_stats[:5]:
                emp = stat['employee']
                name = f"{emp.get('first_name', '')} {emp.get('last_name', '')}"
                
                item_widget = QFrame()
                item_widget.setStyleSheet("""
                    QFrame {
                        background-color: #F9FAFB;
                        border-radius: 12px;
                        padding: 16px;
                        border: 1px solid #E5E7EB;
                    }
                    QFrame:hover {
                        background-color: #F3F4F6;
                        border-color: #10B981;
                        box-shadow: 0px 2px 8px rgba(16, 185, 129, 0.1);
                        transform: translateX(4px);
                    }
                """)
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(12)
                
                # Add emoji icon for employee
                emp_icon = QLabel("👤")
                emp_icon.setStyleSheet("font-size: 18px;")
                emp_icon.setFixedSize(24, 24)
                
                name_label = QLabel(name)
                name_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #111827;")
                
                stats_label = QLabel(f"📅 {stat['present']} days • ⏰ {stat['hours']:.1f}h")
                stats_label.setStyleSheet("font-size: 12px; color: #6B7280; font-weight: 500;")
                
                item_layout.addWidget(emp_icon)
                
                # Name and stats in vertical layout
                info_layout = QVBoxLayout()
                info_layout.setContentsMargins(0, 0, 0, 0)
                info_layout.setSpacing(4)
                
                info_layout.addWidget(name_label)
                info_layout.addWidget(stats_label)
                
                item_layout.addLayout(info_layout)
                item_layout.addStretch()
                
                self.top_employees_layout.addWidget(item_widget)
        except Exception as e:
            print(f"Error loading top employees: {e}")
    
    def load_performance_metrics(self):
        """Load performance metrics"""
        try:
            from modules.payroll import payroll_manager
            from datetime import datetime, timedelta
            
            if not hasattr(self, 'metric_cards'):
                return
            
            # Total hours this week - get from database directly
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0).date()
            week_end = datetime.now().date()
            
            query = """
                SELECT COALESCE(SUM(hours_worked), 0) as total_hours
                FROM attendance
                WHERE attendance_date BETWEEN %s AND %s
            """
            from database.db import db
            result = db.execute_query(query, (week_start, week_end), fetch_one=True)
            total_hours = float(result.get('total_hours', 0) or 0) if result else 0
            
            if 'total_hours' in self.metric_cards:
                self.metric_cards['total_hours'].setText(f"{total_hours:.1f} / 40")
            
            # Net pay this month
            current_month = datetime.now().month
            current_year = datetime.now().year
            monthly_summary = payroll_manager.get_payroll_summary(current_year, current_month)
            net_pay = monthly_summary.get('total_net', 0)
            
            if 'net_pay' in self.metric_cards:
                self.metric_cards['net_pay'].setText(f"₱{net_pay:,.0f}")
            
            # Attendance rate
            from modules.reports import report_manager
            stats = report_manager.get_dashboard_stats()
            attendance = stats.get('today_attendance', {})
            present = attendance.get('present', 0)
            total_active = attendance.get('total_active', 1)
            rate = (present / total_active * 100) if total_active > 0 else 0
            
            if 'attendance_rate' in self.metric_cards:
                self.metric_cards['attendance_rate'].setText(f"{rate:.0f}%")
            
            # Pending tasks
            pending = report_manager.get_pending_approvals()
            if 'pending_tasks' in self.metric_cards:
                self.metric_cards['pending_tasks'].setText(str(pending))
        except Exception as e:
            print(f"Error loading performance metrics: {e}")
            import traceback
            traceback.print_exc()
    
    def create_weekly_attendance_chart(self):
        """Create weekly attendance bar chart with modern styling"""
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid #e5e7eb;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(12, 12, 12, 12)
        chart_layout.setSpacing(12)
        
        # Title with icon - Clean left alignment
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        
        title_icon = QLabel("📈")
        title_icon.setStyleSheet("font-size: 22px;")
        title_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_icon.setFixedSize(36, 36)
        
        title = QLabel("Weekly Attendance")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: 600; 
            color: #111827;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        chart_layout.addLayout(title_layout)
        
        # Matplotlib figure
        if MATPLOTLIB_AVAILABLE:
            self.attendance_figure = Figure(figsize=(7, 4.5), facecolor='white', dpi=100)
            self.attendance_canvas = FigureCanvas(self.attendance_figure)
            chart_layout.addWidget(self.attendance_canvas)
        else:
            error_label = QLabel(
                "📈 Chart unavailable\n\n"
                "Matplotlib is not installed.\n\n"
                "To install:\n"
                "1. PyCharm: Settings → Python Interpreter → + → matplotlib\n"
                "2. Terminal: pip install matplotlib"
            )
            error_label.setStyleSheet("""
                color: #6b7280; 
                font-size: 12px; 
                padding: 40px 20px; 
                background-color: #f9fafb;
                border-radius: 8px;
                line-height: 1.6;
            """)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_layout.addWidget(error_label)
            self.attendance_figure = None
            self.attendance_canvas = None
        
        return chart_frame
    
    def create_payroll_breakdown_chart(self):
        """Create payroll breakdown pie chart with modern styling"""
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 16px;
                padding: 24px;
                border: 1px solid #e5e7eb;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(12, 12, 12, 12)
        chart_layout.setSpacing(12)
        
        # Title with icon - Clean left alignment
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        
        title_icon = QLabel("💼")
        title_icon.setStyleSheet("font-size: 22px;")
        title_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_icon.setFixedSize(36, 36)
        
        title = QLabel("Payroll Breakdown")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: 600; 
            color: #111827;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title)
        title_layout.addStretch()
        chart_layout.addLayout(title_layout)
        
        # Matplotlib figure
        if MATPLOTLIB_AVAILABLE:
            self.payroll_figure = Figure(figsize=(7, 4.5), facecolor='white', dpi=100)
            self.payroll_canvas = FigureCanvas(self.payroll_figure)
            chart_layout.addWidget(self.payroll_canvas)
        else:
            error_label = QLabel(
                "📊 Chart unavailable\n\n"
                "Matplotlib is not installed.\n\n"
                "To install:\n"
                "1. PyCharm: Settings → Python Interpreter → + → matplotlib\n"
                "2. Terminal: pip install matplotlib"
            )
            error_label.setStyleSheet("""
                color: #6b7280; 
                font-size: 12px; 
                padding: 40px 20px; 
                background-color: #f9fafb;
                border-radius: 8px;
                line-height: 1.6;
            """)
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_layout.addWidget(error_label)
            self.payroll_figure = None
            self.payroll_canvas = None
        
        return chart_frame
    
    def load_dashboard_stats(self):
        """Load and display dashboard statistics"""
        try:
            stats = report_manager.get_dashboard_stats()
            
            # Get additional stats
            emp_change = report_manager.get_employee_count_change()
            payroll_change = report_manager.get_payroll_change()
            pending_count = report_manager.get_pending_approvals()
            
            # Update stat cards with values and subtitles
            active_employees = stats.get('employees', {}).get('active', 0)
            self.emp_card.update_value(active_employees)
            change_text = f"+{emp_change} from last month" if emp_change >= 0 else f"{emp_change} from last month"
            self.emp_card.update_subtitle(change_text)
            
            attendance = stats.get('today_attendance', {})
            present_count = attendance.get('present', 0)
            total_active = attendance.get('total_active', 1)
            attendance_rate = (present_count / total_active * 100) if total_active > 0 else 0
            self.attendance_card.update_value(present_count)
            self.attendance_card.update_subtitle(f"{attendance_rate:.0f}% attendance rate")
            
            monthly = stats.get('monthly_payroll', 0)
            self.payroll_card.update_value(f"₱{monthly:,.0f}")
            payroll_change_text = f"+{payroll_change:.0f}% from last month" if payroll_change >= 0 else f"{payroll_change:.0f}% from last month"
            self.payroll_card.update_subtitle(payroll_change_text)
            
            self.pending_card.update_value(pending_count)
            self.pending_card.update_subtitle("Overtime requests")
            
            # Load new KPI sections
            if hasattr(self, 'recent_payrolls_table'):
                self.load_recent_payrolls()
            
            if hasattr(self, 'top_employees_layout'):
                self.load_top_employees()
            
        except Exception as e:
            print(f"Error loading dashboard stats: {e}")
            import traceback
            traceback.print_exc()
    
    def load_recent_activity(self):
        """Load and display recent activity with sample data"""
        try:
            # Clear existing activities
            if hasattr(self, 'activity_list_layout'):
                for i in reversed(range(self.activity_list_layout.count())):
                    item = self.activity_list_layout.itemAt(i)
                    if item:
                        widget = item.widget()
                        if widget:
                            widget.setParent(None)
                
                # Get recent audit log entries
                from modules.audit_log import audit_logger
                recent_logs = audit_logger.get_recent_logs(limit=7)
                
                # If no logs, create sample activity data
                if not recent_logs:
                    from datetime import datetime, timedelta
                    now = datetime.now()
                    sample_activities = [
                        {'action_type': 'LOGIN', 'action_description': 'Clocked in at 9:00 AM', 'created_at': now - timedelta(minutes=30), 'user_name': self.user_data.get('full_name', 'User')},
                        {'action_type': 'CREATE', 'action_description': 'Submitted timesheet for this week', 'created_at': now - timedelta(hours=2), 'user_name': self.user_data.get('full_name', 'User')},
                        {'action_type': 'UPDATE', 'action_description': 'Updated employee profile information', 'created_at': now - timedelta(hours=5), 'user_name': self.user_data.get('full_name', 'User')},
                        {'action_type': 'APPROVE', 'action_description': 'Approved overtime request', 'created_at': now - timedelta(days=1), 'user_name': self.user_data.get('full_name', 'User')},
                        {'action_type': 'VIEW', 'action_description': 'Viewed payroll report', 'created_at': now - timedelta(days=1, hours=3), 'user_name': self.user_data.get('full_name', 'User')},
                        {'action_type': 'EXPORT', 'action_description': 'Exported attendance report to PDF', 'created_at': now - timedelta(days=2), 'user_name': self.user_data.get('full_name', 'User')},
                        {'action_type': 'UPDATE', 'action_description': 'Updated attendance record', 'created_at': now - timedelta(days=2, hours=5), 'user_name': self.user_data.get('full_name', 'User')},
                    ]
                    recent_logs = sample_activities
                
                # Display recent activities
                for idx, log in enumerate(recent_logs):
                    is_last = (idx == len(recent_logs) - 1)
                    activity_item = self.create_activity_item(log, is_last)
                    self.activity_list_layout.addWidget(activity_item)
                
                self.activity_list_layout.addStretch()
        except Exception as e:
            print(f"Error loading recent activity: {e}")
            if hasattr(self, 'activity_list_layout'):
                error_label = QLabel("Unable to load recent activity")
                error_label.setStyleSheet("color: #757575; font-size: 14px; padding: 20px;")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.activity_list_layout.addWidget(error_label)
    
    def create_activity_item(self, log, is_last=False):
        """Create an activity item widget with timeline design"""
        from datetime import datetime
        
        item_widget = QFrame()
        item_widget.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
        """)
        
        # Main layout with timeline
        main_layout = QHBoxLayout(item_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Timeline indicator container
        timeline_container = QWidget()
        timeline_container.setFixedWidth(24)
        timeline_container.setStyleSheet("background: transparent;")
        timeline_layout = QVBoxLayout(timeline_container)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setSpacing(0)
        timeline_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # Timeline dot (circle)
        dot = QFrame()
        dot.setFixedSize(12, 12)
        dot.setStyleSheet("""
            QFrame {
                background-color: #0055FF;
                border-radius: 6px;
                border: 2px solid white;
            }
        """)
        timeline_layout.addWidget(dot)
        
        # Timeline line (vertical line connecting to next item) - hide for last item
        if not is_last:
            line = QFrame()
            line.setFixedWidth(2)
            line.setMinimumHeight(40)
            line.setStyleSheet("""
                QFrame {
                    background-color: #0055FF;
                    border: none;
                }
            """)
            timeline_layout.addWidget(line)
        
        main_layout.addWidget(timeline_container)
        
        # Content area - Clean modern card
        content_widget = QFrame()
        content_widget.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #E5E7EB;
            }
        """)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 12, 16, 12)
        content_layout.setSpacing(14)
        
        # Icon based on action type
        action_type = log.get('action_type', '')
        icon_map = {
            'LOGIN': '🔐',
            'LOGOUT': '🚪',
            'CREATE': '➕',
            'UPDATE': '✏️',
            'DELETE': '🗑️',
            'VIEW': '👁️',
            'EXPORT': '📤',
            'APPROVE': '✅',
            'REJECT': '❌'
        }
        icon = icon_map.get(action_type, '📋')
        
        # Icon with background - Modern styling
        icon_container = QFrame()
        icon_container.setFixedSize(48, 48)
        icon_container.setStyleSheet("""
            QFrame {
                background-color: #F3F4F6;
                border-radius: 12px;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        # Activity details - Clean left alignment
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        # Description
        description = log.get('action_description', 'No description')
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            color: #111827; 
            font-size: 14px; 
            font-weight: 500;
            line-height: 1.4;
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        # Timestamp and user
        timestamp = log.get('created_at', '')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                # Try parsing other common formats
                try:
                    # Try common datetime formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S']:
                        try:
                            timestamp = datetime.strptime(timestamp, fmt)
                            break
                        except:
                            continue
                except:
                    pass
        if isinstance(timestamp, datetime):
            # Show relative time for recent activities
            now = datetime.now()
            diff = now - timestamp
            if diff.days == 0:
                if diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    time_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                else:
                    hours = diff.seconds // 3600
                    time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.days == 1:
                time_str = "Yesterday"
            elif diff.days < 7:
                time_str = f"{diff.days} days ago"
            else:
                time_str = timestamp.strftime("%b %d, %Y at %I:%M %p")
        else:
            time_str = str(timestamp) if timestamp else "Unknown time"
        
        user_name = log.get('user_name') or log.get('username') or "System"
        meta_text = f"{user_name} • {time_str}"
        
        meta_label = QLabel(meta_text)
        meta_label.setStyleSheet("""
            color: #6B7280; 
            font-size: 12px;
            font-weight: 400;
        """)
        meta_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        details_layout.addWidget(desc_label)
        details_layout.addWidget(meta_label)
        details_layout.addStretch()
        
        content_layout.addWidget(icon_container)
        content_layout.addLayout(details_layout)
        content_layout.addStretch()
        
        main_layout.addWidget(content_widget, 1)
        main_layout.addStretch()
        
        return item_widget
    
    def update_weekly_attendance_chart(self):
        """Update the weekly attendance bar chart showing hours worked per day toward 40-hour goal"""
        if not MATPLOTLIB_AVAILABLE or self.attendance_figure is None:
            return
        
        try:
            weekly_data = report_manager.get_weekly_attendance()
            
            self.attendance_figure.clear()
            ax = self.attendance_figure.add_subplot(111)
            
            days = weekly_data['days']
            hours_worked = weekly_data.get('hours_worked', [0] * len(days))
            
            # Calculate total hours
            total_hours = sum(hours_worked)
            if hasattr(self, 'total_hours_value'):
                self.total_hours_value.setText(f"{total_hours:.1f} / 40")
            
            # Goal line at 8 hours per day
            goal_hours = 8.0
            goal_line = [goal_hours] * len(days)
            
            x = range(len(days))
            width = 0.6
            
            # Create bars with gradient colors based on goal
            colors = ['#10B981' if h >= goal_hours else '#F59E0B' if h > 0 else '#E5E7EB' for h in hours_worked]
            bars = ax.bar(x, hours_worked, width, color=colors, alpha=0.85, edgecolor='white', linewidth=1.5)
            
            # Add goal line
            ax.axhline(y=goal_hours, color='#DC2626', linestyle='--', linewidth=2, alpha=0.6, label='Daily Goal (8h)')
            
            # Add value labels on bars
            for i, (bar, hours) in enumerate(zip(bars, hours_worked)):
                if hours > 0:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                           f'{hours:.1f}h', ha='center', va='bottom', fontsize=9, fontweight='600')
            
            ax.set_xlabel('Day of Week', fontsize=11, fontweight='500')
            ax.set_ylabel('Hours Worked', fontsize=11, fontweight='500')
            ax.set_xticks(x)
            ax.set_xticklabels(days, fontsize=10)
            ax.set_ylim(0, 10)
            ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
            ax.grid(True, alpha=0.2, axis='y', linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)
            
            # Add progress text
            progress_pct = (total_hours / 40.0) * 100 if total_hours > 0 else 0
            ax.text(0.02, 0.98, f'Weekly Progress: {progress_pct:.0f}% ({total_hours:.1f}/40h)',
                   transform=ax.transAxes, fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='#F3F4F6', alpha=0.8, edgecolor='#E5E7EB'))
            
            self.attendance_figure.tight_layout()
            self.attendance_canvas.draw()
            
        except Exception as e:
            print(f"Error updating weekly attendance chart: {e}")
    
    def update_payroll_breakdown_chart(self):
        """Update the payroll breakdown pie chart with salary, bonuses, taxes, deductions"""
        if not MATPLOTLIB_AVAILABLE or self.payroll_figure is None:
            return
        
        try:
            breakdown = report_manager.get_payroll_breakdown()
            
            self.payroll_figure.clear()
            ax = self.payroll_figure.add_subplot(111)
            
            # Updated labels and colors for the new breakdown
            labels = ['Salary', 'Bonuses', 'Taxes', 'Deductions']
            sizes = [
                breakdown.get('salary', 70),
                breakdown.get('bonuses', 15),
                breakdown.get('taxes', 10),
                breakdown.get('deductions', 5)
            ]
            colors = ['#0055FF', '#10B981', '#F59E0B', '#EF4444']
            
            # Create pie chart with modern styling
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                colors=colors, 
                autopct='%1.0f%%',
                startangle=90, 
                textprops={'fontsize': 10, 'fontweight': '600', 'color': 'white'},
                explode=(0.05, 0.05, 0.05, 0.05),  # Slight separation for all segments
                shadow=True,
                wedgeprops={'edgecolor': 'white', 'linewidth': 2.5}
            )
            
            # Update autopct text color and style
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
            
            # Update label text colors for better contrast
            for text in texts:
                text.set_fontsize(11)
                text.set_fontweight('600')
            
            ax.set_title('', fontsize=0)  # Remove default title
            
            # Add modern legend with better formatting
            legend_labels = [f'{label}: {size:.1f}%' for label, size in zip(labels, sizes)]
            ax.legend(
                wedges, 
                legend_labels,
                loc='center', 
                fontsize=10, 
                frameon=True,
                framealpha=0.95,
                edgecolor='#e5e7eb',
                facecolor='white',
                borderpad=1.2,
                labelspacing=1.1
            )
            
            self.payroll_figure.tight_layout()
            self.payroll_canvas.draw()
            
            # Update net pay if available
            if hasattr(self, 'net_pay_value'):
                try:
                    stats = report_manager.get_dashboard_stats()
                    monthly = stats.get('monthly_payroll', 0)
                    # Calculate net pay (total - taxes - deductions)
                    total = monthly
                    taxes_amount = total * (breakdown.get('taxes', 10) / 100)
                    deductions_amount = total * (breakdown.get('deductions', 5) / 100)
                    net_pay = total - taxes_amount - deductions_amount
                    self.net_pay_value.setText(f"₱{net_pay:,.0f}")
                except:
                    pass
            
        except Exception as e:
            print(f"Error updating payroll breakdown chart: {e}")
    
    def navigate_to(self, page_id):
        """Navigate to a specific page"""
        # Check for admin-only pages
        admin_only_pages = ['users', 'audit_log']
        if page_id in admin_only_pages:
            if self.user_data.get('role') != 'Admin':
                QMessageBox.warning(
                    self,
                    "Access Denied",
                    "You do not have permission to access this page.\n\n"
                    "Only Administrators can access this feature."
                )
                return
        
        # Update button states
        for pid, btn in self.nav_buttons.items():
            btn.setChecked(pid == page_id)
        
        # Update page title
        titles = {
            'dashboard': 'Dashboard',
            'employees': 'Employee Management',
            'attendance': 'Attendance Tracking',
            'payroll': 'Payroll Processing',
            'reports': 'Reports & Analytics',
            'users': 'User Management',
            'audit_log': 'Audit Log'
        }
        self.page_title.setText(titles.get(page_id, 'Dashboard'))
        
        # Switch page using dynamic indices
        index = self.page_indices.get(page_id, 0)
        if index < self.pages.count():
            try:
                self.pages.setCurrentIndex(index)
                
                # Refresh page data
                if page_id == 'dashboard':
                    self.load_dashboard_stats()
                elif page_id == 'audit_log' and hasattr(self, 'audit_log_page'):
                    # Refresh audit log when navigating to it
                    try:
                        self.audit_log_page.load_logs()
                    except Exception as e:
                        print(f"Error refreshing audit log: {e}")
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Navigation Error",
                    f"Failed to navigate to {page_id}: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Page Not Found",
                f"The requested page '{page_id}' is not available."
            )
        
        self.current_page = page_id
        self.update_datetime()
    
    def export_dashboard_data(self):
        """Export dashboard data to PDF"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            from datetime import datetime
            
            # Check if ReportLab is available
            try:
                import reportlab
            except ImportError:
                QMessageBox.warning(
                    self,
                    "ReportLab Not Installed",
                    "ReportLab library is required to export PDF files.\n\n"
                    "To install:\n"
                    "1. Open PyCharm Settings → Python Interpreter\n"
                    "2. Click '+' and search for 'reportlab'\n"
                    "3. Install it\n\n"
                    "Or run in terminal:\n"
                    "pip install reportlab"
                )
                return
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Dashboard Data",
                f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if filename:
                # Ensure filename ends with .pdf
                if not filename.lower().endswith('.pdf'):
                    filename += '.pdf'
                
                # Generate dashboard PDF report
                success = report_manager.generate_dashboard_pdf(filename)
                if success:
                    from ui.components import show_toast
                    show_toast(self, f"Dashboard data exported successfully!\n{filename}", "success", duration=5000)
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Dashboard report has been exported to:\n\n{filename}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        "Failed to export dashboard data.\n\n"
                        "Possible reasons:\n"
                        "- ReportLab library issue\n"
                        "- File permission error\n"
                        "- Invalid file path\n\n"
                        "Please check the error console for details."
                    )
        except Exception as e:
            import traceback
            error_msg = f"An error occurred while exporting:\n\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Export Error", error_msg)
    
    def handle_logout(self):
        """Handle logout action"""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
            self.close()
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit SwiftPay?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

