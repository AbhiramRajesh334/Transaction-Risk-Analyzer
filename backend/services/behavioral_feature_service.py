"""Behavioral feature engine: compute and cache per-account behavioral metrics.

Features are computed from transactions and graph relationships and cached
for fast API access. The cache is automatically refreshed when the total
transaction count changes.

Each feature includes a short comment explaining what it measures and why
it will be useful for future risk indicators.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from services.transaction_service import list_transactions, count_transactions
from services.account_service import list_accounts
from graph_engine.graph_queries import (
    get_account_transactions,
    get_account_neighbors,
    get_incoming_neighbors,
    get_outgoing_neighbors,
    get_account_degree,
    account_participates_in_cycle,
)


# In-memory cache for computed features
_cache: Dict[str, dict] = {}
_last_tx_count: Optional[int] = None
_last_refreshed: Optional[datetime] = None


STRUCTURING_MIN = 8000.0
STRUCTURING_MAX = 9999.0


def _count_round_trips(transactions: list[dict]) -> int:
    """Count counterparties where funds were both sent and received."""
    sent_to: Dict[str, float] = {}
    received_from: Dict[str, float] = {}

    for tx in transactions:
        amount = float(tx.get("amount") or 0)
        if tx.get("direction") == "outgoing":
            counterparty = tx.get("receiver_account")
            sent_to[counterparty] = sent_to.get(counterparty, 0.0) + amount
        else:
            counterparty = tx.get("sender_account")
            received_from[counterparty] = received_from.get(counterparty, 0.0) + amount

    round_trips = 0
    for counterparty, sent_amount in sent_to.items():
        received_amount = received_from.get(counterparty, 0.0)
        # Require meaningful bidirectional flow: both directions >= ₹5000
        if received_amount >= 5000 and sent_amount >= 5000:
            round_trips += 1
    return round_trips


def _count_structuring_transactions(transactions: list[dict]) -> int:
    return sum(
        1
        for tx in transactions
        if STRUCTURING_MIN <= float(tx.get("amount") or 0) <= STRUCTURING_MAX
    )


def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _compute_features_for_account(account_id: str) -> dict:
    """Compute the behavioral features for a single account.

    Explanations are embedded as comments in each returned field.
    """
    transactions = get_account_transactions(account_id)

    # Transaction counts
    total_count = len(transactions)  # Total number of transactions involving account
    incoming = [tx for tx in transactions if tx.get("direction") == "incoming"]
    outgoing = [tx for tx in transactions if tx.get("direction") == "outgoing"]
    incoming_count = len(incoming)  # How many times this account received funds
    outgoing_count = len(outgoing)  # How many times this account sent funds

    # Amount aggregates
    incoming_amount = sum((tx.get("amount") or 0) for tx in incoming)  # Total value received
    outgoing_amount = sum((tx.get("amount") or 0) for tx in outgoing)  # Total value sent

    # Simple stats
    all_amounts = [tx.get("amount") or 0 for tx in transactions]
    average_amount = (sum(all_amounts) / len(all_amounts)) if all_amounts else 0.0
    max_amount = max(all_amounts) if all_amounts else 0.0

    # Unique counterparties
    counterparties = set()
    for tx in transactions:
        if tx.get("direction") == "incoming":
            counterparties.add(tx.get("sender_account"))
        else:
            counterparties.add(tx.get("receiver_account"))
    unique_counterparties = len(counterparties)  # Distinct other accounts transacted with

    # Degrees from graph
    in_degree = len(get_incoming_neighbors(account_id))  # Number of distinct senders
    out_degree = len(get_outgoing_neighbors(account_id))  # Number of distinct receivers

    # Transaction velocity: transactions per hour across observed span.
    times = [_parse_iso(tx.get("timestamp")) for tx in transactions if tx.get("timestamp")]
    times = [t for t in times if t]
    velocity = 0.0
    if times:
        span = (max(times) - min(times)).total_seconds() / 3600.0
        if span <= 0:
            # Fallback: if all timestamps identical, treat as instantaneous but
            # report velocity as count per 1 hour.
            velocity = float(len(transactions))
        else:
            velocity = len(transactions) / span
    else:
        # If no timestamps, fall back to transactions per day using available count
        velocity = float(len(transactions))

    # Pass through ratio: how much leaves vs arrives. Useful to detect laundering.
    pass_through_ratio = None
    try:
        if incoming_amount > 0:
            pass_through_ratio = outgoing_amount / incoming_amount
        else:
            pass_through_ratio = None
    except Exception:
        pass_through_ratio = None

    # Recent activity count: transactions in the last 7 days (configurable window).
    recent_window = datetime.utcnow() - timedelta(days=7)
    recent_activity_count = 0
    for t in times:
        if t >= recent_window:
            recent_activity_count += 1

    round_trip_count = _count_round_trips(transactions)
    structuring_count = _count_structuring_transactions(transactions)
    circular_flow_participation = 1 if account_participates_in_cycle(account_id) else 0

    features = {
        "account_id": account_id,
        "transaction_count": total_count,
        "incoming_count": incoming_count,
        "outgoing_count": outgoing_count,
        "incoming_amount": incoming_amount,
        "outgoing_amount": outgoing_amount,
        "average_amount": average_amount,
        "max_amount": max_amount,
        "unique_counterparties": unique_counterparties,
        "in_degree": in_degree,
        "out_degree": out_degree,
        "velocity": velocity,
        "pass_through_ratio": pass_through_ratio,
        "recent_activity_count": recent_activity_count,
        "round_trip_count": round_trip_count,
        "structuring_count": structuring_count,
        "circular_flow_participation": circular_flow_participation,
    }

    return features


def recompute_all_features() -> Dict[str, dict]:
    """Force a full recomputation of features for all accounts.

    This is intentionally explicit and relatively expensive; callers should
    normally call ``refresh_if_needed`` which avoids recomputing on every
    request.
    """
    global _cache, _last_tx_count, _last_refreshed
    _cache = {}
    accounts = list_accounts()
    for acc in accounts:
        acc_id = acc["account_id"]
        _cache[acc_id] = _compute_features_for_account(acc_id)

    _last_tx_count = count_transactions()
    _last_refreshed = datetime.utcnow()
    return _cache


def refresh_if_needed() -> None:
    """Refresh cached features only when transaction count has changed.

    This simple change-detection avoids recomputing on every API call while
    ensuring features reflect new data after inserts/deletes.
    """
    global _last_tx_count
    current = count_transactions()
    if _last_tx_count != current or not _cache:
        recompute_all_features()


def get_features_for_account(account_id: str) -> dict:
    """Return features for a single account, refreshing cache if needed."""
    refresh_if_needed()
    return _cache.get(account_id) or {
        "account_id": account_id,
        "transaction_count": 0,
        "incoming_count": 0,
        "outgoing_count": 0,
        "incoming_amount": 0.0,
        "outgoing_amount": 0.0,
        "average_amount": 0.0,
        "max_amount": 0.0,
        "unique_counterparties": 0,
        "in_degree": 0,
        "out_degree": 0,
        "velocity": 0.0,
        "pass_through_ratio": None,
        "recent_activity_count": 0,
        "round_trip_count": 0,
        "structuring_count": 0,
        "circular_flow_participation": 0,
    }


def get_all_features() -> List[dict]:
    """Return features for all accounts."""
    refresh_if_needed()
    return list(_cache.values())


def get_top_activity(limit: int = 10) -> List[dict]:
    """Return accounts sorted by transaction count (descending)."""
    refresh_if_needed()
    return sorted(_cache.values(), key=lambda f: f.get("transaction_count", 0), reverse=True)[:limit]


def get_top_counterparties(limit: int = 10) -> List[dict]:
    """Return accounts sorted by number of unique counterparties (descending)."""
    refresh_if_needed()
    return sorted(_cache.values(), key=lambda f: f.get("unique_counterparties", 0), reverse=True)[:limit]
