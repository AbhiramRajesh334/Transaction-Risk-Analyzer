"""Risk indicator engine: convert behavioral features into fraud indicators."""

from typing import Dict, List, Optional

from services.behavioral_feature_service import get_all_features
from services.baseline_service import get_baseline_for_account, relative_ratio, refresh_baselines
from services.transaction_service import count_transactions
from graph_engine.graph_queries import get_account_neighbors


_cache: Dict[str, dict] = {}
_last_tx_count: Optional[int] = None


def _normalize(value: float, threshold: float, cap: float = 100.0) -> float:
    if threshold <= 0:
        return 0.0
    return min((value / threshold) * 100.0, cap)


def _normalize_relative(value: float, baseline: float, floor: float = 1.0, cap: float = 100.0) -> float:
    ratio = relative_ratio(value, baseline, floor=floor)
    if ratio <= 1.0:
        return 0.0
    return min((ratio - 1.0) * 50.0, cap)


def _round_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def _build_indicator(score: float, evidence: dict) -> dict:
    return {
        "score": _round_score(score),
        "evidence": evidence,
    }


def _activity_spike_indicator(features: dict, baseline: dict) -> dict:
    transaction_count = features["transaction_count"]
    velocity = features["velocity"]
    recent_activity_count = features["recent_activity_count"]

    count_score = 0.5 * _normalize_relative(transaction_count, baseline["transaction_count"], floor=1.0) + 0.5 * _normalize(transaction_count, 18)
    velocity_score = 0.6 * _normalize_relative(velocity, baseline["velocity"], floor=0.2) + 0.4 * _normalize(velocity, 4)
    recent_score = 0.5 * _normalize_relative(recent_activity_count, baseline["recent_activity_count"], floor=1.0) + 0.5 * _normalize(recent_activity_count, 9)

    score = 0.3 * count_score + 0.4 * velocity_score + 0.3 * recent_score
    evidence = {
        "transaction_count": transaction_count,
        "velocity": round(velocity, 3),
        "recent_activity_count": recent_activity_count,
        "baseline": {
            "transaction_count": baseline["transaction_count"],
            "velocity": baseline["velocity"],
            "recent_activity_count": baseline["recent_activity_count"],
        },
        "components": {
            "count_score": _round_score(count_score),
            "velocity_score": _round_score(velocity_score),
            "recent_activity_score": _round_score(recent_score),
        },
    }
    return _build_indicator(score, evidence)


def _amount_anomaly_indicator(features: dict, baseline: dict) -> dict:
    average_amount = features["average_amount"]
    max_amount = features["max_amount"]

    average_score = 0.6 * _normalize_relative(average_amount, baseline["average_amount"], floor=50.0) + 0.4 * _normalize(average_amount, 12000)
    max_score = 0.6 * _normalize_relative(max_amount, baseline["max_amount"], floor=100.0) + 0.4 * _normalize(max_amount, 40000)

    score = 0.45 * average_score + 0.55 * max_score
    evidence = {
        "average_amount": average_amount,
        "max_amount": max_amount,
        "baseline": {
            "average_amount": baseline["average_amount"],
            "max_amount": baseline["max_amount"],
        },
        "components": {
            "average_score": _round_score(average_score),
            "max_score": _round_score(max_score),
        },
    }
    return _build_indicator(score, evidence)


def _pass_through_indicator(features: dict, baseline: dict) -> dict:
    incoming_amount = features["incoming_amount"]
    outgoing_amount = features["outgoing_amount"]
    ratio = features.get("pass_through_ratio")

    amount_score = 0.5 * _normalize_relative(outgoing_amount, baseline["outgoing_amount"], floor=200.0) + 0.5 * _normalize(outgoing_amount, 30000)
    ratio_score = 0.0
    if ratio is not None:
        if ratio >= 1.0:
            ratio_score = _normalize(ratio, 1.5)
        else:
            ratio_score = _normalize(ratio, 1.0) * 0.5

    score = 0.35 * amount_score + 0.65 * ratio_score
    evidence = {
        "incoming_amount": incoming_amount,
        "outgoing_amount": outgoing_amount,
        "pass_through_ratio": ratio,
        "baseline": {"outgoing_amount": baseline["outgoing_amount"]},
        "components": {
            "amount_score": _round_score(amount_score),
            "ratio_score": _round_score(ratio_score),
        },
    }
    return _build_indicator(score, evidence)


