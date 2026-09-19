from datetime import datetime

from .db import get_db


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS afk_users (
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            afk_reason TEXT DEFAULT 'Отошёл',
            afk_since TEXT NOT NULL,
            estimated_return TEXT,
            is_afk INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, guild_id)
        )
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_afk_users_guild ON afk_users(guild_id)
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS afk_cooldown (
            mentioner_id INTEGER NOT NULL,
            afk_user_id INTEGER NOT NULL,
            last_reply TEXT NOT NULL,
            PRIMARY KEY (mentioner_id, afk_user_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS afk_stats (
            user_id INTEGER PRIMARY KEY,
            total_afk_count INTEGER DEFAULT 0,
            total_afk_seconds INTEGER DEFAULT 0,
            longest_afk_seconds INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id INTEGER UNIQUE,
            user_id INTEGER NOT NULL,
            user_name TEXT,
            topic TEXT NOT NULL,
            type TEXT,
            answers TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL,
            closed_at TEXT,
            closed_by INTEGER,
            reason TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            total_applications INTEGER DEFAULT 0,
            accepted INTEGER DEFAULT 0,
            denied INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def save_ticket(channel_id, user_id, user_name, topic, ticket_type, answers, created_at):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO tickets
        (channel_id, user_id, user_name, topic, type, answers, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'open')
    """,
        (channel_id, user_id, user_name, topic, ticket_type, answers, created_at),
    )
    conn.commit()
    conn.close()


def get_ticket(channel_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM tickets WHERE channel_id = ?", (channel_id,))
    row = c.fetchone()
    conn.close()
    return row


def delete_ticket(channel_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM tickets WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()


def update_ticket_status(channel_id, status, closed_by=None, reason=None):
    conn = get_db()
    c = conn.cursor()
    now = datetime.now()

    c.execute(
        """
        UPDATE tickets
        SET status = ?, closed_at = ?, closed_by = ?, reason = ?
        WHERE channel_id = ?
    """,
        (status, now.isoformat(), closed_by, reason, channel_id),
    )

    date = now.strftime("%Y-%m-%d")
    accepted = 1 if status == "accepted" else 0
    denied = 0 if status == "accepted" else 1

    c.execute("SELECT * FROM stats WHERE date = ?", (date,))
    if c.fetchone():
        c.execute(
            """
            UPDATE stats
            SET total_applications = total_applications + 1,
                accepted = accepted + ?,
                denied = denied + ?
            WHERE date = ?
        """,
            (accepted, denied, date),
        )
    else:
        c.execute(
            """
            INSERT INTO stats (date, total_applications, accepted, denied)
            VALUES (?, 1, ?, ?)
        """,
            (date, accepted, denied),
        )

    conn.commit()
    conn.close()


def get_stats():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM tickets")
    total = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM tickets WHERE status = 'accepted'")
    accepted = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM tickets WHERE status = 'denied'")
    denied = c.fetchone()[0] or 0

    c.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
    open_count = c.fetchone()[0] or 0

    c.execute("""
        SELECT date, total_applications, accepted, denied
        FROM stats
        ORDER BY date DESC
        LIMIT 7
    """)
    weekly = c.fetchall()
    conn.close()

    return {
        "total": total,
        "accepted": accepted,
        "denied": denied,
        "open": open_count,
        "weekly": weekly,
    }


def get_all_tickets(limit=50):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        SELECT * FROM tickets
        ORDER BY created_at DESC
        LIMIT ?
    """,
        (limit,),
    )
    rows = c.fetchall()
    conn.close()
    return rows
