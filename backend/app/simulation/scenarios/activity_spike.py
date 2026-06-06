"""Inject an activity spike scenario into the synthetic dataset."""

import random
from datetime import datetime, timedelta


def inject_activity_spike(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject a compact activity spike scenario into the synthetic dataset."""
    target = random.choice(accounts)
    receivers = [account for account in accounts if account["account_id"] != target["account_id"]]
    transaction_count = 4
    start_time = datetime.utcnow() - timedelta(minutes=15)

    created_transactions = []
    for idx in range(transaction_count):
        receiver = random.choice(receivers)
        amount = round(random.uniform(20.0, 3000.0), 2)
        timestamp = (start_time + timedelta(seconds=idx * random.randint(5, 10))).isoformat()

        created_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + idx:06d}",
                "sender_account": target["account_id"],
                "receiver_account": receiver["account_id"],
                "amount": amount,
                "timestamp": timestamp,
            }
        )

    return {
        "transactions": created_transactions,
        "ground_truth_entries": [
            {
                "account_id": target["account_id"],
                "scenario_type": "activity_spike",
                "description": f"Injected {transaction_count} additional transactions for account {target['account_id']} in a short time window.",
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + transaction_count,
    }
