"""Inject a rapid money pass-through scenario."""

import random
from datetime import datetime, timedelta


def inject_rapid_pass_through(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject a rapid pass-through chain A -> B -> C with a short time gap."""
    candidate_b = random.choice(accounts)
    candidate_a = random.choice([a for a in accounts if a["account_id"] != candidate_b["account_id"]])
    candidate_c = random.choice(
        [a for a in accounts if a["account_id"] not in {candidate_b["account_id"], candidate_a["account_id"]}]
    )

    amount = round(random.uniform(1000.0, 100000.0), 2)
    first_timestamp = datetime.utcnow() - timedelta(minutes=random.randint(10, 30))
    second_timestamp = first_timestamp + timedelta(seconds=random.randint(60, 300))
    forwarded_amount = round(amount * random.uniform(0.90, 0.99), 2)

    first_tx = {
        "transaction_id": f"TX{next_transaction_index:06d}",
        "sender_account": candidate_a["account_id"],
        "receiver_account": candidate_b["account_id"],
        "amount": amount,
        "timestamp": first_timestamp.isoformat(),
    }

    second_tx = {
        "transaction_id": f"TX{next_transaction_index + 1:06d}",
        "sender_account": candidate_b["account_id"],
        "receiver_account": candidate_c["account_id"],
        "amount": forwarded_amount,
        "timestamp": second_timestamp.isoformat(),
    }

    return {
        "transactions": [first_tx, second_tx],
        "ground_truth_entries": [
            {
                "account_id": candidate_b["account_id"],
                "scenario_type": "rapid_pass_through",
                "description": f"Injected a rapid pass-through chain through account {candidate_b['account_id']} with forwarded amount {forwarded_amount}.",
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
        "next_transaction_index": next_transaction_index + 2,
    }
