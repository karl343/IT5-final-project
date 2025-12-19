from config.database import db

def update_db():
    conn = db.get_connection()
    if not conn:
        print("Failed to connect to DB")
        return

    cursor = conn.cursor()
    
    # Services Table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                description TEXT
            )
        """)
        print("Created services table")
    except Exception as e:
        print(f"Error creating services table: {e}")

    # Reservation Services Table
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservation_services (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reservation_id INT,
                service_id INT,
                quantity INT DEFAULT 1,
                status ENUM('Requested', 'Approved', 'Completed', 'Declined') DEFAULT 'Requested',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE,
                FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
            )
        """)
        print("Created reservation_services table")
    except Exception as e:
        print(f"Error creating reservation_services table: {e}")

    # Seed Services
    try:
        # Check if empty
        cursor.execute("SELECT COUNT(*) FROM services")
        if cursor.fetchone()[0] == 0:
            services = [
                ('Extra Towels', 5.00, 'Set of 2 fresh towels'),
                ('Extra Pillow', 5.00, 'Soft feather pillow'),
                ('Room Cleaning', 20.00, 'Full room cleaning service'),
                ('Breakfast', 15.00, 'Continental breakfast delivered to room'),
                ('Dinner', 25.00, 'Gourmet dinner set'),
                ('Bottled Water', 2.00, '1L Mineral Water')
            ]
            cursor.executemany("INSERT INTO services (name, price, description) VALUES (%s, %s, %s)", services)
            print("Seeded services data")
            conn.commit()
    except Exception as e:
        print(f"Error seeding services: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_db()
