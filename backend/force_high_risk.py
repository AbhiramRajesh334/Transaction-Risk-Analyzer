import os
import sqlite3
import sys

sys.path.insert(0, os.getcwd())
from services.risk_scoring_service import get_risk_for_account

db_path = os.path.join(os.getcwd(), "data", "app.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
accounts = ['ACC01','ACC02','ACC03','ACC05','ACC06','ACC07','ACC08','ACC09','ACC10','ACC11','ACC12']
placeholders = ','.join('?' for _ in accounts)
query = f"UPDATE transactions SET amount = 25000000.0, timestamp = '2026-07-07T10:00:00.000000' WHERE sender_account IN ({placeholders}) OR receiver_account IN ({placeholders})"
cur.execute(query, accounts + accounts)
conn.commit()
print('updated rows', cur.rowcount)
conn.close()
print(get_risk_for_account('ACC02'))
print(get_risk_for_account('ACC06'))
print(get_risk_for_account('ACC08'))
