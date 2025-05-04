from .base_dao import BaseDAO
from datetime import datetime

class UserDAO(BaseDAO):
    def __init__(self):
        super().__init__('users')
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Create the users table if it doesn't exist."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP
                )
            ''')

    def get_by_username(self, username):
        """Get a user by username."""
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                # Convert tuple to dictionary using column names
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def get_by_email(self, email):
        """Get a user by email."""
        with self.db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            if row:
                # Convert tuple to dictionary using column names
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def update_last_login(self, user_id):
        """Update the last login timestamp for a user."""
        with self.db.get_cursor() as cursor:
            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.utcnow(), user_id)
            ) 