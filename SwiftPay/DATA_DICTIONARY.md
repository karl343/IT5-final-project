# SwiftPay Database Data Dictionary

## Table: `users`

| Column Name | Data Type | Length | Description |
|------------|-----------|--------|-------------|
| `user_id` | INT | - | Unique identifier for each user (Primary Key, Auto Increment) |
| `username` | VARCHAR | 50 | Unique username for login authentication |
| `password_hash` | VARCHAR | 255 | Hashed password using bcrypt encryption |
| `full_name` | VARCHAR | 100 | Full name of the user |
| `role` | ENUM | - | User role: 'Admin' or 'Staff' (Default: 'Staff') |
| `status` | ENUM | - | User account status: 'Active' or 'Inactive' (Default: 'Active') |
| `created_at` | TIMESTAMP | - | Date and time when the user account was created |
| `updated_at` | TIMESTAMP | - | Date and time when the user account was last updated |

---

## Table: `employees`

| Column Name | Data Type | Length | Description |
|------------|-----------|--------|-------------|
| `employee_id` | INT | - | Unique identifier for each employee (Primary Key, Auto Increment) |
| `employee_code` | VARCHAR | 20 | Unique employee code/ID (e.g., EMP001, EMP002) |
| `first_name` | VARCHAR | 50 | Employee's first name |
| `last_name` | VARCHAR | 50 | Employee's last name |
| `email` | VARCHAR | 100 | Employee's email address |
| `phone` | VARCHAR | 20 | Employee's contact phone number |
| `address` | TEXT | - | Employee's complete address |
| `position` | VARCHAR | 100 | Employee's job position/title |
| `department` | VARCHAR | 100 | Department where the employee belongs |
| `rate_per_hour` | DECIMAL | 10,2 | Hourly wage rate (Default: 0.00) |
| `daily_rate` | DECIMAL | 10,2 | Daily wage rate (Default: 0.00) |
| `allowance` | DECIMAL | 10,2 | Monthly allowance amount (Default: 0.00) |
| `sss_deduction` | DECIMAL | 10,2 | SSS (Social Security System) deduction amount (Default: 0.00) |
| `philhealth_deduction` | DECIMAL | 10,2 | PhilHealth deduction amount (Default: 0.00) |
| `pagibig_deduction` | DECIMAL | 10,2 | Pag-IBIG deduction amount (Default: 0.00) |
| `tax_deduction` | DECIMAL | 10,2 | Tax deduction amount (Default: 0.00) |
| `status` | ENUM | - | Employee status: 'Active' or 'Inactive' (Default: 'Active') |
| `date_hired` | DATE | - | Date when the employee was hired |
| `created_at` | TIMESTAMP | - | Date and time when the employee record was created |
| `updated_at` | TIMESTAMP | - | Date and time when the employee record was last updated |

---

## Table: `attendance`

| Column Name | Data Type | Length | Description |
|------------|-----------|--------|-------------|
| `attendance_id` | INT | - | Unique identifier for each attendance record (Primary Key, Auto Increment) |
| `employee_id` | INT | - | Foreign key referencing employees.employee_id |
| `attendance_date` | DATE | - | Date of the attendance record |
| `time_in` | TIME | - | Time when employee clocked in |
| `time_out` | TIME | - | Time when employee clocked out |
| `hours_worked` | DECIMAL | 5,2 | Total hours worked for the day (Default: 0.00) |
| `overtime_hours` | DECIMAL | 5,2 | Overtime hours worked (Default: 0.00) |
| `late_minutes` | INT | - | Minutes late for work (Default: 0) |
| `undertime_minutes` | INT | - | Minutes undertime (Default: 0) |
| `status` | ENUM | - | Attendance status: 'Present', 'Absent', 'Half-Day', or 'Leave' (Default: 'Present') |
| `remarks` | TEXT | - | Additional notes or remarks about the attendance |
| `created_at` | TIMESTAMP | - | Date and time when the attendance record was created |
| `updated_at` | TIMESTAMP | - | Date and time when the attendance record was last updated |

**Constraints:**
- Unique constraint on (employee_id, attendance_date) - one attendance record per employee per day
- Foreign key constraint: employee_id references employees(employee_id) ON DELETE CASCADE

---

## Table: `payroll`

| Column Name | Data Type | Length | Description |
|------------|-----------|--------|-------------|
| `payroll_id` | INT | - | Unique identifier for each payroll period (Primary Key, Auto Increment) |
| `payroll_period` | VARCHAR | 50 | Description of the payroll period (e.g., "January 2024 - First Half") |
| `start_date` | DATE | - | Start date of the payroll period |
| `end_date` | DATE | - | End date of the payroll period |
| `total_employees` | INT | - | Total number of employees in this payroll (Default: 0) |
| `total_gross_pay` | DECIMAL | 15,2 | Total gross pay for all employees (Default: 0.00) |
| `total_deductions` | DECIMAL | 15,2 | Total deductions for all employees (Default: 0.00) |
| `total_net_pay` | DECIMAL | 15,2 | Total net pay for all employees (Default: 0.00) |
| `status` | ENUM | - | Payroll status: 'Draft', 'Processed', 'Approved', or 'Paid' (Default: 'Draft') |
| `processed_by` | INT | - | Foreign key referencing users.user_id (user who processed the payroll) |
| `processed_at` | TIMESTAMP | - | Date and time when the payroll was processed |
| `created_at` | TIMESTAMP | - | Date and time when the payroll record was created |
| `updated_at` | TIMESTAMP | - | Date and time when the payroll record was last updated |

