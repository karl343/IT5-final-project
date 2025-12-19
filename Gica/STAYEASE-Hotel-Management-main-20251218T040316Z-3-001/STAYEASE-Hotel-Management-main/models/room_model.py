from config.database import db

class RoomModel:
    def __init__(self, id=None, room_number=None, type_id=None, status='Available', image_path=None, type_name=None, price=None):
        self.id = id
        self.room_number = room_number
        self.type_id = type_id
        self.status = status
        self.image_path = image_path
        self.type_name = type_name # Joined field
        self.price = price # Joined field

    @staticmethod
    def get_all_rooms():
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT r.*, rt.name as type_name, rt.base_price as price 
                FROM rooms r 
                LEFT JOIN room_types rt ON r.type_id = rt.id
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return [RoomModel(**row) for row in results]
        except Exception as e:
            print(f"Error fetching rooms: {e}")
            return []

    @staticmethod
    def get_available_rooms():
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT r.*, rt.name as type_name, rt.base_price as price 
                FROM rooms r 
                LEFT JOIN room_types rt ON r.type_id = rt.id
                WHERE r.status = 'Available'
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return [RoomModel(**row) for row in results]
        except Exception as e:
            print(f"Error fetching available rooms: {e}")
            return []

    def save(self):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            if self.id:
                query = "UPDATE rooms SET room_number=%s, type_id=%s, status=%s, image_path=%s WHERE id=%s"
                cursor.execute(query, (self.room_number, self.type_id, self.status, self.image_path, self.id))
            else:
                query = "INSERT INTO rooms (room_number, type_id, status, image_path) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (self.room_number, self.type_id, self.status, self.image_path))
                self.id = cursor.lastrowid
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving room: {e}")
            return False

    def delete(self):
        if self.id:
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM rooms WHERE id = %s", (self.id,))
                conn.commit()
                cursor.close()
                return True
            except Exception as e:
                print(f"Error deleting room: {e}")
                return False
        return False

class RoomTypeModel:
    @staticmethod
    def get_all_types():
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM room_types")
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            print(f"Error fetching room types: {e}")
            return []
