"""Inject a round-tripping scenario: funds leave and return through intermediaries."""

import random
from datetime import datetime, timedelta


def inject_round_tripping(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject A -> B -> A round-trip pattern with a large outbound and returning transfer."""
    candidates = [account for account in accounts if account["account_type"] in {"Business", "Salaried"}]
    if len(candidates) < 2:
        candidates = accounts[:2]
    origin, intermediary = random.sample(candidates, 2)

    amount_out = round(random.uniform(45000.0, 65000.0), 2)
    amount_back = round(amount_out * random.uniform(0.88, 0.96), 2)
    start_time = datetime.utcnow() - timedelta(hours=3)

    created_transactions = [
        {
            "transaction_id": f"TX{next_transaction_index:06d}",
            "sender_account": origin["account_id"],
            "receiver_account": intermediary["account_id"],
            "amount": amount_out,
            "timestamp": start_time.isoformat(),
        },
        {
            "transaction_id": f"TX{next_transaction_index + 1:06d}",
            "sender_account": intermediary["account_id"],
            "receiver_account": origin["account_id"],
            "amount": amount_back,
            "timestamp": (start_time + timedelta(minutes=45)).isoformat(),
        },
    ]

    return {
        "transactions": created_transactions,
        "ground_truth_entries": [
            {
                "account_id": origin["account_id"],
                "scenario_type": "round_tripping",
                "description": (
                    f"Round-trip flow: {origin['account_id']} sent {amount_out:,.2f} to "
                    f"{intermediary['account_id']} and received {amount_back:,.2f} back within 45 minutes."
                ),
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + 2,
    }
