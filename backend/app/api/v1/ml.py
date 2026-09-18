import json
import os
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.ml.explainer import xai_explainer_service
from app.ml.inference import inference_service
from app.models.event import SecurityEvent
from app.schemas.ml import (
    ExplainFeaturesRequest,
    MLPredictionRequest,
    MLPredictionResponse,
    ModelInfoResponse,
    XAIExplanationResponse,
)

router = APIRouter(prefix="/ml", tags=["Machine Learning Detection & XAI"])


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """Returns active Random Forest threat model architecture and evaluation metrics."""
    return inference_service.get_model_info()


@router.get("/evaluation-report")
async def get_evaluation_report():
    """Returns the comprehensive benchmark evaluation report with confusion matrices."""
    report_path = os.path.join(settings.MODELS_DIR, "evaluation_report.json")
    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation report not found. Please train models first.",
        )
    with open(report_path, "r") as f:
        data = json.load(f)
    return data


@router.post("/predict", response_model=MLPredictionResponse)
async def predict_threat(
    payload: MLPredictionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluates arbitrary network feature vector or existing event ID,
    returning binary threat probability, multi-class categorization, and detection evidence.
    """
    event_dict: Dict[str, Any] = {}

    if payload.event_id:
        query = select(SecurityEvent).where(SecurityEvent.id == payload.event_id)
        result = await db.execute(query)
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Security event '{payload.event_id}' not found.",
            )
        event_dict = {
            "source": event.source,
            "event_type": event.event_type,
            "protocol": event.protocol,
            "destination_port": event.destination_port,
            "user_identity": event.user_identity,
            "message": event.message,
            "raw_features": event.raw_features or {},
        }
    elif payload.features:
        event_dict = payload.features
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'event_id' or 'features' in request payload.",
        )

    try:
        prediction = inference_service.predict(event_dict)
        return prediction
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference failed: {str(e)}",
        )


@router.post("/analyze-event/{event_id}", response_model=MLPredictionResponse)
async def analyze_event_by_id(
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Pulls existing event from PostgreSQL and runs ML threat analysis."""
    query = select(SecurityEvent).where(SecurityEvent.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security event '{event_id}' not found.",
        )

    event_dict = {
        "source": event.source,
        "event_type": event.event_type,
        "protocol": event.protocol,
        "destination_port": event.destination_port,
        "user_identity": event.user_identity,
        "message": event.message,
        "raw_features": event.raw_features or {},
    }

    prediction = inference_service.predict(event_dict)
    return prediction


@router.get("/explain/{event_id}", response_model=XAIExplanationResponse)
async def explain_event_by_id(
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Computes SHAP TreeExplainer feature attributions for an existing database event,
    returning positive vs negative drivers, base expected value, and rule consensus.
    """
    query = select(SecurityEvent).where(SecurityEvent.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security event '{event_id}' not found.",
        )

    event_dict = {
        "source": event.source,
        "event_type": event.event_type,
        "protocol": event.protocol,
        "destination_port": event.destination_port,
        "user_identity": event.user_identity,
        "message": event.message,
        "raw_features": event.raw_features or {},
    }

    try:
        explanation = xai_explainer_service.explain(event_dict, event_id=event.id)
        return explanation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation failed: {str(e)}",
        )


@router.post("/explain", response_model=XAIExplanationResponse)
async def explain_custom_features(
    payload: ExplainFeaturesRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Computes SHAP feature attributions on-demand for arbitrary feature dictionaries
    or existing event ID.
    """
    event_dict: Dict[str, Any] = {}

    if payload.event_id:
        query = select(SecurityEvent).where(SecurityEvent.id == payload.event_id)
        result = await db.execute(query)
        event = result.scalar_one_or_none()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Security event '{payload.event_id}' not found.",
            )
        event_dict = {
            "source": event.source,
            "event_type": event.event_type,
            "protocol": event.protocol,
            "destination_port": event.destination_port,
            "user_identity": event.user_identity,
            "message": event.message,
            "raw_features": event.raw_features or {},
        }
    elif payload.features:
        event_dict = payload.features
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'event_id' or 'features' in request payload.",
        )

    try:
        explanation = xai_explainer_service.explain(event_dict, event_id=payload.event_id)
        return explanation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SHAP explanation failed: {str(e)}",
        )


