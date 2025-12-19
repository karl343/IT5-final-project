from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, QPushButton)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from models.reservation_model import ReservationModel

class CustomerDashboardView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Welcome Banner
        banner = QFrame()
        banner.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0288d1, stop:1 #29b6f6); border-radius: 10px; color: white;")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(30, 30, 30, 30)
        
        welcome_title = QLabel(f"Welcome, {self.user.full_name}!")
        welcome_title.setStyleSheet("font-size: 24px; font-weight: bold; background: transparent;")
        banner_layout.addWidget(welcome_title)
        
        welcome_sub = QLabel("Ready to book your next stay?")
        welcome_sub.setStyleSheet("font-size: 16px; background: transparent;")
        banner_layout.addWidget(welcome_sub)
        
        layout.addWidget(banner)

        # My Bookings Section
        layout.addWidget(QLabel("My Active Bookings"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Room", "Check In", "Check Out", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        layout.addStretch()
        self.setLayout(layout)
        self.refresh_data()

    def refresh_data(self):
        reservations = ReservationModel.get_all_reservations()
        # Filter for this user
        self.my_reservations = [r for r in reservations if r['user_id'] == self.user.id]
        
        self.table.setRowCount(len(self.my_reservations))
        for i, res in enumerate(self.my_reservations):
            self.table.setItem(i, 0, QTableWidgetItem(res['room_number']))
            self.table.setItem(i, 1, QTableWidgetItem(str(res['check_in'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(res['check_out'])))
            self.table.setItem(i, 3, QTableWidgetItem(res['status']))
            
            # Action Button (Request Service)
            if res['status'] in ['Confirmed', 'Checked-in']:
                btn = QPushButton("Request Service")
                btn.clicked.connect(lambda checked, r_id=res['id']: self.request_service(r_id))
                self.table.setCellWidget(i, 4, btn)
    
    def request_service(self, reservation_id):
        dialog = ServiceRequestDialog(reservation_id, self)
        dialog.exec()

from PyQt6.QtWidgets import QDialog, QComboBox, QSpinBox, QFormLayout, QMessageBox
from models.service_model import ServiceModel

class ServiceRequestDialog(QDialog):
    def __init__(self, reservation_id, parent=None):
        super().__init__(parent)
        self.reservation_id = reservation_id
        self.setWindowTitle("Request Room Service")
        self.setFixedSize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        self.service_combo = QComboBox()
        self.services = ServiceModel.get_all_services()
        for s in self.services:
            self.service_combo.addItem(f"{s.name} (₱{s.price})", s.id)
            
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 10)
        
        form.addRow("Service:", self.service_combo)
        form.addRow("Quantity:", self.qty_spin)
        layout.addLayout(form)

        btn = QPushButton("Submit Request")
        btn.clicked.connect(self.submit)
        layout.addWidget(btn)
        self.setLayout(layout)

    def submit(self):
        service_id = self.service_combo.currentData()
        qty = self.qty_spin.value()
        ServiceModel.add_service_to_reservation(self.reservation_id, service_id, qty)
        QMessageBox.information(self, "Success", "Service requested successfully!")
        self.accept()
