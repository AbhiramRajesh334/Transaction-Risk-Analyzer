"""Inject a counterparty explosion scenario."""

import random
from datetime import datetime, timedelta


def inject_counterparty_explosion(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject a counterparty explosion scenario with a compact set of new connections."""
    target = random.choice(accounts)
    candidates = [a for a in accounts if a["account_id"] != target["account_id"]]
    unique_count = min(len(candidates), 5)
    selected = random.sample(candidates, unique_count)

    base_time = datetime.utcnow() - timedelta(hours=1)
    injected_transactions = []
    for offset, counterparty in enumerate(selected):
        timestamp = (base_time + timedelta(seconds=offset * 30)).isoformat()
        amount = round(random.uniform(10.0, 15000.0), 2)
        injected_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + offset:06d}",
                "sender_account": target["account_id"],
                "receiver_account": counterparty["account_id"],
                "amount": amount,
                "timestamp": timestamp,
            }
        )

    return {
        "transactions": injected_transactions,
        "ground_truth_entries": [
            {
                "account_id": target["account_id"],
                "scenario_type": "counterparty_explosion",
                "description": f"Injected interactions with {unique_count} unique counterparties for account {target['account_id']}.",
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + unique_count,
    }
