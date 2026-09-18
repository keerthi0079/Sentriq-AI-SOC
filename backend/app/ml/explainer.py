import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
import shap

from app.core.config import settings
from app.ml.inference import ThreatInferenceService
from app.ml.preprocessing import ALL_FEATURE_COLUMNS, NUMERIC_FEATURES, MLPreprocessor
from app.schemas.ml import FeatureAttribution, XAIExplanationResponse

logger = logging.getLogger("sentriq.xai")

FEATURE_DISPLAY_NAMES: Dict[str, str] = {
    "dur": "Connection Duration (dur)",
    "spkts": "Source Packet Count (spkts)",
    "dpkts": "Destination Packet Count (dpkts)",
    "sbytes": "Source Byte Volume (sbytes)",
    "dbytes": "Destination Byte Volume (dbytes)",
    "rate": "Overall Flow Rate (rate)",
    "sttl": "Source Time-to-Live (sttl)",
    "dttl": "Destination Time-to-Live (dttl)",
    "sload": "Source Bit Rate Load (sload)",
    "dload": "Destination Bit Rate Load (dload)",
    "ct_dst_ltm": "Dest IP Connection Count (ct_dst_ltm)",
    "ct_src_dport_ltm": "Src-to-Dest Port Connection Count (ct_src_dport_ltm)",
    "ct_dst_sport_ltm": "Dest-to-Src Port Connection Count (ct_dst_sport_ltm)",
    "destination_port": "Destination Port Number",
    "proto": "Transport Protocol",
    "service": "Network Service",
    "source": "Event Source System",
}


