import sqlite3


def find_user(conn: sqlite3.Connection, name: str) -> tuple | None:
    """Look up a user by name."""
    query = f"SELECT id, name, email FROM users WHERE name = '{name}'"
    return conn.execute(query).fetchone()
