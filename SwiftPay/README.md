# 💰 SwiftPay - Payroll Management System

A comprehensive payroll management solution built with Python, PyQt6, and MySQL. SwiftPay provides a modern, user-friendly interface for managing employees, tracking attendance, computing payroll, and generating reports.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [Default Credentials](#-default-credentials)
- [Project Structure](#-project-structure)
- [Module Overview](#-module-overview)
- [Payroll Formulas](#-payroll-formulas)
- [Screenshots](#-screenshots)
- [Future Enhancements](#-future-enhancements)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### 🔐 User Authentication
- Secure login with bcrypt password hashing
- Role-based access control (Admin, Staff)
- User management (Admin only)

### 👥 Employee Management
- Complete CRUD operations
- Employee search and filtering
- Track personal info, position, compensation, and deductions
- Active/Inactive status management

### 📅 Attendance Tracking
- Real-time time clock interface
- Time-in / Time-out recording
- Automatic calculation of:
  - Hours worked
  - Overtime hours
  - Late minutes
  - Undertime
- Attendance records by date range

### 💰 Payroll Processing
- Automatic payroll computation
- Support for:
  - Basic pay calculation
  - Overtime pay (1.25x rate)
  - Government deductions (SSS, PhilHealth, Pag-IBIG)
  - Tax deductions
  - Late and absence deductions
- Payslip generation (view and export)
- Payroll period management

### 📊 Reports & Analytics
- Attendance reports
- Payroll summary reports
- Employee list reports
- Export to CSV
- Export to PDF (requires ReportLab)

---

## 💻 System Requirements

- **Python**: 3.8 or higher
- **MySQL**: 8.0 or higher
- **Operating System**: Windows, macOS, or Linux

---

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
cd SwiftPay
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages:
- **PyQt6** (≥6.4.0) - GUI framework
- **mysql-connector-python** (≥8.0.0) - MySQL database connector
- **bcrypt** (≥4.0.0) - Password hashing
- **reportlab** (≥4.0.0) - PDF generation (optional)

---

## 🗄️ Database Setup

### Step 1: Start MySQL Server

Ensure your MySQL server is running.

### Step 2: Configure Database Connection

Edit `database/db.py` and update the configuration:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD_HERE',  # Update this
    'database': 'swiftpay_db',
    'autocommit': False,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

### Step 3: Initialize Database

**Option A: Automatic (Recommended)**

The application will automatically create the database and tables on first run.

**Option B: Manual**

```bash
mysql -u root -p < database/schema.sql
```

---

## ▶️ Running the Application

```bash
python main.py
```

Or on some systems:

```bash
python3 main.py
```

---

## 🔑 Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |

⚠️ **Important**: Change the default password after first login!

---

## 📁 Project Structure

```
SwiftPay/
│
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── database/
│   ├── __init__.py
│   ├── db.py              # Database connection & operations
│   └── schema.sql         # MySQL database schema
│
├── modules/
│   ├── __init__.py
│   ├── users.py           # User authentication & management
│   ├── employees.py       # Employee CRUD operations
│   ├── attendance.py      # Attendance tracking
│   ├── payroll.py         # Payroll computation
│   └── reports.py         # Report generation
│
├── ui/
│   ├── __init__.py
│   ├── styles.py          # UI themes & styles
│   ├── login_ui.py        # Login window
│   ├── dashboard_ui.py    # Main dashboard
│   ├── employees_ui.py    # Employee management UI
│   ├── attendance_ui.py   # Attendance tracking UI
│   ├── payroll_ui.py      # Payroll processing UI
│   ├── reports_ui.py      # Reports & analytics UI
│   └── users_ui.py        # User management UI (Admin)
│
└── assets/
    └── icons/             # Application icons
```

---

## 📦 Module Overview

### Database Module (`database/db.py`)
- Singleton database connection
- Query execution helpers
- Context manager for transactions
- Schema initialization

### Users Module (`modules/users.py`)
- bcrypt password hashing
- Login/logout functionality
- User CRUD operations
- Role-based access

### Employees Module (`modules/employees.py`)
- Employee code generation
- Complete CRUD operations
- Search and filter
- Data validation

### Attendance Module (`modules/attendance.py`)
- Time-in/Time-out recording
- Automatic calculations
- Attendance summaries
- Bulk operations

### Payroll Module (`modules/payroll.py`)
- Payroll computation engine
- Payroll period management
- Payslip generation
- Payroll history

### Reports Module (`modules/reports.py`)
- Report data generation
- CSV export
- PDF export (with ReportLab)
- Dashboard statistics

---

## 🧮 Payroll Formulas

### Basic Pay
```
Basic Pay = Total Hours Worked × Rate Per Hour
```

### Overtime Pay
```
OT Pay = Overtime Hours × (Rate Per Hour × 1.25)
```

### Late Deduction
```
Late Deduction = Late Minutes × (Rate Per Hour ÷ 60)
```

### Absence Deduction
```
Absence Deduction = Daily Rate × Number of Absences
```

### Gross Pay
```
Gross Pay = Basic Pay + OT Pay + Allowances
```

### Total Deductions
```
Total Deductions = SSS + PhilHealth + Pag-IBIG + Tax + Late Deduction + Absence Deduction
```

### Net Pay
```
Net Pay = Gross Pay - Total Deductions
```

---

## 🖼️ Screenshots

The application features a modern, clean interface with:

1. **Login Screen** - Secure authentication with branding
2. **Dashboard** - Overview with statistics and quick actions
3. **Employee Management** - Table view with CRUD operations
4. **Attendance Tracking** - Time clock and records
5. **Payroll Processing** - Generation and payslip viewing
6. **Reports** - Tabbed interface with export options

---

## 🚀 Future Enhancements

- [ ] Leave management system
- [ ] Employee self-service portal
- [ ] Biometric integration
- [ ] Email notifications
- [ ] Multi-branch support
- [ ] Backup and restore
- [ ] Audit logging
- [ ] Mobile companion app
- [ ] API for third-party integration
- [ ] Advanced analytics dashboard

---

## ❓ Troubleshooting

### "Database connection failed"
1. Ensure MySQL is running
2. Check credentials in `database/db.py`
3. Verify the database exists or can be created

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### PyQt6 display issues on Linux
```bash
sudo apt-get install libxcb-xinerama0
```

### PDF export not working
```bash
pip install reportlab
```

### Password reset for admin
Run in MySQL:
```sql
USE swiftpay_db;
UPDATE users SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.g9hH3L5zL5zL5z' WHERE username = 'admin';
```
Then login with password: `admin123`

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📞 Support

For support and questions, please open an issue on the project repository.

---

**SwiftPay** - Simplifying Payroll Management 💼

