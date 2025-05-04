from datetime import datetime
from .base_dao import BaseDAO

class ListeningHistoryDAO(BaseDAO):
    def __init__(self):
        """Initialize the ListeningHistory DAO."""
        super().__init__('listening_history')
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        """Create the listening history table if it doesn't exist."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS listening_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    song_id TEXT NOT NULL,
                    song_title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    duration INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

    def get_user_history(self, user_id, limit=10):
        """Get listening history for a specific user."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM listening_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_favorite_artists(self, user_id, limit=5):
        """Get user's favorite artists based on listening history."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                SELECT artist, COUNT(*) as play_count
                FROM listening_history
                WHERE user_id = ?
                GROUP BY artist
                ORDER BY play_count DESC
                LIMIT ?
            ''', (user_id, limit))
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_history_by_mood(self, user_id, mood, limit=10):
        """Get listening history filtered by mood."""
        with self.db.get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM listening_history 
                WHERE user_id = ? AND mood = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, mood, limit))
            rows = cursor.fetchall()
            if rows:
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return [] 