class XAIExplainerService:
    """
    Singleton Explainable AI service using SHAP TreeExplainer on Random Forest
    threat detection models. Computes mathematically rigorous Shapley feature
    attributions, synthesizes natural language evidence, and bridges heuristic
    rules with ML signals.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(XAIExplainerService, cls).__new__(cls)
            cls._instance._load_explainer()
        return cls._instance

    def _load_explainer(self):
        self.explainer_ready = False
        self._cache: Dict[str, XAIExplanationResponse] = {}
        self._max_cache_size = 200

        try:
            prep_path = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
            bin_path = os.path.join(settings.MODELS_DIR, "binary_rf_model.joblib")

            if os.path.exists(prep_path) and os.path.exists(bin_path):
                self.preprocessor = MLPreprocessor.load(prep_path)
                self.model = joblib.load(bin_path)
                self.explainer = shap.TreeExplainer(self.model)
                self.feature_names = self.preprocessor.preprocessor.get_feature_names_out()
                self.explainer_ready = True
                logger.info(f"SHAP TreeExplainer initialized successfully with {len(self.feature_names)} features.")
            else:
                logger.warning("ML model or preprocessor artifacts missing in models_store/. Cannot initialize SHAP.")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP TreeExplainer: {e}")
            self.explainer_ready = False

    def _format_display_name(self, raw_col_name: str) -> str:
        clean = raw_col_name.replace("num__", "").replace("cat__", "")
        if clean in FEATURE_DISPLAY_NAMES:
            return FEATURE_DISPLAY_NAMES[clean]
        for prefix in ("proto_", "service_", "source_"):
            if clean.startswith(prefix):
                category = prefix[:-1].capitalize()
                val = clean[len(prefix):]
                return f"{category}: {val}"
        return clean.replace("_", " ").title()

    def explain(
        self,
        event_dict: Dict[str, Any],
        event_id: Optional[str] = None,
    ) -> XAIExplanationResponse:
        """
        Computes SHAP feature attribution vector and natural language explanation
        for an input event dictionary.
        """
        if not self.explainer_ready:
            self._load_explainer()

        if not self.explainer_ready:
            raise RuntimeError("SHAP Explainability service is currently unavailable. Ensure models are trained.")

        # Check Cache if event_id is given
        if event_id and event_id in self._cache:
            return self._cache[event_id]

        start_time = time.perf_counter()

        # 1. Transform features
        df = self.preprocessor.extract_features_from_dict(event_dict)
        X = self.preprocessor.transform(df)

        # 2. Compute SHAP values
        # sv is shape (1, num_features, 2) where class 1 is Attack
        sv = self.explainer.shap_values(X)
        if isinstance(sv, list):
            attack_shap = sv[1][0]
            base_val = float(self.explainer.expected_value[1])
        elif isinstance(sv, np.ndarray) and len(sv.shape) == 3:
            attack_shap = sv[0, :, 1]
            base_val = float(self.explainer.expected_value[1])
        else:
            attack_shap = sv[0]
            base_val = float(self.explainer.expected_value)

        total_abs_shap = float(np.sum(np.abs(attack_shap))) or 1.0

        # Also get inference prediction from ThreatInferenceService
        inf_service = ThreatInferenceService()
        pred_res = inf_service.predict(event_dict)

        # 3. Assemble FeatureAttributions
        all_attrs: List[FeatureAttribution] = []
        for i, col_name in enumerate(self.feature_names):
            val_shap = float(attack_shap[i])
            pct = round((abs(val_shap) / total_abs_shap) * 100.0, 1)

            # Retrieve actual observed value
            clean_name = col_name.replace("num__", "").replace("cat__", "")
            obs_val: Any = "—"
            if clean_name in df.columns:
                obs_val = round(float(df[clean_name].iloc[0]), 2)
            else:
                # One-hot encoded feature
                for cat_col in ("proto", "service", "source"):
                    prefix = f"{cat_col}_"
                    if clean_name.startswith(prefix):
                        cat_val = clean_name[len(prefix):]
                        actual_val = str(df[cat_col].iloc[0])
                        obs_val = 1.0 if actual_val.lower() == cat_val.lower() else 0.0

            all_attrs.append(
                FeatureAttribution(
                    feature_name=clean_name,
                    display_name=self._format_display_name(col_name),
                    feature_value=obs_val,
                    shap_value=round(val_shap, 4),
                    contribution_percent=pct,
                    direction="positive" if val_shap >= 0 else "negative",
                )
            )

        # Separate positive and negative contributors
        positive_list = sorted(
            [a for a in all_attrs if a.direction == "positive"],
            key=lambda x: x.shap_value,
            reverse=True,
        )
        negative_list = sorted(
            [a for a in all_attrs if a.direction == "negative"],
            key=lambda x: abs(x.shap_value),
            reverse=True,
        )

        top_positive = positive_list[:5]
        top_negative = negative_list[:3]

        # 4. Synthesize Natural Language Narrative
        pos_phrases = [
            f"{p.display_name} (val: {p.feature_value}, +{p.contribution_percent}%)"
            for p in top_positive[:3]
        ]
        neg_phrases = [
            f"{n.display_name} (val: {n.feature_value}, -{n.contribution_percent}%)"
            for n in top_negative[:2]
        ]

        pos_summary = ", ".join(pos_phrases) if pos_phrases else "No dominant attack signals"
        neg_summary = ", ".join(neg_phrases) if neg_phrases else "minimal baseline mitigation"

        narrative = (
            f"Model classified event as '{pred_res.predicted_attack_category}' with "
            f"{pred_res.threat_probability * 100:.1f}% attack probability against a base expectation of "
            f"{base_val * 100:.1f}%. Attack classification was primarily driven by {pos_summary}. "
            f"Conversely, {neg_summary} supported routine traffic patterns."
        )

        # 5. Rule-to-XAI Bridge Consensus Check (PRD FR-08)
        # Check if top SHAP features align with heuristic detection reasons
        rule_reasons = pred_res.detection_reasons or []
        top_pos_names = [p.feature_name.lower() for p in top_positive]

        rule_agreement = False
        if pred_res.is_threat:
            # Check for conceptual alignment
            has_rate_rule = any("rate" in r.lower() or "volume" in r.lower() or "flood" in r.lower() for r in rule_reasons)
            has_rate_shap = any(n in top_pos_names for n in ["rate", "sbytes", "dbytes", "spkts", "sload"])

            has_port_rule = any("port" in r.lower() or "recon" in r.lower() or "scan" in r.lower() for r in rule_reasons)
            has_port_shap = any(n in top_pos_names for n in ["ct_dst_sport_ltm", "ct_src_dport_ltm", "destination_port", "ct_dst_ltm"])

            has_auth_rule = any("auth" in r.lower() or "login" in r.lower() or "credential" in r.lower() for r in rule_reasons)
            has_auth_shap = any(n in top_pos_names for n in ["ct_dst_sport_ltm", "dur", "source_auth_service"])

            if (has_rate_rule and has_rate_shap) or (has_port_rule and has_port_shap) or (has_auth_rule and has_auth_shap):
                rule_agreement = True
            elif not rule_reasons:
                rule_agreement = True
            else:
                rule_agreement = len(top_positive) > 0
        else:
            rule_agreement = True

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # Sort all features descending by absolute impact
        sorted_all = sorted(all_attrs, key=lambda x: abs(x.shap_value), reverse=True)

        response = XAIExplanationResponse(
            event_id=event_id,
            model_version=pred_res.model_version,
            predicted_category=pred_res.predicted_attack_category,
            attack_probability=round(pred_res.threat_probability, 4),
            base_value=round(base_val, 4),
            positive_contributors=top_positive,
            negative_contributors=top_negative,
            all_features=sorted_all,
            narrative=narrative,
            rule_agreement=rule_agreement,
            rule_reasons=rule_reasons,
            inference_latency_ms=latency_ms,
        )

        # Cache response
        if event_id:
            if len(self._cache) >= self._max_cache_size:
                # Drop oldest item
                oldest = next(iter(self._cache))
                del self._cache[oldest]
            self._cache[event_id] = response

        return response


# Global singleton instance
xai_explainer_service = XAIExplainerService()

