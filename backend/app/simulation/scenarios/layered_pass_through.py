"""Inject a layered pass-through chain: A -> B -> C -> D, each forwarding most of the amount onward."""

import random
from datetime import datetime, timedelta


def inject_layered_pass_through(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Create a multi-hop layering chain where funds pass through 3 intermediate accounts.

    Unlike a simple round-trip, this mimics classic money laundering layering:
    funds enter one account and cascade through intermediaries before reaching
    a final destination, with each hop taking a small cut.
    """
    if len(accounts) < 4:
        raise ValueError("At least four accounts are required for layered pass-through injection.")

    # Choose 4 distinct accounts for the chain.
    chain = random.sample(accounts, 4)
    initial_amount = round(random.uniform(30000.0, 70000.0), 2)
    start_time = datetime.utcnow() - timedelta(hours=8)

    created_transactions = []
    current_amount = initial_amount
    for idx in range(3):
        sender = chain[idx]["account_id"]
        receiver = chain[idx + 1]["account_id"]
        # Each hop forwards 93-97% of the received amount.
        forwarded = round(current_amount * random.uniform(0.93, 0.97), 2)
        timestamp = (start_time + timedelta(minutes=idx * 35)).isoformat()
        created_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + idx:06d}",
                "sender_account": sender,
                "receiver_account": receiver,
                "amount": forwarded,
                "timestamp": timestamp,
            }
        )
        current_amount = forwarded

    chain_path = " -> ".join(a["account_id"] for a in chain)
    return {
        "transactions": created_transactions,
        "ground_truth_entries": [
            {
                "account_id": chain[0]["account_id"],
                "scenario_type": "pass_through",
                "description": (
                    f"Layered pass-through detected: {initial_amount:,.2f} cascaded along {chain_path}."
                ),
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + len(created_transactions),
    }
