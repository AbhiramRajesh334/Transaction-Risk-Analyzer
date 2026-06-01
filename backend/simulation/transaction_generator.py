"""Synthetic transaction generator for realistic financial activity."""

import random
from datetime import datetime, timedelta
from simulation.profile_generator import get_account_profiles


def _build_counterparty_map(accounts: list[dict]) -> dict[str, list[str]]:
    """Create a limited counterparty set for each account based on profile behavior."""
    profiles = get_account_profiles()
    counterparty_map = {}
    account_ids = [account["account_id"] for account in accounts]

    for account in accounts:
        profile = profiles[account["account_type"]]
        possible_receivers = [account_id for account_id in account_ids if account_id != account["account_id"]]
        desired_count = min(len(possible_receivers), random.randint(*profile.counterparty_range))
        counterparty_map[account["account_id"]] = random.sample(possible_receivers, desired_count)

    return counterparty_map


def _choose_sender(account_ids: list[str], account_types: dict[str, str]) -> str:
    """Choose a sender account using weighted transaction frequency by profile."""
    weights = [get_account_profiles()[account_types[account_id]].transaction_weight for account_id in account_ids]
    return random.choices(account_ids, weights=weights, k=1)[0]


def _build_transaction_id(index: int) -> str:
    return f"TX{index:06d}"


def _build_transaction_amount(account_type: str) -> float:
    """Sample a transaction amount based on the sender account profile."""
    profile = get_account_profiles()[account_type]
    amount = random.uniform(profile.amount_range[0], profile.amount_range[1])
    return round(amount, 2)


def _build_timestamp() -> str:
    """Generate a timestamp inside the last 30 days."""
    now = datetime.utcnow()
    offset_seconds = random.randint(0, 30 * 24 * 60 * 60)
    return (now - timedelta(seconds=offset_seconds)).isoformat()


def generate_transactions(
    accounts: list[dict], number_of_transactions: int, start_index: int = 1
) -> list[dict]:
    """Generate synthetic transactions for existing accounts while avoiding self-transfers."""
    if len(accounts) < 2:
        raise ValueError("At least two accounts are required to generate transactions.")

    account_ids = [account["account_id"] for account in accounts]
    account_types = {account["account_id"]: account["account_type"] for account in accounts}
    counterparty_map = _build_counterparty_map(accounts)

    transactions = []
    transaction_index = start_index

    while len(transactions) < number_of_transactions:
        sender = _choose_sender(account_ids, account_types)
        receiver_candidates = counterparty_map.get(sender, [])
        if not receiver_candidates:
            continue

        receiver = random.choice(receiver_candidates)
        if receiver == sender:
            continue

        transaction = {
            "transaction_id": _build_transaction_id(transaction_index),
            "sender_account": sender,
            "receiver_account": receiver,
            "amount": _build_transaction_amount(account_types[sender]),
            "timestamp": _build_timestamp(),
        }
        transactions.append(transaction)
        transaction_index += 1

    return sorted(transactions, key=lambda item: item["timestamp"])
