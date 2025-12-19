"""
SwiftPay Theme Module
Modern glassmorphic design with dark mode support
Inspired by Rippling, Gusto, Deel, and Linear
"""


class Theme:
    """
    Theme configuration for SwiftPay
    Supports light and dark modes with modern glassmorphic design
    """
    
    # Light Mode Colors
    LIGHT = {
        # Brand Colors
        'PRIMARY': '#0055FF',          # Vibrant Blue
        'PRIMARY_LIGHT': '#3373FF',    # Lighter Blue
        'PRIMARY_DARK': '#0033CC',     # Darker Blue
        'ACCENT': '#00D4D4',           # Cyan/Teal Accent
        'ACCENT_LIGHT': '#33DDDD',
        'ACCENT_DARK': '#00B4B4',
        
        # Backgrounds
        'BG_PRIMARY': '#FFFFFF',
        'BG_SECONDARY': '#F8F9FA',
        'BG_CARD': '#FFFFFF',
        'BG_HOVER': '#F5F7FA',
        
        # Text
        'TEXT_PRIMARY': '#1A1A1A',
        'TEXT_SECONDARY': '#6B7280',
        'TEXT_DISABLED': '#9CA3AF',
        
        # Borders & Dividers
        'BORDER': '#E5E7EB',
        'DIVIDER': '#F3F4F6',
        
        # Status Colors
        'SUCCESS': '#10B981',
        'WARNING': '#F59E0B',
        'ERROR': '#EF4444',
        'INFO': '#3B82F6',
        
        # Sidebar
        'SIDEBAR_BG': '#0F172A',
        'SIDEBAR_HOVER': '#1E293B',
        'SIDEBAR_ACTIVE': '#0055FF',
    }
    
    # Dark Mode Colors
    DARK = {
        # Brand Colors (same)
        'PRIMARY': '#0055FF',
        'PRIMARY_LIGHT': '#3373FF',
        'PRIMARY_DARK': '#0033CC',
        'ACCENT': '#00D4D4',
        'ACCENT_LIGHT': '#33DDDD',
        'ACCENT_DARK': '#00B4B4',
        
        # Backgrounds
        'BG_PRIMARY': '#121212',       # Main background
        'BG_SECONDARY': '#0F0F0F',
        'BG_CARD': '#1E1E1E',          # Card background
        'BG_HOVER': '#2A2A2A',
        
        # Text
        'TEXT_PRIMARY': '#FFFFFF',
        'TEXT_SECONDARY': '#A1A1AA',
        'TEXT_DISABLED': '#71717A',
        
        # Borders & Dividers
        'BORDER': '#2A2A2A',
        'DIVIDER': '#1E1E1E',
        
        # Status Colors (adjusted for dark mode)
        'SUCCESS': '#34D399',
        'WARNING': '#FBBF24',
        'ERROR': '#F87171',
        'INFO': '#60A5FA',
        
        # Sidebar
        'SIDEBAR_BG': '#0A0A0A',
        'SIDEBAR_HOVER': '#1A1A1A',
        'SIDEBAR_ACTIVE': '#0055FF',
    }
    
    @staticmethod
    def get_theme(is_dark=False):
        """Get theme colors based on mode"""
        return Theme.DARK if is_dark else Theme.LIGHT
    
    @staticmethod
    def generate_style_sheet(theme_dict, is_dark=False):
        """Generate comprehensive stylesheet from theme"""
        colors = theme_dict
        
        return f"""
        /* Main Application */
        QMainWindow {{
            background-color: {colors['BG_PRIMARY']};
            color: {colors['TEXT_PRIMARY']};
        }}
        
        QWidget {{
            font-family: 'Inter', 'Segoe UI', 'Roboto', -apple-system, sans-serif;
            font-size: 14px;
            color: {colors['TEXT_PRIMARY']};
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['TEXT_PRIMARY']};
        }}
        
        QLabel[class="secondary"] {{
            color: {colors['TEXT_SECONDARY']};
        }}
        
        /* Input Fields */
        QLineEdit {{
            padding: 12px 16px;
            border: 1px solid {colors['BORDER']};
            border-radius: 8px;
            background-color: {colors['BG_CARD']};
            color: {colors['TEXT_PRIMARY']};
            font-size: 14px;
            min-height: 20px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {colors['PRIMARY']};
            background-color: {colors['BG_CARD']};
        }}
        
        QLineEdit:disabled {{
            background-color: {colors['BG_HOVER']};
            color: {colors['TEXT_DISABLED']};
            border-color: {colors['BORDER']};
        }}
        
        /* Buttons */
        QPushButton {{
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            min-height: 24px;
        }}
        
        QPushButton[class="primary"] {{
            background-color: {colors['PRIMARY']};
            color: white;
        }}
        
        QPushButton[class="primary"]:hover {{
            background-color: {colors['PRIMARY_LIGHT']};
        }}
        
        QPushButton[class="primary"]:pressed {{
            background-color: {colors['PRIMARY_DARK']};
        }}
        
        QPushButton[class="outline"] {{
            background-color: transparent;
            color: {colors['PRIMARY']};
            border: 1px solid {colors['PRIMARY']};
        }}
        
        QPushButton[class="outline"]:hover {{
            background-color: {colors['PRIMARY']};
            color: white;
        }}
        
        QPushButton:disabled {{
            background-color: {colors['BG_HOVER']};
            color: {colors['TEXT_DISABLED']};
            border: 1px solid {colors['BORDER']};
        }}
        
        /* Cards */
        QFrame[class="card"] {{
            background-color: {colors['BG_CARD']};
            border: 1px solid {colors['BORDER']};
            border-radius: 12px;
        }}
        
        QFrame[class="glass-card"] {{
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid {colors['BORDER']};
            border-radius: 12px;
        }}
        
        /* Tables */
        QTableWidget {{
            background-color: {colors['BG_CARD']};
            border: 1px solid {colors['BORDER']};
            border-radius: 8px;
            gridline-color: {colors['DIVIDER']};
            color: {colors['TEXT_PRIMARY']};
        }}
        
        QTableWidget::item {{
            padding: 12px;
            border-bottom: 1px solid {colors['DIVIDER']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {colors['PRIMARY']};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {colors['BG_HOVER']};
            color: {colors['TEXT_PRIMARY']};
            padding: 12px;
            border: none;
            border-bottom: 2px solid {colors['BORDER']};
            font-weight: 600;
            font-size: 13px;
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background-color: {colors['BG_SECONDARY']};
            width: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['BORDER']};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['TEXT_SECONDARY']};
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background-color: {colors['BG_SECONDARY']};
            height: 8px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['BORDER']};
            border-radius: 4px;
            min-width: 20px;
        }}
        
        /* ComboBox */
        QComboBox {{
            padding: 12px 16px;
            border: 1px solid {colors['BORDER']};
            border-radius: 8px;
            background-color: {colors['BG_CARD']};
            color: {colors['TEXT_PRIMARY']};
            font-size: 14px;
            min-height: 20px;
        }}
        
        QComboBox:focus {{
            border: 1px solid {colors['PRIMARY']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        /* Group Box */
        QGroupBox {{
            font-weight: 600;
            border: 1px solid {colors['BORDER']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            color: {colors['TEXT_PRIMARY']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            color: {colors['TEXT_PRIMARY']};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 1px solid {colors['BORDER']};
            border-radius: 8px;
            background-color: {colors['BG_CARD']};
        }}
        
        QTabBar::tab {{
            padding: 10px 20px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            background-color: {colors['BG_SECONDARY']};
            color: {colors['TEXT_SECONDARY']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['PRIMARY']};
            color: white;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {colors['BG_HOVER']};
        }}
        
        /* Sidebar */
        QWidget#sidebar {{
            background-color: {colors['SIDEBAR_BG']};
        }}
        
        QPushButton#sidebarBtn {{
            background-color: transparent;
            color: rgba(255, 255, 255, 0.8);
            text-align: left;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            margin: 4px 8px;
        }}
        
        QPushButton#sidebarBtn:hover {{
            background-color: {colors['SIDEBAR_HOVER']};
            color: white;
        }}
        
        QPushButton#sidebarBtn:checked {{
            background-color: {colors['SIDEBAR_ACTIVE']};
            color: white;
        }}
        """


# Global theme manager
class ThemeManager:
    """Manages theme state and switching"""
    
    _instance = None
    _dark_mode = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def is_dark_mode(cls):
        """Check if dark mode is enabled"""
        return cls._dark_mode
    
    @classmethod
    def set_dark_mode(cls, enabled):
        """Enable or disable dark mode"""
        cls._dark_mode = enabled
    
    @classmethod
    def toggle_dark_mode(cls):
        """Toggle dark mode"""
        cls._dark_mode = not cls._dark_mode
        return cls._dark_mode
    
    @classmethod
    def get_theme(cls):
        """Get current theme"""
        return Theme.get_theme(cls._dark_mode)
    
    @classmethod
    def get_stylesheet(cls):
        """Get stylesheet for current theme"""
        theme_dict = cls.get_theme()
        return Theme.generate_style_sheet(theme_dict, cls._dark_mode)

