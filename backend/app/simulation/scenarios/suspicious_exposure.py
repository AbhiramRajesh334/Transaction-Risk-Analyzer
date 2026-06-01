"""Inject a suspicious exposure scenario."""

import random
from datetime import datetime


def _build_high_risk_account_id(existing_account_ids: set[str]) -> str:
    base = "X"
    suffix = 1
    while True:
        account_id = f"{base}{suffix:03d}"
        if account_id not in existing_account_ids:
            return account_id
        suffix += 1


def inject_suspicious_exposure(accounts: list[dict], transactions: list[dict], next_transaction_index: int) -> dict:
    """Inject a suspicious business account behavior into the existing network."""
    candidates = [a for a in accounts if a["account_type"] == "Business"]
    if not candidates:
        candidates = accounts

    suspect = random.choice(candidates)
    receivers = random.sample([a for a in accounts if a["account_id"] != suspect["account_id"]], min(3, len(accounts) - 1))
    injected_transactions = []
    ground_truth_entries = [
        {
            "account_id": suspect["account_id"],
            "scenario_type": "suspicious_exposure",
            "description": f"Marked existing account {suspect['account_id']} as suspicious and connected it to several normal counterparts.",
            "created_at": datetime.utcnow().isoformat(),
        }
    ]

    for offset, receiver in enumerate(receivers):
        injected_transactions.append(
            {
                "transaction_id": f"TX{next_transaction_index + offset:06d}",
                "sender_account": suspect["account_id"],
                "receiver_account": receiver["account_id"],
                "amount": round(random.uniform(1000.0, 30000.0), 2),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        ground_truth_entries.append(
            {
                "account_id": receiver["account_id"],
                "scenario_type": "suspicious_exposure",
                "description": f"Account {receiver['account_id']} received funds from suspicious account {suspect['account_id']}.",
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    return {
        "transactions": injected_transactions,
        "ground_truth_entries": ground_truth_entries,
        "next_transaction_index": next_transaction_index + len(injected_transactions),
    }
