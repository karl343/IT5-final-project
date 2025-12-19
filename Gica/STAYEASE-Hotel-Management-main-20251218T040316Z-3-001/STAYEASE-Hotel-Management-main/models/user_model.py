from config.database import db

class UserModel:
    def __init__(self, id=None, username=None, password_hash=None, role=None, full_name=None, email=None, phone=None, created_at=None, **kwargs):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.created_at = created_at

    @staticmethod
    def login(username, password):
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()
            if user:
                return UserModel(**user)
            return None
        except Exception as e:
            print(f"Error during login: {e}")
            return None

    @staticmethod
    def get_all_users():
        try:
            conn = db.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            cursor.close()
            return [UserModel(**row) for row in results]
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    def save(self):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            if self.id:
                query = "UPDATE users SET username=%s, role=%s, full_name=%s, email=%s, phone=%s WHERE id=%s"
                cursor.execute(query, (self.username, self.role, self.full_name, self.email, self.phone, self.id))
            else:
                query = "INSERT INTO users (username, password_hash, role, full_name, email, phone) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (self.username, self.password_hash, self.role, self.full_name, self.email, self.phone))
                self.id = cursor.lastrowid
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False

    def delete(self):
        if self.id:
            try:
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = %s", (self.id,))
                conn.commit()
                cursor.close()
                return True
            except Exception as e:
                print(f"Error deleting user: {e}")
                return False
        return False
