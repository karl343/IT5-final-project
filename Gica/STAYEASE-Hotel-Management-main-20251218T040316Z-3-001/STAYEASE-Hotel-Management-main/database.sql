CREATE DATABASE IF NOT EXISTS hotel_db;
USE hotel_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Receptionist', 'Customer') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Room Types Table
CREATE TABLE IF NOT EXISTS room_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    description TEXT
);

-- Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE NOT NULL,
    type_id INT,
    status ENUM('Available', 'Occupied', 'Maintenance') DEFAULT 'Available',
    image_path VARCHAR(255),
    FOREIGN KEY (type_id) REFERENCES room_types(id) ON DELETE SET NULL
);

-- Reservations Table
CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    room_id INT,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status ENUM('Pending', 'Confirmed', 'Checked-in', 'Checked-out', 'Cancelled') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    method VARCHAR(50),
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
);

-- Logs Table
CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Sample Data
INSERT INTO room_types (name, base_price, description) VALUES 
('Standard', 100.00, 'Basic room with essential amenities'),
('Deluxe', 180.00, 'Spacious room with city view'),
('Suite', 350.00, 'Luxury suite with king bed and jacuzzi');

INSERT INTO rooms (room_number, type_id, status) VALUES 
('101', 1, 'Available'),
('102', 1, 'Available'),
('201', 2, 'Available'),
('202', 2, 'Maintenance'),
('301', 3, 'Available');

-- Default Admin (Password: admin123) - In a real app, hash this!
INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES 
('admin', 'admin123', 'Admin', 'System Administrator', 'admin@hotel.com', '1234567890');

INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES 
('reception', 'reception123', 'Receptionist', 'Front Desk', 'reception@hotel.com', '0987654321');
