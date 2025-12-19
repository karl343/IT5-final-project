from models.user_model import UserModel

class AuthController:
    def __init__(self):
        self.current_user = None

    def login(self, username, password):
        user = UserModel.login(username, password)
        if user:
            self.current_user = user
            return True, "Login successful"
        return False, "Invalid username or password"

    def logout(self):
        self.current_user = None

    def register(self, username, password, full_name, email, phone):
        # Check if user exists
        # In a real app, we'd handle exceptions here
        try:
            new_user = UserModel(
                username=username,
                password_hash=password, # Hash this in production!
                role='Customer',
                full_name=full_name,
                email=email,
                phone=phone
            )
            new_user.save()
            return True, "Registration successful"
        except Exception as e:
            return False, str(e)

    def get_current_user(self):
        return self.current_user
