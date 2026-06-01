"""Account persistence operations for the synthetic data layer."""

from database.database import get_db_connection


def insert_accounts(accounts: list[dict]) -> int:
    """Insert a batch of accounts into the SQLite accounts table."""
    conn = get_db_connection()
    with conn:
        conn.executemany(
            "INSERT OR IGNORE INTO accounts (account_id, account_type, created_at) VALUES (?, ?, ?)",
            [(account["account_id"], account["account_type"], account["created_at"]) for account in accounts],
        )
    return len(accounts)


def list_accounts() -> list[dict]:
    """Return all account rows from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_id, account_type, created_at FROM accounts ORDER BY account_id")
    return [dict(row) for row in cursor.fetchall()]


def count_accounts() -> int:
    """Count existing accounts in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(1) AS total FROM accounts")
    return int(cursor.fetchone()["total"])
