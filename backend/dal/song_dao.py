from .base_dao import BaseDAO

class SongDAO(BaseDAO):
    def __init__(self):
        super().__init__()
        self.table_name = 'songs'
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT,
            genre TEXT,
            duration INTEGER,
            mood_category TEXT,
            spotify_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        self.create_table(create_table_sql)

    def get_songs_by_mood(self, mood):
        """Get songs categorized by a specific mood."""
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE mood_category = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (mood,))
            return cursor.fetchall()

    def get_songs_by_artist(self, artist):
        """Get all songs by a specific artist."""
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE artist = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (artist,))
            return cursor.fetchall()

    def get_songs_by_genre(self, genre):
        """Get all songs of a specific genre."""
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE genre = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (genre,))
            return cursor.fetchall() 