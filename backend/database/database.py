"""Database initialization and connection utilities."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "app.db"


def get_db_connection() -> sqlite3.Connection:
    """Return a SQLite connection and ensure the database folder exists."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database() -> None:
    """Create required SQLite tables for synthetic accounts, transactions, and ground truth scenarios."""
    connection = get_db_connection()
    with connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                account_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                sender_account TEXT NOT NULL,
                receiver_account TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (sender_account) REFERENCES accounts(account_id),
                FOREIGN KEY (receiver_account) REFERENCES accounts(account_id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ground_truth_scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                scenario_type TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            )
            """
        )


def insert_ground_truth_entries(entries: list[dict]) -> int:
    """Insert ground truth scenario records into SQLite."""
    connection = get_db_connection()
    with connection:
        connection.executemany(
            "INSERT INTO ground_truth_scenarios (account_id, scenario_type, description, created_at) VALUES (?, ?, ?, ?)",
            [
                (
                    entry["account_id"],
                    entry["scenario_type"],
                    entry["description"],
                    entry["created_at"],
                )
                for entry in entries
            ],
        )
    return len(entries)


def list_ground_truth_entries() -> list[dict]:
    """Return all ground truth scenario records."""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id, account_id, scenario_type, description, created_at FROM ground_truth_scenarios ORDER BY id"
    )
    return [dict(row) for row in cursor.fetchall()]


def clear_demo_data() -> None:
    """Remove all demo accounts, transactions, and ground truth records."""
    connection = get_db_connection()
    with connection:
        connection.execute("DELETE FROM ground_truth_scenarios")
        connection.execute("DELETE FROM transactions")
        connection.execute("DELETE FROM accounts")
