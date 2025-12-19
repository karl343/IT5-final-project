import random
from datetime import datetime, timedelta
import mysql.connector
from config.database import db

def seed_data():
    conn = db.get_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    cursor = conn.cursor()
    print("Seeding database...")

    # 1. Create Sample Customers
    customers = [
        ('john_doe', 'User123!', 'Customer', 'John Doe', 'john@example.com', '1234567890'),
        ('jane_smith', 'User123!', 'Customer', 'Jane Smith', 'jane@example.com', '0987654321'),
        ('alice_w', 'User123!', 'Customer', 'Alice Wonderland', 'alice@example.com', '1122334455'),
        ('bob_builder', 'User123!', 'Customer', 'Bob Builder', 'bob@example.com', '5566778899'),
        ('charlie_brown', 'User123!', 'Customer', 'Charlie Brown', 'charlie@example.com', '9988776655')
    ]

    customer_ids = []
    for cust in customers:
        try:
            # Check if exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (cust[0],))
            res = cursor.fetchone()
            if res:
                customer_ids.append(res[0])
            else:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, full_name, email, phone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, cust)
                customer_ids.append(cursor.lastrowid)
                print(f"Created customer: {cust[0]}")
        except mysql.connector.Error as err:
            print(f"Error creating customer {cust[0]}: {err}")

    conn.commit()

    # 2. Get Rooms
    cursor.execute("SELECT id, room_number FROM rooms")
    rooms = cursor.fetchall()
    room_ids = [r[0] for r in rooms]

    if not room_ids or not customer_ids:
        print("Not enough rooms or customers to seed reservations.")
        return

    # 3. Create Reservations (Past and Future)
    statuses = ['Confirmed', 'Checked-in', 'Checked-out', 'Cancelled', 'Pending']
    
    # Clear existing reservations if needed? No, let's append.
    
    print("Generating 50 sample reservations...")
    for _ in range(50):
        user_id = random.choice(customer_ids)
        room_id = random.choice(room_ids)
        
        # Random date in last 60 days
        days_offset = random.randint(-60, 5) 
        check_in = datetime.now() + timedelta(days=days_offset)
        duration = random.randint(1, 5)
        check_out = check_in + timedelta(days=duration)
        
        total_price = random.randint(100, 500) * duration
        status = random.choice(statuses)

        # Ensure future dates aren't 'Checked-out'
        if check_in > datetime.now() and status == 'Checked-out':
            status = 'Confirmed'
        
        try:
            cursor.execute("""
                INSERT INTO reservations (user_id, room_id, check_in, check_out, total_price, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, room_id, check_in.date(), check_out.date(), total_price, status, check_in))
        except mysql.connector.Error as err:
            print(f"Error creating reservation: {err}")

    conn.commit()
    print("Seeding complete! Reports should now show data.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    seed_data()
