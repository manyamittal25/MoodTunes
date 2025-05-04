from .db_connection import DatabaseConnection
from .db_config import DB_CONFIG

class BaseDAO:
    def __init__(self, table_name):
        """Initialize the DAO with a table name."""
        self.table_name = table_name
        self.db = DatabaseConnection(DB_CONFIG)

    def create_table(self, create_table_sql):
        """Create a table using the provided SQL."""
        with self.db.get_cursor() as cursor:
            cursor.execute(create_table_sql)

    def create_table_if_not_exists(self):
        """Create the table if it doesn't exist. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement create_table_if_not_exists")

    def insert(self, data):
        """Insert a record into the table."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, list(data.values()))
            return cursor.lastrowid

    def get_by_id(self, id):
        """Get a record by ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            if row:
                # Convert tuple to dictionary using column names
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    def get_all(self):
        """Get all records from the table."""
        query = f"SELECT * FROM {self.table_name}"
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                # Convert tuples to dictionaries using column names
                columns = [description[0] for description in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def update(self, id, data):
        """Update a record in the table."""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        
        with self.db.get_cursor() as cursor:
            values = list(data.values())
            values.append(id)
            cursor.execute(query, values)
            return cursor.rowcount

    def delete(self, id):
        """Delete a record from the table."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (id,))
            return cursor.rowcount 