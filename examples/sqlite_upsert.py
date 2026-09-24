import sqlite3


def record_login(db_path: str, user_id: int, ts: float) -> int:
    """Upsert the user's last login time and return their total login count."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO logins (user_id, last_seen, count) VALUES (?, ?, 1) "
            "ON CONFLICT(user_id) DO UPDATE SET last_seen = ?, count = count + 1",
            (user_id, ts, ts),
        )
        (count,) = conn.execute(
            "SELECT count FROM logins WHERE user_id = ?", (user_id,)
        ).fetchone()
    return count
