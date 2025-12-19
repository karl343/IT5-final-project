from config.database import db

class ServiceModel:
    def __init__(self, id=None, name=None, price=None, description=None):
        self.id = id
        self.name = name
        self.price = price
        self.description = description

    @staticmethod
    def get_all_services():
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM services")
        results = cursor.fetchall()
        cursor.close()
        return [ServiceModel(**row) for row in results]

    @staticmethod
    def add_service_to_reservation(reservation_id, service_id, quantity=1):
        conn = db.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO reservation_services (reservation_id, service_id, quantity, status)
            VALUES (%s, %s, %s, 'Requested')
        """
        cursor.execute(query, (reservation_id, service_id, quantity))
        conn.commit()
        cursor.close()

    @staticmethod
    def get_services_for_reservation(reservation_id):
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT rs.*, s.name, s.price 
            FROM reservation_services rs
            JOIN services s ON rs.service_id = s.id
            WHERE rs.reservation_id = %s
        """
        cursor.execute(query, (reservation_id,))
        results = cursor.fetchall()
        cursor.close()
        return results

    @staticmethod
    def update_service_status(service_entry_id, status):
        conn = db.get_connection()
        cursor = conn.cursor()
        query = "UPDATE reservation_services SET status = %s WHERE id = %s"
        cursor.execute(query, (status, service_entry_id))
        conn.commit()
        cursor.close()
