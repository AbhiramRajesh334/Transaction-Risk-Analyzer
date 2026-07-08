"""Inject a fan-out cash-out scenario: one origin disperses funds to many new, previously unconnected accounts."""

import random
from datetime import datetime, timedelta


def inject_fan_out_cash_out(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Simulate a smurfing-style fan-out where one account rapidly disperses to a wide set of unrelated accounts.

    A single account sending many moderate-sized transfers to counterparties it
    has never interacted with before is a strong structuring + counterparty-explosion signal.
    """
    # Prefer Business or Salaried as the origin (they have plausible large balances).
    candidates = [a for a in accounts if a["account_type"] in {"Business", "Salaried"}]
    if not candidates:
        candidates = accounts[:]

    origin = random.choice(candidates)

    # Identify accounts with NO prior transactions involving the origin.
    existing_counterparties: set[str] = set()
    for tx in transactions:
        if tx["sender_account"] == origin["account_id"]:
            existing_counterparties.add(tx["receiver_account"])
        if tx["receiver_account"] == origin["account_id"]:
            existing_counterparties.add(tx["sender_account"])

    fresh_targets = [
        a for a in accounts
        if a["account_id"] != origin["account_id"] and a["account_id"] not in existing_counterparties
    ]
    if len(fresh_targets) < 4:
        # Fall back to any account if not enough fresh ones.
        fresh_targets = [a for a in accounts if a["account_id"] != origin["account_id"]]

    # Send to up to 7 distinct recipients in rapid succession.
    num_targets = min(7, len(fresh_targets))
    targets = random.sample(fresh_targets, num_targets)
    start_time = datetime.utcnow() - timedelta(hours=1)

    created_transactions = []
    for idx, receiver in enumerate(targets):
        # Amounts just below common thresholds but larger than normal peer transfers.
        amount = round(random.uniform(4500.0, 9500.0), 2)
        timestamp = (start_time + timedelta(minutes=idx * 7)).isoformat()
        created_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + idx:06d}",
                "sender_account": origin["account_id"],
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
                "account_id": origin["account_id"],
                "scenario_type": "counterparty_explosion",
                "description": (
                    f"Fan-out cash-out: {origin['account_id']} distributed {total:,.2f} across "
                    f"{num_targets} previously unconnected accounts within 1 hour."
                ),
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + len(created_transactions),
    }
