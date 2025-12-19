"""
SwiftPay UI Styles Module
Contains global styles and theme definitions for the application
"""


class Styles:
    """
    Global styles and theme definitions for SwiftPay.
    Uses a modern, clean design with a professional color scheme.
    """
    
    # Color Palette - New Branding
    PRIMARY = "#0055FF"        # Vibrant Blue
    PRIMARY_LIGHT = "#3373FF"  # Lighter Blue
    PRIMARY_DARK = "#0033CC"   # Darker Blue
    ACCENT = "#00D4D4"         # Cyan/Teal Accent
    ACCENT_LIGHT = "#33DDDD"
    ACCENT_DARK = "#00B4B4"
    SECONDARY = "#00D4D4"      # Teal (matches accent)
    SECONDARY_LIGHT = "#33DDDD"
    SECONDARY_DARK = "#00B4B4"
    SUCCESS = "#10B981"        # Modern Green
    WARNING = "#F59E0B"        # Modern Orange
    ERROR = "#EF4444"          # Modern Red
    INFO = "#3B82F6"           # Modern Blue
    
    # Neutral Colors
    WHITE = "#ffffff"
    LIGHT_GRAY = "#f5f5f5"
    GRAY = "#9e9e9e"
    DARK_GRAY = "#424242"
    BLACK = "#212121"
    
    # Background Colors
    BG_PRIMARY = "#f8f9fa"
    BG_SECONDARY = "#ffffff"
    BG_SIDEBAR = "#1a237e"
    
    # Main Application Style
    MAIN_STYLE = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QWidget {
            font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, sans-serif;
            font-size: 14px;
        }
        
        QLabel {
            color: #212121;
        }
        
        QLineEdit {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            font-size: 14px;
            min-height: 20px;
        }
        
        QLineEdit:focus {
            border-color: #0055FF;
        }
        
        QLineEdit:disabled {
            background-color: #f5f5f5;
            color: #9e9e9e;
        }
        
        QPushButton {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            min-height: 20px;
        }
        
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #9e9e9e;
        }
        
        QComboBox {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            font-size: 14px;
            min-height: 20px;
        }
        
        QComboBox:focus {
            border-color: #0055FF;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
        }
        
        QDateEdit {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            font-size: 14px;
            min-height: 20px;
        }
        
        QDateEdit:focus {
            border-color: #0055FF;
        }
        
        QTimeEdit {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            font-size: 14px;
            min-height: 20px;
        }
        
        QSpinBox, QDoubleSpinBox {
            padding: 10px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            font-size: 14px;
            min-height: 20px;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #0055FF;
        }
        
        QTextEdit {
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
            font-size: 14px;
        }
        
        QTextEdit:focus {
            border-color: #0055FF;
        }
        
        QTableWidget {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            gridline-color: #f0f0f0;
        }
        
        QTableWidget::item {
            padding: 10px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        QTableWidget::item:selected {
            background-color: #e8eaf6;
            color: #1a237e;
        }
        
        QHeaderView::section {
            background-color: #1a237e;
            color: white;
            padding: 12px;
            border: none;
            font-weight: bold;
            font-size: 13px;
        }
        
        QScrollBar:vertical {
            border: none;
            background-color: #f5f5f5;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #bdbdbd;
            border-radius: 5px;
            min-height: 30px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #9e9e9e;
        }
        
        QScrollBar:horizontal {
            border: none;
            background-color: #f5f5f5;
            height: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #bdbdbd;
            border-radius: 5px;
            min-width: 30px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            margin-top: 15px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            color: #0055FF;
        }
        
        QTabWidget::pane {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background-color: white;
        }
        
        QTabBar::tab {
            padding: 12px 24px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            background-color: #e0e0e0;
            color: #424242;
        }
        
        QTabBar::tab:selected {
            background-color: #0055FF;
            color: white;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #bdbdbd;
        }
        
        QMessageBox {
            background-color: white;
        }
        
        QMessageBox QLabel {
            font-size: 14px;
        }
        
        QDialog {
            background-color: #f8f9fa;
        }
        
        QProgressBar {
            border: none;
            border-radius: 8px;
            background-color: #e0e0e0;
            height: 10px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            border-radius: 8px;
            background-color: #0055FF;
        }
    """
    
    # Button Styles
    BTN_PRIMARY = """
        QPushButton {
            background-color: #0055FF;
            color: white;
        }
        QPushButton:hover {
            background-color: #3373FF;
        }
        QPushButton:pressed {
            background-color: #0033CC;
        }
    """
    
    BTN_SECONDARY = """
        QPushButton {
            background-color: #00897b;
            color: white;
        }
        QPushButton:hover {
            background-color: #4ebaaa;
        }
        QPushButton:pressed {
            background-color: #005b4f;
        }
    """
    
    BTN_SUCCESS = """
        QPushButton {
            background-color: #2e7d32;
            color: white;
        }
        QPushButton:hover {
            background-color: #4caf50;
        }
        QPushButton:pressed {
            background-color: #1b5e20;
        }
    """
    
    BTN_WARNING = """
        QPushButton {
            background-color: #f57c00;
            color: white;
        }
        QPushButton:hover {
            background-color: #ff9800;
        }
        QPushButton:pressed {
            background-color: #e65100;
        }
    """
    
    BTN_DANGER = """
        QPushButton {
            background-color: #c62828;
            color: white;
        }
        QPushButton:hover {
            background-color: #ef5350;
        }
        QPushButton:pressed {
            background-color: #b71c1c;
        }
    """
    
    BTN_OUTLINE = """
        QPushButton {
            background-color: transparent;
            color: #0055FF;
            border: 1px solid #0055FF;
        }
        QPushButton:hover {
            background-color: #0055FF;
            color: white;
        }
        QPushButton:pressed {
            background-color: #0033CC;
        }
    """
    
    # Sidebar Style - Modern Dark Sidebar
    SIDEBAR_STYLE = """
        QWidget#sidebar {
            background-color: #0F172A;
        }
        
        QPushButton#sidebarBtn {
            background-color: transparent;
            color: rgba(255, 255, 255, 0.8);
            text-align: left;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            margin: 4px 8px;
        }
        
        QPushButton#sidebarBtn:hover {
            background-color: #1E293B;
            color: white;
        }
        
        QPushButton#sidebarBtn:checked {
            background-color: #0055FF;
            color: white;
        }
        
        QLabel#sidebarTitle {
            color: white;
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
        }
        
        QLabel#sidebarSubtitle {
            color: rgba(255, 255, 255, 0.7);
            font-size: 12px;
            padding: 0 20px 20px 20px;
        }
    """
    
    # Card Style
    CARD_STYLE = """
        QFrame#card {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }
        
        QFrame#cardPrimary {
            background-color: #0055FF;
            border-radius: 12px;
            border: none;
        }
        
        QFrame#cardSuccess {
            background-color: #10B981;
            border-radius: 12px;
            border: none;
        }
        
        QFrame#cardWarning {
            background-color: #F59E0B;
            border-radius: 12px;
            border: none;
        }
        
        QFrame#cardInfo {
            background-color: #3B82F6;
            border-radius: 12px;
            border: none;
        }
        
        QGroupBox {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
        }
    """
    
    # Input Style (for form inputs)
    INPUT_STYLE = """
        padding: 10px 15px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        background-color: white;
        font-size: 14px;
        min-height: 20px;
    """
    
    # Table Style
    TABLE_STYLE = """
        QTableWidget {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            gridline-color: #f0f0f0;
        }
        
        QTableWidget::item {
            padding: 10px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        QTableWidget::item:selected {
            background-color: #0055FF;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #F5F7FA;
            color: #1A1A1A;
            padding: 12px;
            border: none;
            border-bottom: 2px solid #E5E7EB;
            font-weight: 600;
            font-size: 13px;
        }
    """
    
    # Login Page Style
    LOGIN_STYLE = """
        QWidget#loginPage {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                stop:0 #1a237e, stop:1 #534bae);
        }
        
        QFrame#loginCard {
            background-color: white;
            border-radius: 20px;
        }
        
        QLabel#loginTitle {
            font-size: 32px;
            font-weight: bold;
            color: #0055FF;
        }
        
        QLabel#loginSubtitle {
            font-size: 14px;
            color: #757575;
        }
    """
    
    # Status Badge Styles
    @staticmethod
    def get_status_style(status):
        """Get style for status badges"""
        status_colors = {
            'Active': '#10B981',
            'Inactive': '#9CA3AF',
            'Present': '#10B981',
            'Absent': '#EF4444',
            'Leave': '#3B82F6',
            'Half-Day': '#F59E0B',
            'Draft': '#9CA3AF',
            'Processed': '#3B82F6',
            'Approved': '#10B981',
            'Paid': '#0055FF',
            'Admin': '#0055FF',
            'Staff': '#00D4D4'
        }
        color = status_colors.get(status, '#9e9e9e')
        return f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }}
        """

