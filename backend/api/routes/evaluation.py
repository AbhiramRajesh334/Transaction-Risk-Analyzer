"""Evaluation metrics API routes."""

from fastapi import APIRouter, Query

from services.evaluation_service import get_evaluation_report

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/metrics")
def get_metrics(threshold: int = Query(60, ge=0, le=100)):
    return get_evaluation_report(threshold=threshold)
