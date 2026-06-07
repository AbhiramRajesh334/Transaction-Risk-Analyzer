"""Generate a realistic, small demo dataset with clustered communities.

Produces 16 accounts and a compact transaction network with visible student,
salaried, and business clusters. The demo generator clears stale data and
injects exactly five fraud scenarios while keeping the final graph investigator-friendly.
"""

import random
from collections import Counter
from datetime import datetime, timedelta
from typing import List

from database.database import clear_demo_data, get_db_connection, insert_ground_truth_entries
from services.account_service import insert_accounts, list_accounts
from services.transaction_service import insert_transactions, list_transactions
from app.simulation.scenarios.activity_spike import inject_activity_spike
from app.simulation.scenarios.amount_anomaly import inject_amount_anomaly
from app.simulation.scenarios.rapid_pass_through import inject_rapid_pass_through
from app.simulation.scenarios.counterparty_explosion import inject_counterparty_explosion
from app.simulation.scenarios.suspicious_exposure import inject_suspicious_exposure
from app.simulation.scenarios.round_tripping import inject_round_tripping
from app.simulation.scenarios.structuring import inject_structuring
from app.simulation.scenarios.circular_flow import inject_circular_flow

SEED = 42


def _build_accounts() -> List[dict]:
    """Create a fixed set of 16 accounts: 6 Student, 6 Salaried, 4 Business."""
    accounts = []
    for i in range(1, 7):
        accounts.append(
            {
                "account_id": f"STU{i:02d}",
                "account_type": "Student",
                "created_at": (datetime.utcnow() - timedelta(days=30 + i)).isoformat(),
            }
        )

    for i in range(1, 7):
        accounts.append(
            {
                "account_id": f"SAL{i:02d}",
                "account_type": "Salaried",
                "created_at": (datetime.utcnow() - timedelta(days=60 + i * 3)).isoformat(),
            }
        )

    for i in range(1, 5):
        accounts.append(
            {
                "account_id": f"BUS{i:02d}",
                "account_type": "Business",
                "created_at": (datetime.utcnow() - timedelta(days=120 + i * 10)).isoformat(),
            }
        )

    return accounts


def _build_transaction_timestamp(start: datetime, minute_offset: int) -> str:
    return (start + timedelta(minutes=minute_offset)).isoformat()


def _build_amount(account_type: str) -> float:
    if account_type == "Student":
        return round(random.uniform(20.0, 120.0), 2)
    if account_type == "Salaried":
        return round(random.uniform(80.0, 450.0), 2)
    return round(random.uniform(200.0, 4000.0), 2)


def _generate_community_transactions(accounts: List[dict]) -> List[dict]:
    account_map = {account["account_id"]: account for account in accounts}
    students = [account["account_id"] for account in accounts if account["account_type"] == "Student"]
    salaried = [account["account_id"] for account in accounts if account["account_type"] == "Salaried"]
    businesses = [account["account_id"] for account in accounts if account["account_type"] == "Business"]

    transactions = []
    tx_index = 1
    start_time = datetime.utcnow() - timedelta(days=12)
    minute_offset = 0

    def add_tx(sender: str, receiver: str):
        nonlocal tx_index, minute_offset
        transactions.append(
            {
                "transaction_id": f"TX{tx_index:06d}",
                "sender_account": sender,
                "receiver_account": receiver,
                "amount": _build_amount(account_map[sender]["account_type"]),
                "timestamp": _build_transaction_timestamp(start_time, minute_offset),
            }
        )
        tx_index += 1
        minute_offset += 12

    # Student clusters: repeat payments among a small set of peer counterparties and one shared vendor.
    student_clusters = [students[:4], students[4:]]
    for cluster_index, cluster in enumerate(student_clusters):
        vendor = businesses[cluster_index % len(businesses)]
        for student in cluster:
            peers = [peer for peer in cluster if peer != student]
            if peers:
                add_tx(student, peers[0])
            if len(peers) > 1:
                add_tx(student, peers[1])
            add_tx(student, vendor)

    # Salaried accounts: limited family and household relationships, with steady vendor flows.
    salary_vendor_map = {
        "rent": businesses[2],
        "utilities": businesses[3],
        "groceries": businesses[0],
    }
    for index, salaried_account in enumerate(salaried):
        family_members = [a for a in salaried if a != salaried_account][:2]
        add_tx(salaried_account, salary_vendor_map["rent"])
        add_tx(salaried_account, salary_vendor_map["utilities"])
        add_tx(salaried_account, salary_vendor_map["groceries"])
        add_tx(salaried_account, family_members[0])

    # Business accounts: moderate outgoing activity to a consistent set of customers and partners.
    business_map = {
        businesses[0]: [salaried[0], salaried[1], students[0], students[3]],
        businesses[1]: [salaried[2], salaried[3], students[1], students[4]],
        businesses[2]: [salaried[4], salaried[5], students[2], students[5]],
        businesses[3]: [salaried[0], salaried[2], students[0], students[2]],
    }

    for sender, receivers in business_map.items():
        for receiver in receivers:
            add_tx(sender, receiver)

    # A minimal cross-cluster payment to preserve realism without over-densifying the network.
    add_tx(students[0], businesses[2])

    return transactions


