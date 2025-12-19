-- SwiftPay Database Schema
-- MySQL Database for Payroll Management System

CREATE DATABASE IF NOT EXISTS swiftpay_db;
USE swiftpay_db;

-- =====================================================
-- TABLE: users (for login authentication)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('Admin', 'Staff') NOT NULL DEFAULT 'Staff',
    status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: employees
-- =====================================================
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    position VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    rate_per_hour DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    daily_rate DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    allowance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    sss_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    philhealth_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    pagibig_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tax_deduction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    date_hired DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =====================================================
-- TABLE: attendance
-- =====================================================
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    time_in TIME,
    time_out TIME,
    hours_worked DECIMAL(5, 2) DEFAULT 0.00,
    overtime_hours DECIMAL(5, 2) DEFAULT 0.00,
    late_minutes INT DEFAULT 0,
    undertime_minutes INT DEFAULT 0,
    status ENUM('Present', 'Absent', 'Half-Day', 'Leave') NOT NULL DEFAULT 'Present',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE KEY unique_attendance (employee_id, attendance_date)
);

-- =====================================================
-- TABLE: payroll (payroll period header)
-- =====================================================
CREATE TABLE IF NOT EXISTS payroll (
    payroll_id INT AUTO_INCREMENT PRIMARY KEY,
    payroll_period VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_employees INT DEFAULT 0,
    total_gross_pay DECIMAL(15, 2) DEFAULT 0.00,
    total_deductions DECIMAL(15, 2) DEFAULT 0.00,
    total_net_pay DECIMAL(15, 2) DEFAULT 0.00,
    status ENUM('Draft', 'Processed', 'Approved', 'Paid') NOT NULL DEFAULT 'Draft',
    processed_by INT,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (processed_by) REFERENCES users(user_id)
);

-- =====================================================
-- TABLE: payroll_details (individual employee payroll)
-- =====================================================
CREATE TABLE IF NOT EXISTS payroll_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    payroll_id INT NOT NULL,
    employee_id INT NOT NULL,
    days_worked INT DEFAULT 0,
    hours_worked DECIMAL(6, 2) DEFAULT 0.00,
    overtime_hours DECIMAL(6, 2) DEFAULT 0.00,
    late_minutes INT DEFAULT 0,
    absences INT DEFAULT 0,
    basic_pay DECIMAL(12, 2) DEFAULT 0.00,
    overtime_pay DECIMAL(12, 2) DEFAULT 0.00,
    allowance DECIMAL(12, 2) DEFAULT 0.00,
    gross_pay DECIMAL(12, 2) DEFAULT 0.00,
    sss_deduction DECIMAL(10, 2) DEFAULT 0.00,
    philhealth_deduction DECIMAL(10, 2) DEFAULT 0.00,
    pagibig_deduction DECIMAL(10, 2) DEFAULT 0.00,
    tax_deduction DECIMAL(10, 2) DEFAULT 0.00,
    late_deduction DECIMAL(10, 2) DEFAULT 0.00,
    absence_deduction DECIMAL(10, 2) DEFAULT 0.00,
    other_deductions DECIMAL(10, 2) DEFAULT 0.00,
    total_deductions DECIMAL(12, 2) DEFAULT 0.00,
    net_pay DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (payroll_id) REFERENCES payroll(payroll_id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE KEY unique_payroll_employee (payroll_id, employee_id)
);

-- =====================================================
-- SAMPLE DATA: Default Admin User
-- Password: admin123 (hashed with bcrypt)
-- =====================================================
INSERT INTO users (username, password_hash, full_name, role, status)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.g9hH3L5zL5zL5z', 'System Administrator', 'Admin', 'Active')
ON DUPLICATE KEY UPDATE username = username;

-- =====================================================
-- SAMPLE DATA: Sample Employees
-- =====================================================
INSERT INTO employees (employee_code, first_name, last_name, email, phone, position, department, rate_per_hour, daily_rate, allowance, sss_deduction, philhealth_deduction, pagibig_deduction, status, date_hired)
VALUES 
('EMP001', 'Juan', 'Dela Cruz', 'juan.delacruz@email.com', '09171234567', 'Software Developer', 'IT Department', 125.00, 1000.00, 1500.00, 500.00, 200.00, 100.00, 'Active', '2023-01-15'),
('EMP002', 'Maria', 'Santos', 'maria.santos@email.com', '09181234567', 'HR Manager', 'Human Resources', 150.00, 1200.00, 2000.00, 600.00, 250.00, 100.00, 'Active', '2022-06-01'),
('EMP003', 'Pedro', 'Reyes', 'pedro.reyes@email.com', '09191234567', 'Accountant', 'Finance', 135.00, 1080.00, 1800.00, 550.00, 225.00, 100.00, 'Active', '2023-03-20')
ON DUPLICATE KEY UPDATE employee_code = employee_code;

-- =====================================================
-- VIEWS: Useful reports
-- =====================================================

-- View for employee attendance summary
CREATE OR REPLACE VIEW vw_attendance_summary AS
SELECT 
    e.employee_id,
    e.employee_code,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    e.position,
    e.department,
    a.attendance_date,
    a.time_in,
    a.time_out,
    a.hours_worked,
    a.overtime_hours,
    a.late_minutes,
    a.status
FROM employees e
LEFT JOIN attendance a ON e.employee_id = a.employee_id
WHERE e.status = 'Active';

-- View for payroll summary
CREATE OR REPLACE VIEW vw_payroll_summary AS
SELECT 
    p.payroll_id,
    p.payroll_period,
    p.start_date,
    p.end_date,
    pd.employee_id,
    e.employee_code,
    CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
    e.position,
    pd.days_worked,
    pd.hours_worked,
    pd.basic_pay,
    pd.overtime_pay,
    pd.allowance,
    pd.gross_pay,
    pd.total_deductions,
    pd.net_pay,
    p.status AS payroll_status
FROM payroll p
JOIN payroll_details pd ON p.payroll_id = pd.payroll_id
JOIN employees e ON pd.employee_id = e.employee_id;

-- =====================================================
-- TABLE: audit_log (for tracking system activities)
-- =====================================================
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    action_description TEXT,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action_type (action_type),
    INDEX idx_entity_type (entity_type),
    INDEX idx_created_at (created_at)
);

