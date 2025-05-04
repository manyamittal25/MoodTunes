from .base_dao import BaseDAO

class PlaylistDAO(BaseDAO):
    def __init__(self):
        super().__init__()
        self.table_name = 'playlists'
        self.create_table_if_not_exists()
        self.create_playlist_songs_table()

    def create_table_if_not_exists(self):
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            mood_category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        '''
        self.create_table(create_table_sql)

    def create_playlist_songs_table(self):
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS playlist_songs (
            playlist_id INTEGER NOT NULL,
            song_id TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            position INTEGER,
            PRIMARY KEY (playlist_id, song_id),
            FOREIGN KEY (playlist_id) REFERENCES playlists(id),
            FOREIGN KEY (song_id) REFERENCES songs(song_id)
        )
        '''
        self.create_table(create_table_sql)

    def get_user_playlists(self, user_id):
        """Get all playlists for a specific user."""
        query = f"""
        SELECT * FROM {self.table_name} 
        WHERE user_id = ?
        ORDER BY created_at DESC
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()

    def get_playlist_songs(self, playlist_id):
        """Get all songs in a playlist."""
        query = """
        SELECT s.* FROM songs s
        JOIN playlist_songs ps ON s.song_id = ps.song_id
        WHERE ps.playlist_id = ?
        ORDER BY ps.position
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (playlist_id,))
            return cursor.fetchall()

    def add_song_to_playlist(self, playlist_id, song_id, position=None):
        """Add a song to a playlist."""
        if position is None:
            # Get the current max position
            query = "SELECT MAX(position) FROM playlist_songs WHERE playlist_id = ?"
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (playlist_id,))
                result = cursor.fetchone()
                position = (result[0] or 0) + 1

        query = """
        INSERT INTO playlist_songs (playlist_id, song_id, position)
        VALUES (?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (playlist_id, song_id, position))
            return cursor.lastrowid 