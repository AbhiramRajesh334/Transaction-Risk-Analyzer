"""Inject a structuring scenario: many transfers just below a reporting threshold."""

import random
from datetime import datetime, timedelta

STRUCTURING_THRESHOLD = 10000.0


def inject_structuring(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject repeated sub-threshold transfers to avoid a single large-reporting event."""
    target = random.choice([account for account in accounts if account["account_type"] != "Student"] or accounts)
    receivers = [account["account_id"] for account in accounts if account["account_id"] != target["account_id"]]
    transaction_count = 5
    start_time = datetime.utcnow() - timedelta(hours=2)

    created_transactions = []
    for idx in range(transaction_count):
        amount = round(random.uniform(8800.0, STRUCTURING_THRESHOLD - 50), 2)
        created_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + idx:06d}",
                "sender_account": target["account_id"],
                "receiver_account": receivers[idx % len(receivers)],
                "amount": amount,
                "timestamp": (start_time + timedelta(minutes=idx * 8)).isoformat(),
            }
        )

    total_amount = sum(tx["amount"] for tx in created_transactions)
    return {
        "transactions": created_transactions,
        "ground_truth_entries": [
            {
                "account_id": target["account_id"],
                "scenario_type": "structuring",
                "description": (
                    f"Structuring pattern: {transaction_count} transfers totaling {total_amount:,.2f}, "
                    f"each below the {STRUCTURING_THRESHOLD:,.0f} reporting threshold."
                ),
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + transaction_count,
    }
