import sys
import os

# Add project root to path if running directly
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QPushButton, 
                             QHeaderView, QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from models.room_model import RoomModel, RoomTypeModel

class RoomView(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Top Bar
        top_layout = QHBoxLayout()
        title = QLabel("Room Management")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title)
        
        top_layout.addStretch()
        
        if self.user.role == 'Admin':
            add_btn = QPushButton("+ Add Room")
            add_btn.clicked.connect(self.add_room)
            top_layout.addWidget(add_btn)

        layout.addLayout(top_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Room Number", "Type", "Price", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)
        
        # Actions
        if self.user.role == 'Admin':
            action_layout = QHBoxLayout()
            edit_btn = QPushButton("Edit Selected")
            edit_btn.clicked.connect(self.edit_room)
            delete_btn = QPushButton("Delete Selected")
            delete_btn.setObjectName("DangerButton")
            delete_btn.clicked.connect(self.delete_room)
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            layout.addLayout(action_layout)

        self.setLayout(layout)
        self.refresh_data()

    def refresh_data(self):
        self.rooms = RoomModel.get_all_rooms()
        self.table.setRowCount(len(self.rooms))
        for i, room in enumerate(self.rooms):
            self.table.setItem(i, 0, QTableWidgetItem(str(room.id)))
            self.table.setItem(i, 1, QTableWidgetItem(room.room_number))
            self.table.setItem(i, 2, QTableWidgetItem(room.type_name))
            self.table.setItem(i, 3, QTableWidgetItem(f"₱{room.price}"))
            self.table.setItem(i, 4, QTableWidgetItem(room.status))

    def add_room(self):
        dialog = RoomDialog(parent=self)
        if dialog.exec():
            self.refresh_data()

    def edit_room(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        room = self.rooms[selected]
        dialog = RoomDialog(room, self)
        if dialog.exec():
            self.refresh_data()

    def delete_room(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        room = self.rooms[selected]
        confirm = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this room?")
        if confirm == QMessageBox.StandardButton.Yes:
            room.delete()
            self.refresh_data()

class RoomDialog(QDialog):
    def __init__(self, room=None, parent=None):
        super().__init__(parent)
        self.room = room
        self.setWindowTitle("Add Room" if not room else "Edit Room")
        self.setFixedSize(300, 250)
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

        self.number_input = QLineEdit()
        self.type_combo = QComboBox()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Available", "Occupied", "Maintenance"])

        # Load types
        types = RoomTypeModel.get_all_types()
        for t in types:
            self.type_combo.addItem(t['name'], t['id'])

        if self.room:
            self.number_input.setText(self.room.room_number)
            self.status_combo.setCurrentText(self.room.status)
            index = self.type_combo.findData(self.room.type_id)
            if index >= 0: self.type_combo.setCurrentIndex(index)

        form.addRow("Room Number:", self.number_input)
        form.addRow("Type:", self.type_combo)
        form.addRow("Status:", self.status_combo)

        layout.addLayout(form)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save(self):
        room_number = self.number_input.text().strip()
        type_id = self.type_combo.currentData()
        status = self.status_combo.currentText()

        # Validation
        if not room_number:
            QMessageBox.warning(self, "Invalid Input", "Please enter a room number.")
            return
        
        if not type_id:
            QMessageBox.warning(self, "Invalid Selection", "Please select a room type.")
            return

        if self.room:
            self.room.room_number = room_number
            self.room.type_id = type_id
            self.room.status = status
            if self.room.save():
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update room. Please try again.")
        else:
            new_room = RoomModel(room_number=room_number, type_id=type_id, status=status)
            if new_room.save():
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to create room. Please try again.")

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
            
    try:
        window = RoomView(MockUser())
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error running view: {e}")
