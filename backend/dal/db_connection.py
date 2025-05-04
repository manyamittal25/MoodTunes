import sqlite3
import contextlib
from typing import Generator, Any

class DatabaseConnection:
    def __init__(self, db_config):
        """Initialize the database connection with configuration."""
        self.db_config = db_config

    @contextlib.contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with context management."""
        conn = sqlite3.connect(**self.db_config)
        try:
            yield conn
        finally:
            conn.close()

    @contextlib.contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Get a database cursor with context management."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close() 