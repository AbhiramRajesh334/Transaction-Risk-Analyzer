"""Inject a transaction amount anomaly scenario."""

import random
from datetime import datetime


def inject_amount_anomaly(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject one transaction with an unusually large amount for a single account."""
    target = random.choice(accounts)
    receiver = random.choice([a for a in accounts if a["account_id"] != target["account_id"]])

    amount = 250000.0

    transaction = {
        "transaction_id": f"TX{next_transaction_index:06d}",
        "sender_account": target["account_id"],
        "receiver_account": receiver["account_id"],
        "amount": amount,
        "timestamp": datetime.utcnow().isoformat(),
    }

    return {
        "transactions": [transaction],
        "ground_truth_entries": [
            {
                "account_id": target["account_id"],
                "scenario_type": "amount_anomaly",
                "description": f"Injected a large anomalous transaction of {amount} for account {target['account_id']}.",
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + 1,
    }
