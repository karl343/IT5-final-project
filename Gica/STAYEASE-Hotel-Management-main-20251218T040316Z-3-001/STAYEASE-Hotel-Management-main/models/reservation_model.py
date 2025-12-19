from    config.database import db

class ReservationModel:
    def __init__(self, id=None, user_id=None, room_id=None, check_in=None, check_out=None, total_price=None, status='Pending', created_at=None):
        self.id = id
        self.user_id = user_id
        self.room_id = room_id
        self.check_in = check_in
        self.check_out = check_out
        self.total_price = total_price
        self.status = status
        self.created_at = created_at

    @staticmethod
    def create_reservation(user_id, room_id, check_in, check_out, total_price):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO reservations (user_id, room_id, check_in, check_out, total_price, status)
                VALUES (%s, %s, %s, %s, %s, 'Pending')
            """
            cursor.execute(query, (user_id, room_id, check_in, check_out, total_price))
            res_id = cursor.lastrowid
            
            # Update room status to Occupied (or Reserved) - simplified logic
            # In a real app, we'd check dates more carefully.
            # For now, let's just log it or handle status in the controller.
            
            conn.commit()
            cursor.close()
            return res_id
        except Exception as e:
            print(f"Error creating reservation: {e}")
            return None

    @staticmethod
    def get_all_reservations():
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT res.*, COALESCE(u.full_name, 'Walk-in Customer') as customer_name, r.room_number 
                FROM reservations res
                LEFT JOIN users u ON res.user_id = u.id
                JOIN rooms r ON res.room_id = r.id
                ORDER BY res.created_at DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error fetching reservations: {e}")
            return []

    @staticmethod
    def get_stats():
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Total Revenue
            cursor.execute("SELECT SUM(total_price) as total_revenue FROM reservations WHERE status != 'Cancelled'")
            revenue = cursor.fetchone()['total_revenue'] or 0
            
            # Total Reservations Today
            cursor.execute("SELECT COUNT(*) as today_count FROM reservations WHERE DATE(created_at) = CURDATE()")
            today_count = cursor.fetchone()['today_count']
            
            # Occupancy Rate (Occupied Rooms / Total Rooms)
            cursor.execute("SELECT COUNT(*) as total FROM rooms")
            total_rooms = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as occupied FROM rooms WHERE status = 'Occupied'")
            occupied_rooms = cursor.fetchone()['occupied']
            
            occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            
            cursor.close()
            return {
                "revenue": revenue,
                "today_reservations": today_count,
                "occupancy_rate": round(occupancy_rate, 1),
                "available_rooms": total_rooms - occupied_rooms
            }
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {
                "revenue": 0,
                "today_reservations": 0,
                "occupancy_rate": 0,
                "available_rooms": 0
            }

    @staticmethod
    def update_status(reservation_id, status):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # If checking out, we might want to calculate final bill including services
            # For now just update status
            query = "UPDATE reservations SET status = %s WHERE id = %s"
            cursor.execute(query, (status, reservation_id))
            
            # If Checked-in, update room status to Occupied
            if status == 'Checked-in':
                cursor.execute("""
                    UPDATE rooms SET status = 'Occupied' 
                    WHERE id = (SELECT room_id FROM reservations WHERE id = %s)
                """, (reservation_id,))
                
            # If Checked-out, update room status to Available (or Dirty/Maintenance)
            if status == 'Checked-out':
                 cursor.execute("""
                    UPDATE rooms SET status = 'Available' 
                    WHERE id = (SELECT room_id FROM reservations WHERE id = %s)
                """, (reservation_id,))
                
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error updating reservation status: {e}")
            return False