**Constraints:**
- Foreign key constraint: processed_by references users(user_id)

---

## Table: `payroll_details`

| Column Name | Data Type | Length | Description |
|------------|-----------|--------|-------------|
| `detail_id` | INT | - | Unique identifier for each payroll detail record (Primary Key, Auto Increment) |
| `payroll_id` | INT | - | Foreign key referencing payroll.payroll_id |
| `employee_id` | INT | - | Foreign key referencing employees.employee_id |
| `days_worked` | INT | - | Number of days worked in the payroll period (Default: 0) |
| `hours_worked` | DECIMAL | 6,2 | Total hours worked in the payroll period (Default: 0.00) |
| `overtime_hours` | DECIMAL | 6,2 | Total overtime hours worked (Default: 0.00) |
| `late_minutes` | INT | - | Total late minutes in the payroll period (Default: 0) |
| `absences` | INT | - | Number of absences in the payroll period (Default: 0) |
| `basic_pay` | DECIMAL | 12,2 | Basic salary amount (Default: 0.00) |
| `overtime_pay` | DECIMAL | 12,2 | Overtime pay amount (Default: 0.00) |
| `allowance` | DECIMAL | 12,2 | Allowance amount (Default: 0.00) |
| `gross_pay` | DECIMAL | 12,2 | Total gross pay (basic + overtime + allowance) (Default: 0.00) |
| `sss_deduction` | DECIMAL | 10,2 | SSS deduction amount (Default: 0.00) |
| `philhealth_deduction` | DECIMAL | 10,2 | PhilHealth deduction amount (Default: 0.00) |
| `pagibig_deduction` | DECIMAL | 10,2 | Pag-IBIG deduction amount (Default: 0.00) |
| `tax_deduction` | DECIMAL | 10,2 | Tax deduction amount (Default: 0.00) |
| `late_deduction` | DECIMAL | 10,2 | Deduction for late arrivals (Default: 0.00) |
| `absence_deduction` | DECIMAL | 10,2 | Deduction for absences (Default: 0.00) |
| `other_deductions` | DECIMAL | 10,2 | Other miscellaneous deductions (Default: 0.00) |
| `total_deductions` | DECIMAL | 12,2 | Sum of all deductions (Default: 0.00) |
| `net_pay` | DECIMAL | 12,2 | Net pay after all deductions (gross_pay - total_deductions) (Default: 0.00) |
| `created_at` | TIMESTAMP | - | Date and time when the payroll detail record was created |
| `updated_at` | TIMESTAMP | - | Date and time when the payroll detail record was last updated |

**Constraints:**
- Unique constraint on (payroll_id, employee_id) - one payroll detail per employee per payroll period
- Foreign key constraint: payroll_id references payroll(payroll_id) ON DELETE CASCADE
- Foreign key constraint: employee_id references employees(employee_id) ON DELETE CASCADE

---

## Table: `audit_log`

| Column Name | Data Type | Length | Description |
|------------|-----------|--------|-------------|
| `log_id` | INT | - | Unique identifier for each audit log entry (Primary Key, Auto Increment) |
| `user_id` | INT | - | Foreign key referencing users.user_id (ID of the user who performed the action) |
| `action_type` | VARCHAR | 50 | Type of action performed (e.g., Login, Logout, Create, Update, Delete) |
| `entity_type` | VARCHAR | 50 | Type of entity affected (e.g., Employee, Payroll, Attendance, User) |
| `entity_id` | INT | - | ID of the specific entity record that was affected |
| `action_description` | TEXT | - | Detailed description of the action performed |
| `old_values` | TEXT | - | Previous values before the change (stored as JSON/string) |
| `new_values` | TEXT | - | New or changed values after the action (stored as JSON/string) |
| `ip_address` | VARCHAR | 45 | IP address from which the action was performed |
| `user_agent` | TEXT | - | User agent/browser information |
| `created_at` | TIMESTAMP | - | Date and time when the action was logged |

**Constraints:**
- Foreign key constraint: user_id references users(user_id) ON DELETE SET NULL
- Index on user_id for faster queries
- Index on action_type for filtering by action type
- Index on entity_type for filtering by entity type
- Index on created_at for date range queries

---

## Database Views

### View: `vw_attendance_summary`
Provides a summary view of employee attendance records with employee information.

**Columns:** employee_id, employee_code, employee_name, position, department, attendance_date, time_in, time_out, hours_worked, overtime_hours, late_minutes, status

### View: `vw_payroll_summary`
Provides a summary view of payroll records with employee and payroll period information.

**Columns:** payroll_id, payroll_period, start_date, end_date, employee_id, employee_code, employee_name, position, days_worked, hours_worked, basic_pay, overtime_pay, allowance, gross_pay, total_deductions, net_pay, payroll_status

---

## Notes

- All monetary amounts are stored in DECIMAL format to ensure precision
- All timestamps use MySQL TIMESTAMP type with automatic default values
- Foreign key relationships ensure referential integrity
- Unique constraints prevent duplicate records where applicable
- ENUM types restrict values to predefined options
- TEXT fields are used for variable-length text data that may exceed VARCHAR limits

