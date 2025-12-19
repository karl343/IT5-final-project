"""
SwiftPay UI Package
Contains all PyQt6 GUI components
"""

from .styles import Styles
from .login_ui import LoginWindow
from .dashboard_ui import DashboardWindow

__all__ = [
    'Styles',
    'LoginWindow',
    'DashboardWindow'
]

