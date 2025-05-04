from datetime import datetime
from .base_dao import BaseDAO

class MoodHistoryDAO(BaseDAO):
    def __init__(self):
        """Initialize the MoodHistory DAO."""
        super().__init__('mood_history')
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Create the mood history table if it doesn't exist."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mood_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    mood TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    song_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

    def get_user_mood_history(self, user_id, limit=10):
        """Get mood history for a specific user."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM mood_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_mood_stats(self, user_id):
        """Get mood statistics for a user."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                SELECT mood, COUNT(*) as count
                FROM mood_history
                WHERE user_id = ?
                GROUP BY mood
            ''', (user_id,))
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return [] 