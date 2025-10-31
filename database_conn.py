import sqlite3
import sys
import os

def _validate_file_type(path: str):
    """Validate that path ends in .db and is an absolute file path"""

    if not path.endswith('.db'):
        raise ValueError(f"Invalid file type. Expected .db file, got: {path}")

    if not os.path.isabs(path):
        raise ValueError(f"Path must be absolute, got relative path: {path}")

def establish_connection(path: str):
    try:
        _validate_file_type(sys.argv[1])
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn
    except ValueError as e:
        print(f"Validation error: {e}")
    except FileNotFoundError as e:
        print(f"File error: {e}")

    sys.exit(1)

def get_table_names(conn) -> list:
    """Returns list of tuples: [(table_name, row_count), ...]"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    # Get name and count for each table
    table_info = []
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        table_info.append((table_name, count))

    return table_info

def get_table_data(conn, table_name: str) -> tuple:
    """Returns columns and rows for a specific table

    Returns:
        tuple: (column_names, rows) where column_names is a list of strings
               and rows is a list of tuples
    """
    cursor = conn.cursor()

    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]

    # Get all rows
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    return columns, rows


def get_database_schema(conn):
    """Get full schema of all tables"""
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema_text = "Database Schema:\n\n"
    for table_name, create_sql in tables:
        schema_text += f"{create_sql}\n\n"

    return schema_text