def _counterparty_explosion_indicator(features: dict, baseline: dict) -> dict:
    unique_counterparties = features["unique_counterparties"]
    in_degree = features["in_degree"]
    out_degree = features["out_degree"]

    unique_score = 0.6 * _normalize_relative(unique_counterparties, baseline["unique_counterparties"], floor=1.0) + 0.4 * _normalize(unique_counterparties, 10)
    in_score = _normalize(in_degree, 6)
    out_score = _normalize(out_degree, 6)

    score = 0.4 * unique_score + 0.3 * in_score + 0.3 * out_score
    evidence = {
        "unique_counterparties": unique_counterparties,
        "in_degree": in_degree,
        "out_degree": out_degree,
        "baseline": {"unique_counterparties": baseline["unique_counterparties"]},
        "components": {
            "unique_score": _round_score(unique_score),
            "in_score": _round_score(in_score),
            "out_score": _round_score(out_score),
        },
    }
    return _build_indicator(score, evidence)


def _round_tripping_indicator(features: dict) -> dict:
    round_trip_count = features.get("round_trip_count", 0)
    # Scale: 0 trips=0, 1 trip=35, 2 trips=65, 3+ trips=100
    score = _normalize(round_trip_count, 3)
    evidence = {
        "round_trip_count": round_trip_count,
        "components": {"round_trip_score": _round_score(score)},
    }
    return _build_indicator(score, evidence)


def _structuring_indicator(features: dict) -> dict:
    structuring_count = features.get("structuring_count", 0)
    score = _normalize(structuring_count, 3)
    evidence = {
        "structuring_count": structuring_count,
        "threshold_band": "8000-9999",
        "components": {"structuring_score": _round_score(score)},
    }
    return _build_indicator(score, evidence)


def _circular_flow_indicator(features: dict) -> dict:
    participation = features.get("circular_flow_participation", 0)
    pass_through = features.get("pass_through_ratio") or 0.0
    # Not just binary: scale by how strong the pass-through also is.
    # Only confirmed multi-cycle accounts with high pass-through get max score.
    if not participation:
        score = 0.0
    elif pass_through >= 0.9:
        score = 100.0
    elif pass_through >= 0.7:
        score = 80.0
    else:
        score = 55.0
    evidence = {
        "circular_flow_participation": participation,
        "pass_through_ratio": round(pass_through, 2),
        "components": {"cycle_score": _round_score(score)},
    }
    return _build_indicator(score, evidence)


def _suspicious_exposure_indicator(account_id: str, all_indicators: Dict[str, dict]) -> dict:
    neighbors = get_account_neighbors(account_id)
    neighbor_risks = []
    for neighbor_id in neighbors:
        neighbor_indicator = all_indicators.get(neighbor_id)
        if not neighbor_indicator:
            continue
        neighbor_max = max(
            neighbor_indicator["activity_spike"]["score"],
            neighbor_indicator["amount_anomaly"]["score"],
            neighbor_indicator["pass_through"]["score"],
            neighbor_indicator["counterparty_explosion"]["score"],
            neighbor_indicator["round_tripping"]["score"],
            neighbor_indicator["structuring"]["score"],
            neighbor_indicator["circular_flow"]["score"],
        )
        neighbor_risks.append((neighbor_id, neighbor_max))

    if not neighbor_risks:
        evidence = {
            "neighbor_count": 0,
            "suspicious_neighbor_count": 0,
            "neighbor_scores": [],
        }
        return _build_indicator(0.0, evidence)

    neighbor_risks.sort(key=lambda item: item[1], reverse=True)
    risk_scores = [score for _, score in neighbor_risks]
    average_neighbor_risk = sum(risk_scores) / len(risk_scores)
    suspicious_neighbors = [item for item in neighbor_risks if item[1] >= 60]
    suspicious_count = len(suspicious_neighbors)

    score = 0.65 * average_neighbor_risk + min(suspicious_count * 6, 30)
    evidence = {
        "neighbor_count": len(neighbor_risks),
        "suspicious_neighbor_count": suspicious_count,
        "average_neighbor_risk": round(average_neighbor_risk, 2),
        "top_neighbors": [
            {"account_id": account, "max_indicator_score": score}
            for account, score in neighbor_risks[:3]
        ],
    }
    return _build_indicator(score, evidence)


