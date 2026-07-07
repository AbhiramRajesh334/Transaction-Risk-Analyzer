"""Final risk scoring engine: convert indicators into an explainable risk score."""

from typing import Dict, List

from services.risk_indicator_service import (
    get_all_indicators,
    get_indicators_for_account,
)
from services.account_service import list_accounts


WEIGHTS = {
    "activity_spike": 0.12,
    "amount_anomaly": 0.16,
    "pass_through": 0.22,
    "counterparty_explosion": 0.08,
    "suspicious_exposure": 0.16,
    "round_tripping": 0.14,
    "structuring": 0.08,
    "circular_flow": 0.08,
}


def _risk_level(score: float) -> str:
    if score >= 65:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _top_reasons(indicators: dict, limit: int = 8) -> List[str]:
    contributions = []
    for key, weight in WEIGHTS.items():
        indicator = indicators.get(key, {})
        score = indicator.get("score", 0)
        if score > 0:
            contributions.append((key, score * weight))

    contributions.sort(key=lambda item: item[1], reverse=True)
    return [key.replace("_", " ").title() for key, _ in contributions[:limit]]


def _build_indicator_breakdown(indicators: dict) -> dict:
    return {
        key: {
            "score": indicators.get(key, {}).get("score", 0),
            "evidence": indicators.get(key, {}).get("evidence", {}),
        }
        for key in WEIGHTS.keys()
    }


def _compute_score(indicators: dict) -> float:
    score = 0.0
    peak_indicator = 0.0
    for key, weight in WEIGHTS.items():
        indicator = indicators.get(key, {})
        indicator_score = indicator.get("score", 0)
        score += indicator_score * weight
        peak_indicator = max(peak_indicator, indicator_score)

    # Strong single-signal boost: one very high indicator should pull score up.
    if peak_indicator >= 80:
        score += (peak_indicator - 80) * 0.45

    return max(0.0, min(100.0, score))


def _build_risk_profile(account_id: str, indicators: dict) -> dict:
    normalized_score = _compute_score(indicators)
    return {
        "account_id": account_id,
        "risk_score": int(round(normalized_score)),
        "risk_level": _risk_level(normalized_score),
        "top_reasons": _top_reasons(indicators),
        "indicator_breakdown": _build_indicator_breakdown(indicators),
    }


def get_risk_for_account(account_id: str) -> dict:
    indicators = get_indicators_for_account(account_id)
    return _build_risk_profile(account_id, indicators)


def get_risk_for_all() -> List[dict]:
    indicators = get_all_indicators()
    return [_build_risk_profile(entry["account_id"], entry) for entry in indicators]


def get_high_risk_accounts() -> List[dict]:
    return [
        profile
        for profile in get_risk_for_all()
        if profile["risk_level"] == "HIGH"
    ]


def get_top_accounts(limit: int = 10) -> List[dict]:
    return sorted(get_risk_for_all(), key=lambda item: item["risk_score"], reverse=True)[:limit]
