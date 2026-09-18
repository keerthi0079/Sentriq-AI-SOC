import os
from typing import Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.core.config import settings

NUMERIC_FEATURES = [
    "dur",
    "spkts",
    "dpkts",
    "sbytes",
    "dbytes",
    "rate",
    "sttl",
    "dttl",
    "sload",
    "dload",
    "ct_dst_ltm",
    "ct_src_dport_ltm",
    "ct_dst_sport_ltm",
    "destination_port",
]

CATEGORICAL_FEATURES = [
    "proto",
    "service",
    "source",
]

ALL_FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


class MLPreprocessor:
    """
    Standardizes numeric features using StandardScaler and encodes categorical
    security-event fields using OneHotEncoder with handle_unknown='ignore'.
    """

    def __init__(self):
        self.preprocessor = ColumnTransformer(
            transformers=[
                (
                    "num",
                    StandardScaler(),
                    NUMERIC_FEATURES,
                ),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    CATEGORICAL_FEATURES,
                ),
            ],
            remainder="drop",
        )
        self.is_fitted = False

    def extract_features_from_dict(self, event_dict: Dict) -> pd.DataFrame:
        """Flattens an event payload or raw_features into a standardized DataFrame."""
        row = {}
        raw = event_dict.get("raw_features") or {}

        # Numeric extraction with safe defaults
        for col in NUMERIC_FEATURES:
            val = raw.get(col)
            if val is None:
                val = event_dict.get(col, 0)
            try:
                row[col] = float(val)
            except (ValueError, TypeError):
                row[col] = 0.0

        # Categorical extraction
        row["proto"] = str(raw.get("proto") or event_dict.get("protocol") or "TCP").upper()
        row["service"] = str(raw.get("service") or event_dict.get("service") or "other").lower()
        row["source"] = str(event_dict.get("source") or "auth_service").lower()

        return pd.DataFrame([row])

    def fit(self, df: pd.DataFrame) -> "MLPreprocessor":
        """Fits the scaler and one-hot encoder on the training dataframe."""
        clean_df = self._ensure_columns(df)
        self.preprocessor.fit(clean_df)
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transforms features using the fitted preprocessor."""
        if not self.is_fitted:
            raise ValueError("MLPreprocessor must be fitted before calling transform().")
        clean_df = self._ensure_columns(df)
        return self.preprocessor.transform(clean_df)

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        """Fits and transforms training features."""
        clean_df = self._ensure_columns(df)
        transformed = self.preprocessor.fit_transform(clean_df)
        self.is_fitted = True
        return transformed

    def _ensure_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensures all expected feature columns exist with valid types."""
        out_df = df.copy()
        for col in NUMERIC_FEATURES:
            if col not in out_df.columns:
                out_df[col] = 0.0
            out_df[col] = pd.to_numeric(out_df[col], errors="coerce").fillna(0.0)

        for col in CATEGORICAL_FEATURES:
            if col not in out_df.columns:
                out_df[col] = "unknown"
            out_df[col] = out_df[col].astype(str).fillna("unknown")

        return out_df[ALL_FEATURE_COLUMNS]

    def save(self, filepath: str = None) -> str:
        """Serializes the fitted preprocessor to disk."""
        if not filepath:
            os.makedirs(settings.MODELS_DIR, exist_ok=True)
            filepath = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
        joblib.dump(self, filepath)
        return filepath

    @classmethod
    def load(cls, filepath: str = None) -> "MLPreprocessor":
        """Loads a serialized preprocessor from disk."""
        if not filepath:
            filepath = os.path.join(settings.MODELS_DIR, "preprocessor.joblib")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Preprocessor artifact not found at {filepath}")
        return joblib.load(filepath)

