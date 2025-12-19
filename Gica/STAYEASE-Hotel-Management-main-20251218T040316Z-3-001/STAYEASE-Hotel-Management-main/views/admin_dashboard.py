from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from models.reservation_model import ReservationModel

class AdminDashboardView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Welcome Message
        welcome = QLabel(f"Welcome back, {self.user.full_name}!")
        welcome.setStyleSheet("font-size: 18px; color: #546e7a; font-weight: 600;")
        layout.addWidget(welcome)

        # KPI Cards Row
        kpi_layout = QHBoxLayout()
        
        self.rev_card = self.create_card("Total Revenue", "₱0")
        kpi_layout.addWidget(self.rev_card)
        
        self.res_card = self.create_card("Today's Bookings", "0")
        kpi_layout.addWidget(self.res_card)
        
        self.occ_card = self.create_card("Occupancy Rate", "0%")
        kpi_layout.addWidget(self.occ_card)
        
        self.avail_card = self.create_card("Available Rooms", "0")
        kpi_layout.addWidget(self.avail_card)

        layout.addLayout(kpi_layout)

        # Recent Activity (Reservations)
        layout.addWidget(QLabel("Recent Reservations"))
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Customer", "Room", "Status", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.refresh_data()

    def create_card(self, title, value):
        card = QFrame()
        card.setObjectName("Card")
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15)) # Lighter shadow for cleaner look
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        title_lbl = QLabel(title)
        title_lbl.setObjectName("CardTitle")
        card_layout.addWidget(title_lbl)
        
        value_lbl = QLabel(value)
        value_lbl.setObjectName("CardValue")
        card_layout.addWidget(value_lbl)
        
        return card

    def refresh_data(self):
        # Fetch stats
        stats = ReservationModel.get_stats()
        
        self.rev_card.findChild(QLabel, "CardValue").setText(f"₱{stats['revenue']:,.2f}")
        self.res_card.findChild(QLabel, "CardValue").setText(str(stats['today_reservations']))
        self.occ_card.findChild(QLabel, "CardValue").setText(f"{stats['occupancy_rate']}%")
        self.avail_card.findChild(QLabel, "CardValue").setText(str(stats['available_rooms']))

        # Update Table
        reservations = ReservationModel.get_all_reservations()
        self.table.setRowCount(len(reservations))
        for i, res in enumerate(reservations):
            self.table.setItem(i, 0, QTableWidgetItem(str(res['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(res['customer_name']))
            self.table.setItem(i, 2, QTableWidgetItem(res['room_number']))
            self.table.setItem(i, 3, QTableWidgetItem(res['status']))
            self.table.setItem(i, 4, QTableWidgetItem(f"₱{res['total_price']}"))
