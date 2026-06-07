"""Inject a circular fund-flow scenario: A -> B -> C -> A."""

import random
from datetime import datetime, timedelta


def inject_circular_flow(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject a three-hop cycle that returns funds to the origin account."""
    if len(accounts) < 3:
        raise ValueError("At least three accounts are required for circular flow injection.")

    cycle_accounts = random.sample(accounts, 3)
    amount = round(random.uniform(18000.0, 35000.0), 2)
    start_time = datetime.utcnow() - timedelta(hours=5)

    hops = [
        (cycle_accounts[0]["account_id"], cycle_accounts[1]["account_id"]),
        (cycle_accounts[1]["account_id"], cycle_accounts[2]["account_id"]),
        (cycle_accounts[2]["account_id"], cycle_accounts[0]["account_id"]),
    ]

    created_transactions = []
    for idx, (sender, receiver) in enumerate(hops):
        created_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + idx:06d}",
                "sender_account": sender,
                "receiver_account": receiver,
                "amount": round(amount * (0.97 ** idx), 2),
                "timestamp": (start_time + timedelta(minutes=idx * 20)).isoformat(),
            }
        )

    cycle_path = " -> ".join(account["account_id"] for account in cycle_accounts) + f" -> {cycle_accounts[0]['account_id']}"
    return {
        "transactions": created_transactions,
        "ground_truth_entries": [
            {
                "account_id": cycle_accounts[0]["account_id"],
                "scenario_type": "circular_flow",
                "description": f"Circular flow detected along path {cycle_path}.",
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + len(created_transactions),
    }