def _compute_indicators_for_account(account_id: str, features: dict) -> dict:
    baseline = get_baseline_for_account(account_id)
    return {
        "account_id": account_id,
        "activity_spike": _activity_spike_indicator(features, baseline),
        "amount_anomaly": _amount_anomaly_indicator(features, baseline),
        "pass_through": _pass_through_indicator(features, baseline),
        "counterparty_explosion": _counterparty_explosion_indicator(features, baseline),
        "round_tripping": _round_tripping_indicator(features),
        "structuring": _structuring_indicator(features),
        "circular_flow": _circular_flow_indicator(features),
        "suspicious_exposure": None,
    }


def recompute_all_indicators() -> Dict[str, dict]:
    global _cache, _last_tx_count
    _cache = {}
    refresh_baselines()
    features = get_all_features()
    feature_map = {entry["account_id"]: entry for entry in features}

    for account_id, feature_data in feature_map.items():
        _cache[account_id] = _compute_indicators_for_account(account_id, feature_data)

    for account_id in list(_cache.keys()):
        _cache[account_id]["suspicious_exposure"] = _suspicious_exposure_indicator(account_id, _cache)

    _last_tx_count = count_transactions()
    return _cache


def refresh_if_needed() -> None:
    global _last_tx_count
    current = count_transactions()
    if _last_tx_count != current or not _cache:
        recompute_all_indicators()


def get_indicators_for_account(account_id: str) -> dict:
    refresh_if_needed()
    return _cache.get(account_id, {
        "account_id": account_id,
        "activity_spike": _build_indicator(0.0, {}),
        "amount_anomaly": _build_indicator(0.0, {}),
        "pass_through": _build_indicator(0.0, {}),
        "counterparty_explosion": _build_indicator(0.0, {}),
        "round_tripping": _build_indicator(0.0, {}),
        "structuring": _build_indicator(0.0, {}),
        "circular_flow": _build_indicator(0.0, {}),
        "suspicious_exposure": _build_indicator(0.0, {}),
    })


def get_all_indicators() -> List[dict]:
    refresh_if_needed()
    return list(_cache.values())


def get_top_activity_spike(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["activity_spike"]["score"], reverse=True
    )[:limit]


def get_top_pass_through(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["pass_through"]["score"], reverse=True
    )[:limit]


def get_top_counterparty_explosion(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["counterparty_explosion"]["score"], reverse=True
    )[:limit]


def get_top_exposure(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["suspicious_exposure"]["score"], reverse=True
    )[:limit]


def get_top_round_tripping(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["round_tripping"]["score"], reverse=True
    )[:limit]


def get_top_structuring(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["structuring"]["score"], reverse=True
    )[:limit]


def get_top_circular_flow(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["circular_flow"]["score"], reverse=True
    )[:limit]


def get_top_amount_anomaly(limit: int = 10) -> List[dict]:
    refresh_if_needed()
    return sorted(
        _cache.values(), key=lambda item: item["amount_anomaly"]["score"], reverse=True
    )[:limit]
