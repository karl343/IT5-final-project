import sys
from PyQt6.QtWidgets import QApplication
from views.login_view import LoginWindow
from views.main_window import MainWindow

import os

def main():
    app = QApplication(sys.argv)
    
    # Get absolute path to assets
    base_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_dir, "assets", "style.qss")
    
    # Load Stylesheet
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Stylesheet not found at {style_path}")

    # Start Application Loop
    while True:
        login_window = LoginWindow()
        if login_window.exec(): # If login successful (returns Accepted)
            user = login_window.get_user()
            main_window = MainWindow(user)
            main_window.show()
            app.exec() # Run the main window loop
            
            # Check if we should restart (logout) or exit
            if not main_window.logging_out:
                break # Exit loop if closed normally
        else:
            break # Exit loop if login cancelled

if __name__ == "__main__":
    main()
