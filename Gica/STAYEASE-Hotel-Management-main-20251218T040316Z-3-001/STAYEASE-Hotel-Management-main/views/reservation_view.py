import sys
import os

# Add project root to path if running directly
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QHeaderView, QDialog, QFormLayout, QDateEdit, QComboBox, QMessageBox, QMenu, QRadioButton, QButtonGroup, QLineEdit, QApplication)
from PyQt6.QtCore import Qt, QDate
from datetime import datetime
from models.reservation_model import ReservationModel
from models.room_model import RoomModel
from models.user_model import UserModel

class ReservationView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Top Bar
        top_layout = QHBoxLayout()
        title = QLabel("Reservations")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        top_layout.addStretch()
        
        # Only show New Booking for Receptionist (or Customer if self-booking is allowed)
        # User requested to remove it for Admin
        if self.user.role != 'Admin':
            new_booking_btn = QPushButton("+ New Booking")
            new_booking_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            new_booking_btn.clicked.connect(self.new_booking)
            top_layout.addWidget(new_booking_btn)

        layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Customer", "Room", "Check In", "Check Out", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False) # Cleaner look with just row borders
        self.table.verticalHeader().setVisible(False) # Hide vertical row numbers
        
        # Enable context menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_data()

    def refresh_data(self):
        self.reservations = ReservationModel.get_all_reservations()
        # Filter for customer if needed
        if self.user.role == 'Customer':
            self.reservations = [r for r in self.reservations if r['user_id'] == self.user.id]

        self.table.setRowCount(len(self.reservations))
        for i, res in enumerate(self.reservations):
            self.table.setItem(i, 0, QTableWidgetItem(str(res['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(res['customer_name']))
            self.table.setItem(i, 2, QTableWidgetItem(res['room_number']))
            self.table.setItem(i, 3, QTableWidgetItem(str(res['check_in'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(res['check_out'])))
            
            status_item = QTableWidgetItem(res['status'])
            # Color coding for status
            if res['status'] == 'Confirmed':
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif res['status'] == 'Pending':
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif res['status'] == 'Cancelled':
                status_item.setForeground(Qt.GlobalColor.red)
                
            self.table.setItem(i, 5, status_item)

    def show_context_menu(self, position):
        if self.user.role not in ['Admin', 'Receptionist']:
            return

        indexes = self.table.selectedIndexes()
        if not indexes:
            return
            
        row = indexes[0].row()
        reservation = self.reservations[row]
        res_id = reservation['id']
        current_status = reservation['status']
        
        menu = QMenu()
        
        # Actions
        accept_action = menu.addAction("Accept Booking")
        checkin_action = menu.addAction("Check In")
        checkout_action = menu.addAction("Check Out")
        menu.addSeparator()
        cancel_action = menu.addAction("Cancel Booking")
        
        # Enable/Disable based on status logic
        if current_status == 'Pending':
            checkin_action.setEnabled(False)
            checkout_action.setEnabled(False)
        elif current_status == 'Confirmed':
            accept_action.setEnabled(False)
            checkout_action.setEnabled(False)
        elif current_status == 'Checked-in':
            accept_action.setEnabled(False)
            checkin_action.setEnabled(False)
            cancel_action.setEnabled(False)
        elif current_status in ['Cancelled', 'Checked-out']:
            accept_action.setEnabled(False)
            checkin_action.setEnabled(False)
            checkout_action.setEnabled(False)
            cancel_action.setEnabled(False)

        action = menu.exec(self.table.viewport().mapToGlobal(position))
        
        if action == accept_action:
            self.update_status(res_id, "Confirmed")
        elif action == checkin_action:
            self.update_status(res_id, "Checked-in")
        elif action == checkout_action:
            self.update_status(res_id, "Checked-out")
        elif action == cancel_action:
            # Confirm cancellation
            confirm = QMessageBox.question(self, "Confirm Cancellation", 
                                         "Are you sure you want to cancel this booking?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.update_status(res_id, "Cancelled")

    def update_status(self, res_id, new_status):
        try:
            ReservationModel.update_status(res_id, new_status)
            QMessageBox.information(self, "Success", f"Reservation updated to {new_status}")
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")

    def new_booking(self):
        dialog = BookingDialog(self.user, parent=self)
        if dialog.exec():
            self.refresh_data()

class BookingDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("New Reservation")
        self.setFixedSize(450, 500)
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

        # Walk-in Toggle
        self.walkin_group = QButtonGroup(self)
        self.radio_registered = QRadioButton("Registered Customer")
        self.radio_walkin = QRadioButton("Walk-in Guest")
        self.radio_registered.setChecked(True)
        
        self.walkin_group.addButton(self.radio_registered)
        self.walkin_group.addButton(self.radio_walkin)
        
        self.radio_registered.toggled.connect(self.toggle_customer_input)
        self.radio_walkin.toggled.connect(self.toggle_customer_input)

        if self.user.role == 'Receptionist':
             role_layout = QHBoxLayout()
             role_layout.addWidget(self.radio_registered)
             role_layout.addWidget(self.radio_walkin)
             form.addRow("Customer Type:", role_layout)

        # If Admin/Receptionist, select user
        self.user_combo = QComboBox()
        if self.user.role in ['Admin', 'Receptionist']:
            users = UserModel.get_all_users()
            for u in users:
                if u.role == 'Customer':
                    self.user_combo.addItem(u.username, u.id)
            form.addRow("Select Customer:", self.user_combo)
            
        # Walk-in Name Input
        self.walkin_name = QLineEdit()
        self.walkin_name.setPlaceholderText("Enter Guest Name")
        if self.user.role == 'Receptionist':
             form.addRow("Guest Name:", self.walkin_name)
             
        self.toggle_customer_input() # Set initial state
        
        # Room Selection
        self.room_combo = QComboBox()
        rooms = RoomModel.get_available_rooms()
        for r in rooms:
            self.room_combo.addItem(f"{r.room_number} ({r.type_name} - ₱{r.price})", r)
        
        self.check_in = QDateEdit()
        self.check_in.setDate(QDate.currentDate())
        self.check_in.setCalendarPopup(True)
        
        self.check_out = QDateEdit()
        self.check_out.setDate(QDate.currentDate().addDays(1))
        self.check_out.setCalendarPopup(True)

        form.addRow("Room:", self.room_combo)
        form.addRow("Check In:", self.check_in)
        form.addRow("Check Out:", self.check_out)

        layout.addLayout(form)
        
        self.price_label = QLabel("Total Price: ₱0.00")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.price_label)
        
        # Recalculate price on change
        self.room_combo.currentIndexChanged.connect(self.update_price)
        self.check_in.dateChanged.connect(self.update_price)
        self.check_out.dateChanged.connect(self.update_price)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Confirm Booking")
        save_btn.clicked.connect(self.save)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.update_price()

    def toggle_customer_input(self):
        is_walkin = self.radio_walkin.isChecked()
        self.user_combo.setVisible(not is_walkin)
        self.walkin_name.setVisible(is_walkin)
        
        # Hide label for combo if walkin, hide label for walkin if combo ? 
        # FormLayout manages widgets but labels are separate. 
        # Simple fix: just hide the widgets. The labels might stay but that's okay for now or we can use a StackedLayout if needed.
        # Actually QFormLayout.addRow returns nothing to reference the label easily without iterating.
        # Let's just rely on widget visibility.


    def update_price(self):
        room = self.room_combo.currentData()
        if not room: return
        
        days = self.check_in.date().daysTo(self.check_out.date())
        if days < 1: days = 1
        
        total = float(room.price) * days
        self.price_label.setText(f"Total Price: ₱{total:.2f}")
        self.current_total = total

    def save(self):
        # Get values
        check_in = self.check_in.date().toPyDate()
        check_out = self.check_out.date().toPyDate()
        
        # Validation
        if check_out <= check_in:
            QMessageBox.warning(self, "Invalid Dates", "Check-out date must be after check-in date.")
            return
        
        # Calculate days
        days = (check_out - check_in).days
        if days <= 0:
            QMessageBox.warning(self, "Invalid Dates", "Reservation must be at least 1 day.")
            return
        
        # Get room and user
        room_data = self.room_combo.currentData()
        if not room_data:
            QMessageBox.warning(self, "Invalid Selection", "Please select a room.")
            return
        room_id = room_data.id
        
        # Handle walk-in vs registered customer
        if self.user.role == 'Receptionist' and self.radio_walkin.isChecked():
            # Walk-in customer
            guest_name = self.walkin_name.text().strip()
            if not guest_name:
                QMessageBox.warning(self, "Invalid Input", "Please enter the guest name.")
                return
            
            # Create a new user for walk-in
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            new_user = UserModel(
                username=f"walkin_{timestamp}",
                password_hash="walkin",  # Placeholder password
                role="Customer",
                full_name=guest_name
            )
            try:
                new_user.save()
                user_id = new_user.id
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create walk-in customer profile: {str(e)}")
                return
        else:
            # Registered customer (or current user if not Admin/Receptionist)
            if self.user.role in ['Admin', 'Receptionist']:
                user_id = self.user_combo.currentData()
        ReservationModel.create_reservation(user_id, room_data.id, check_in, check_out, self.current_total)
        QMessageBox.information(self, "Success", f"Reservation created successfully!\nTotal: ₱{self.current_total:,.2f}")
        self.accept()

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

    # Mock ReservationView class for standalone testing of BookingDialog
    class MockReservationView(QWidget):
        def __init__(self, user):
            super().__init__()
            self.user = user
            self.setWindowTitle("Reservation Management (Mock)")
            self.setGeometry(100, 100, 800, 600)
            layout = QVBoxLayout()
            
            # Simple button to open BookingDialog
            btn = QPushButton("Open Booking Dialog", self)
            btn.clicked.connect(self.new_booking)
            layout.addWidget(btn)
            self.setLayout(layout)

        def new_booking(self):
            dialog = BookingDialog(self.user, parent=self)
            if dialog.exec():
                print("Booking dialog closed successfully.")
            else:
                print("Booking dialog cancelled.")

        def refresh_data(self):
            print("Refreshing data (mock)")
            
    try:
        window = MockReservationView(MockUser())
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error running view: {e}")