def generate_demo_dataset() -> dict:
    """Reset the DB and create the realistic demo dataset with fraud injection."""
    random.seed(SEED)
    clear_demo_data()

    accounts = _build_accounts()
    insert_accounts(accounts)

    base_transactions = _generate_community_transactions(accounts)
    insert_transactions(base_transactions)

    accounts_db = list_accounts()
    transactions_db = list_transactions()
    next_tx_index = max(int(tx["transaction_id"].replace("TX", "")) for tx in transactions_db) + 1 if transactions_db else 1

    injected_transactions = []
    injected_ground = []

    for scenario_executor in [
        inject_activity_spike,
        inject_amount_anomaly,
        inject_rapid_pass_through,
        inject_counterparty_explosion,
        inject_suspicious_exposure,
        inject_round_tripping,
        inject_structuring,
        inject_circular_flow,
    ]:
        result = scenario_executor(accounts_db, transactions_db, next_tx_index)
        next_tx_index = result["next_transaction_index"]
        injected_transactions.extend(result.get("transactions", []))
        injected_ground.extend(result.get("ground_truth_entries", []))

        if result.get("new_accounts"):
            insert_accounts(result["new_accounts"])
            accounts_db.extend(result["new_accounts"])

        transactions_db.extend(result.get("transactions", []))

    if injected_transactions:
        insert_transactions(injected_transactions)

    if injected_ground:
        insert_ground_truth_entries(injected_ground)

    final_accounts = list_accounts()
    final_transactions = list_transactions()

    if len(final_accounts) != 16:
        raise ValueError(
            f"Demo dataset must contain exactly 16 accounts, found {len(final_accounts)}."
        )
    if len(final_transactions) >= 100:
        raise ValueError(
            f"Demo dataset must contain fewer than 100 transactions, found {len(final_transactions)}."
        )

    risk_counts = Counter()
    for transaction in injected_transactions:
        risk_counts[transaction["sender_account"]] += 1
        risk_counts[transaction["receiver_account"]] += 1

    high_risk_accounts = [account_id for account_id, _ in risk_counts.most_common(4)]
    if high_risk_accounts:
        connection = get_db_connection()
        with connection:
            connection.executemany(
                "UPDATE accounts SET account_type = 'HighRisk' WHERE account_id = ?",
                [(account_id,) for account_id in high_risk_accounts],
            )

    final_accounts = list_accounts()
    final_transactions = list_transactions()

    return {
        "base_accounts": len(accounts),
        "base_transactions": len(base_transactions),
        "injected_transactions": len(injected_transactions),
        "injected_ground_truth": len(injected_ground),
        "final_accounts": len(final_accounts),
        "final_transactions": len(final_transactions),
    }
