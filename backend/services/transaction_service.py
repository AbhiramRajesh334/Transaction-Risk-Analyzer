"""Transaction persistence operations for the synthetic data layer."""

from database.database import get_db_connection


def insert_transactions(transactions: list[dict]) -> int:
    """Insert a batch of transactions into the SQLite transactions table."""
    conn = get_db_connection()
    with conn:
        conn.executemany(
            "INSERT OR IGNORE INTO transactions (transaction_id, sender_account, receiver_account, amount, timestamp) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    transaction["transaction_id"],
                    transaction["sender_account"],
                    transaction["receiver_account"],
                    transaction["amount"],
                    transaction["timestamp"],
                )
                for transaction in transactions
            ],
        )
    return len(transactions)


def list_transactions() -> list[dict]:
    """Return all transactions from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT transaction_id, sender_account, receiver_account, amount, timestamp FROM transactions ORDER BY timestamp"
    )
    return [dict(row) for row in cursor.fetchall()]


def count_transactions() -> int:
    """Count existing transactions in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(1) AS total FROM transactions")
    return int(cursor.fetchone()["total"])
