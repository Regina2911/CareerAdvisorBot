import sqlite3


def create_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            age INTEGER,
            interests TEXT,
            work_format TEXT,
            strength TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_user(user_id, age, interests, work_format, strength):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, age, interests, work_format, strength))

    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return user