"""Synthetic account profile definitions and behavior attributes."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class AccountProfile:
    account_type: str
    amount_range: tuple[float, float]
    counterparty_range: tuple[int, int]
    transaction_weight: int
    description: str


def get_account_profiles() -> Dict[str, AccountProfile]:
    """Return the profile configuration for each synthetic account type."""
    return {
        "Student": AccountProfile(
            account_type="Student",
            amount_range=(20.0, 1500.0),
            counterparty_range=(2, 4),
            transaction_weight=1,
            description="Low-value transactions, rare activity, small set of counterparties.",
        ),
        "Salaried": AccountProfile(
            account_type="Salaried",
            amount_range=(200.0, 12000.0),
            counterparty_range=(4, 7),
            transaction_weight=3,
            description="Moderate transaction size with regular recurring payments and a stable counterparty set.",
        ),
        "Business": AccountProfile(
            account_type="Business",
            amount_range=(1000.0, 100000.0),
            counterparty_range=(8, 15),
            transaction_weight=7,
            description="High-volume activity across many counterparties and larger payment values.",
        ),
    }


def choose_profile_types(number_of_accounts: int) -> list[str]:
    """Generate a list of account types with a balanced distribution."""
    student_count = max(1, number_of_accounts // 4)
    business_count = max(1, number_of_accounts // 4)
    salaried_count = number_of_accounts - student_count - business_count

    return ["Student"] * student_count + ["Salaried"] * salaried_count + ["Business"] * business_count
