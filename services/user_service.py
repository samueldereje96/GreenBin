# services/user_service.py
import json
import os
from models.user import User

class UserService:
    def __init__(self, file_path="data/users.json"):
        self.file_path = file_path
        self.users = []
        self.load_users()

    def load_users(self):
        """Load users from JSON file into memory"""
        if not os.path.exists(self.file_path):
            return
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.users = [User(
                    u["id"],
                    u["name"],
                    u["email"],
                    u["phone"]
                ) for u in data]
        except json.JSONDecodeError:
            pass  # Empty or corrupted file

    def get_all_users(self):
        """Return list of all users"""
        return self.users

    def get_user_by_id(self, user_id):
        """Return user by ID"""
        for u in self.users:
            if u.id == user_id:
                return u
        return None
