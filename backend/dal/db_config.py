import os

# Database configuration
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'db.sqlite3')

# Database connection settings
DB_CONFIG = {
    'database': DB_PATH,
    'check_same_thread': False  # Required for SQLite in multi-threaded environments
} 