"""Synthetic account generator for student, salaried, and business profiles."""

import random
from datetime import datetime, timedelta
from simulation.profile_generator import choose_profile_types


def _build_account_id(index: int, account_type: str) -> str:
    prefix_map = {"Student": "STU", "Salaried": "SAL", "Business": "BUS"}
    prefix = prefix_map.get(account_type, "ACC")
    return f"{prefix}{index:04d}"


def _build_created_at() -> str:
    days_ago = random.randint(1, 90)
    creation_date = datetime.utcnow() - timedelta(days=days_ago)
    return creation_date.isoformat()


def generate_accounts(number_of_accounts: int, start_index: int = 1) -> list[dict]:
    """Create synthetic account metadata for the requested number of accounts."""
    profile_types = choose_profile_types(number_of_accounts)
    random.shuffle(profile_types)

    accounts = []
    for offset, account_type in enumerate(profile_types):
        account_id = _build_account_id(start_index + offset, account_type)
        accounts.append(
            {
                "account_id": account_id,
                "account_type": account_type,
                "created_at": _build_created_at(),
            }
        )

    return accounts
