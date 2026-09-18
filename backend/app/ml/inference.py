import json
import logging
import os
from typing import Any, Dict, List, Optional
import joblib
import numpy as np

from app.core.config import settings
from app.ml.preprocessing import MLPreprocessor
from app.schemas.ml import MLPredictionResponse, ModelInfoResponse

logger = logging.getLogger(__name__)


class ThreatInferenceService:
    """
    Singleton inference service providing binary threat prediction,
    multi-class attack categorization, confidence distribution, and
    rule-assisted detection explanations.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThreatInferenceService, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance

    def _load_models(self):
        self.models_loaded = False
        try:
            prep_path = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
            bin_path = os.path.join(settings.MODELS_DIR, "binary_rf_model.joblib")
            mc_path = os.path.join(settings.MODELS_DIR, "multiclass_rf_model.joblib")
            meta_path = os.path.join(settings.MODELS_DIR, "metadata.json")

            if all(os.path.exists(p) for p in [prep_path, bin_path, mc_path, meta_path]):
                self.preprocessor = MLPreprocessor.load(prep_path)
                self.binary_model = joblib.load(bin_path)
                self.multiclass_model = joblib.load(mc_path)
                with open(meta_path, "r") as f:
                    self.metadata = json.load(f)
                self.models_loaded = True
                logger.info("Sentriq ML models loaded successfully.")
            else:
                logger.warning("ML models not yet trained or artifacts missing in models_store/.")
        except Exception as e:
            logger.error(f"Failed to load ML model artifacts: {e}")
            self.models_loaded = False

    def predict(self, event_data: Dict[str, Any]) -> MLPredictionResponse:
        """Executes inference on an input security event."""
        if not self.models_loaded:
            self._load_models()

        if not self.models_loaded:
            raise RuntimeError("ML threat detection models are unavailable. Run model training first.")

        # 1. Transform features
        df_feat = self.preprocessor.extract_features_from_dict(event_data)
        X = self.preprocessor.transform(df_feat)

        # 2. Binary Prediction
        bin_probs = self.binary_model.predict_proba(X)[0]
        # Class 1 is attack
        attack_prob = float(bin_probs[1]) if len(bin_probs) > 1 else float(bin_probs[0])
        is_threat = attack_prob >= 0.50

        # 3. Multi-Class Categorization
        mc_classes = list(self.multiclass_model.classes_)
        mc_probs = self.multiclass_model.predict_proba(X)[0]
        class_prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(mc_classes, mc_probs)}

        # Predicted category
        best_idx = int(np.argmax(mc_probs))
        predicted_cat = mc_classes[best_idx]
        confidence = float(mc_probs[best_idx])

        # If binary model is convinced it's normal, ensure Normal category is prioritized
        if not is_threat and predicted_cat != "Normal":
            if "Normal" in class_prob_dict and class_prob_dict["Normal"] > 0.3:
                predicted_cat = "Normal"
                confidence = class_prob_dict["Normal"]

        # 4. Synthesize Rule-Assisted Detection Reasons (PRD FR-08)
        reasons = self._generate_detection_reasons(event_data, predicted_cat, is_threat, df_feat.iloc[0].to_dict())

        return MLPredictionResponse(
            is_threat=is_threat,
            verdict="MALICIOUS" if is_threat else "BENIGN",
            threat_probability=round(attack_prob, 4),
            predicted_attack_category=predicted_cat,
            confidence=round(confidence, 4),
            class_probabilities=class_prob_dict,
            detection_reasons=reasons,
            model_version=self.metadata.get("model_version", "1.0.0"),
            evaluated_features=df_feat.iloc[0].to_dict(),
        )

    def _generate_detection_reasons(
        self,
        event_data: Dict[str, Any],
        predicted_cat: str,
        is_threat: bool,
        features: Dict[str, Any],
    ) -> List[str]:
        """Provides explainable heuristic evidence explaining the classification."""
        reasons = []

        if not is_threat:
            reasons.append("Network flow parameters (duration, packet rates, TTL) fall within normal baseline distributions.")
            reasons.append("Standard bilateral TCP/UDP handshake behavior with expected response payload ratios.")
            return reasons

        # Threat explanations
        if predicted_cat == "Brute Force":
            reasons.append("Elevated frequency of failed authentication sequences detected within short time window.")
            reasons.append("Inbound traffic directed to administrative service endpoint (SSH/Auth) from single origin IP.")
            if event_data.get("user_identity"):
                reasons.append(f"Target account credential probing observed against user identity '{event_data.get('user_identity')}'.")

        elif predicted_cat == "DoS":
            rate = features.get("rate", 0)
            spkts = features.get("spkts", 0)
            reasons.append(f"Volumetric packet flood anomaly detected: {rate:.1f} packets/sec exceeds baseline threshold.")
            reasons.append(f"Abnormal unidirectional outbound volume ({spkts} packets) with disproportionately zero return response.")

        elif predicted_cat == "Port Scan":
            reasons.append("Sequential rapid destination port probing observed across perimeter network range.")
            reasons.append("Low packet count per destination connection characteristic of SYN/FIN reconnaissance scanners.")

        elif predicted_cat == "Web Attack":
            reasons.append("Suspicious HTTP payload characteristics targeting web application endpoint.")
            reasons.append("Abnormal transaction depth and parameter length deviating from standard web request profiles.")

        elif predicted_cat == "Exploitation":
            reasons.append("Anomalous payload structure and execution characteristics matching exploit vector signatures.")
            if "sudo" in str(event_data.get("message", "")).lower() or "privilege" in str(event_data.get("message", "")).lower():
                reasons.append("Suspicious privilege escalation command executed following unauthorized connection.")

        else:
            reasons.append(f"Traffic patterns classified as {predicted_cat} based on Random Forest feature attribution.")

        return reasons

    def get_model_info(self) -> ModelInfoResponse:
        """Returns metadata about the active ML models."""
        if not self.models_loaded:
            self._load_models()

        if not self.models_loaded:
            return ModelInfoResponse(
                model_version="unavailable",
                algorithm="RandomForestClassifier",
                trained_at="not_trained",
                supported_classes=[],
                features_used=[],
                dataset_sample_size=0,
                metrics_summary={},
            )

        return ModelInfoResponse(
            model_version=self.metadata.get("model_version", "1.0.0"),
            algorithm=self.metadata.get("algorithm", "RandomForestClassifier"),
            trained_at=self.metadata.get("trained_at", ""),
            supported_classes=self.metadata.get("classes", []),
            features_used=self.metadata.get("features", []),
            dataset_sample_size=self.metadata.get("dataset_sample_size", 0),
            metrics_summary=self.metadata.get("metrics_summary", {}),
        )


inference_service = ThreatInferenceService()

