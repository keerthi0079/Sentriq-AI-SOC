from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MLPredictionRequest(BaseModel):
    event_id: Optional[str] = None
    features: Optional[Dict[str, Any]] = None


class MLPredictionResponse(BaseModel):
    is_threat: bool
    verdict: str  # "MALICIOUS" or "BENIGN"
    threat_probability: float  # 0.0 to 1.0
    predicted_attack_category: str
    confidence: float  # confidence in the predicted class
    class_probabilities: Dict[str, float]
    detection_reasons: List[str]
    model_version: str
    evaluated_features: Dict[str, Any]


class ModelInfoResponse(BaseModel):
    model_version: str
    algorithm: str
    trained_at: str
    supported_classes: List[str]
    features_used: List[str]
    dataset_sample_size: int
    metrics_summary: Dict[str, float]


class FeatureAttribution(BaseModel):
    feature_name: str
    display_name: str
    feature_value: Any
    shap_value: float
    contribution_percent: float
    direction: str  # "positive" (threat driver) or "negative" (benign indicator)
    baseline_mean: Optional[float] = None


class XAIExplanationResponse(BaseModel):
    event_id: Optional[str] = None
    model_version: str
    predicted_category: str
    attack_probability: float
    base_value: float
    positive_contributors: List[FeatureAttribution]
    negative_contributors: List[FeatureAttribution]
    all_features: List[FeatureAttribution]
    narrative: str
    rule_agreement: bool
    rule_reasons: List[str]
    inference_latency_ms: float


class ExplainFeaturesRequest(BaseModel):
    event_id: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
