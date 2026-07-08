"""Inject a ghost account reactivation scenario: a dormant account suddenly resurfaces with high-value activity."""

import random
from datetime import datetime, timedelta


def inject_ghost_account_reactivation(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Pick an existing account with minimal transaction history and flood it with sudden high-value activity.

    A dormant or low-activity account suddenly sending several large transfers in a
    short window is a classic indicator of account takeover or ghost account use.
    """
    # Prefer Student accounts — they normally have low amounts — to make the spike dramatic.
    candidates = [a for a in accounts if a["account_type"] == "Student"]
    if not candidates:
        candidates = accounts[:]

    # Count existing transaction involvement per account.
    tx_count: dict[str, int] = {}
    for tx in transactions:
        tx_count[tx["sender_account"]] = tx_count.get(tx["sender_account"], 0) + 1
        tx_count[tx["receiver_account"]] = tx_count.get(tx["receiver_account"], 0) + 1

    # Pick the quietest account.
    target = min(candidates, key=lambda a: tx_count.get(a["account_id"], 0))
    receivers = [a for a in accounts if a["account_id"] != target["account_id"]]

    # Simulate a burst of high-value transactions compressed into < 30 minutes.
    transaction_count = 6
    start_time = datetime.utcnow() - timedelta(minutes=25)
    created_transactions = []

    for idx in range(transaction_count):
        receiver = random.choice(receivers)
        # Amounts far above what a student account would normally process.
        amount = round(random.uniform(12000.0, 48000.0), 2)
        timestamp = (start_time + timedelta(minutes=idx * 4)).isoformat()
        created_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + idx:06d}",
                "sender_account": target["account_id"],
                "receiver_account": receiver["account_id"],
                "amount": amount,
                "timestamp": timestamp,
            }
        )

    total = sum(tx["amount"] for tx in created_transactions)
    return {
        "transactions": created_transactions,
        "ground_truth_entries": [
            {
                "account_id": target["account_id"],
                "scenario_type": "activity_spike",
                "description": (
                    f"Ghost account reactivation: {target['account_id']} sent {transaction_count} transfers "
                    f"totalling {total:,.2f} within 25 minutes after prolonged inactivity."
                ),
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + transaction_count,
    }
