import json
import os
from datetime import datetime, timezone
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from app.core.config import settings
from app.ml.evaluate import compute_classification_metrics
from app.ml.preprocessing import ALL_FEATURE_COLUMNS, MLPreprocessor
from app.services.benchmark_loader import BenchmarkLoader
from app.services.data_generator import SecurityDataGenerator


def assemble_training_dataset() -> pd.DataFrame:
    """
    Compiles a comprehensive training dataset combining authentic UNSW-NB15
    benchmark samples with representative scenario traffic.
    """
    rows = []

    # 1. Load UNSW-NB15 benchmark records
    benchmark_events = BenchmarkLoader.load_unsw_sample()
    for ev in benchmark_events:
        raw = ev.raw_features or {}
        raw["source"] = ev.source
        raw["protocol"] = ev.protocol
        raw["destination_port"] = ev.destination_port
        raw["is_attack"] = 1 if ev.is_attack else 0
        raw["attack_type"] = ev.attack_type
        rows.append(raw)

    # 2. Add Brute Force scenario variations
    for _ in range(3):
        bf_events = SecurityDataGenerator.generate_brute_force_scenario(fail_count=8)
        for ev in bf_events:
            raw = ev.raw_features or {}
            raw["source"] = ev.source
            raw["protocol"] = ev.protocol
            raw["destination_port"] = ev.destination_port
            raw["is_attack"] = 1
            raw["attack_type"] = ev.attack_type
            rows.append(raw)

    # 3. Add DoS burst variations
    for _ in range(4):
        dos_events = SecurityDataGenerator.generate_dos_scenario(packet_burst=6)
        for ev in dos_events:
            raw = ev.raw_features or {}
            raw["source"] = ev.source
            raw["protocol"] = ev.protocol
            raw["destination_port"] = ev.destination_port
            raw["is_attack"] = 1
            raw["attack_type"] = "DoS"
            rows.append(raw)

    # 4. Add Port Scan variations
    for _ in range(3):
        scan_events = SecurityDataGenerator.generate_port_scan_scenario()
        for ev in scan_events:
            raw = ev.raw_features or {}
            raw["source"] = ev.source
            raw["protocol"] = ev.protocol
            raw["destination_port"] = ev.destination_port
            raw["is_attack"] = 1
            raw["attack_type"] = "Port Scan"
            rows.append(raw)

    # 5. Add Benign flows for balance
    for _ in range(45):
        benign = SecurityDataGenerator.generate_benign_event()
        raw = benign.raw_features or {}
        raw["source"] = benign.source
        raw["protocol"] = benign.protocol
        raw["destination_port"] = benign.destination_port
        raw["is_attack"] = 0
        raw["attack_type"] = "Normal"
        rows.append(raw)

    df = pd.DataFrame(rows)
    # Normalize attack categories
    df["attack_type"] = df["attack_type"].replace({"Reconnaissance": "Port Scan", "Backdoors": "Exploitation"})
    return df


def train_models():
    """Trains, evaluates, and serializes the binary and multi-class models."""
    print("[*] Assembling Sentriq ML training corpus...")
    df = assemble_training_dataset()
    print(f"[+] Total training records assembled: {len(df)}")
    print(f"[+] Class distribution:\n{df['attack_type'].value_counts()}\n")

    os.makedirs(settings.MODELS_DIR, exist_ok=True)

    # 1. Feature Preprocessing
    preprocessor = MLPreprocessor()
    X = preprocessor.fit_transform(df)
    y_binary = df["is_attack"].astype(int).values
    y_multiclass = df["attack_type"].astype(str).values

    # Save Preprocessor
    prep_path = preprocessor.save(os.path.join(settings.MODELS_DIR, "preprocessor.joblib"))
    print(f"[+] Preprocessor saved to {prep_path}")

    # 2. Train-Test Split (80/20 Stratified)
    X_train, X_test, y_bin_train, y_bin_test, y_mc_train, y_mc_test = train_test_split(
        X, y_binary, y_multiclass, test_size=0.20, random_state=42, stratify=y_binary
    )

    # 3. Model 1: Binary Classifier (Normal vs Attack)
    print("[*] Training Binary Threat Classifier (Random Forest)...")
    binary_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        class_weight="balanced",
    )
    binary_model.fit(X_train, y_bin_train)
    y_bin_pred = binary_model.predict(X_test)
    bin_metrics = compute_classification_metrics(
        y_bin_test, y_bin_pred, labels=[0, 1], is_binary=True
    )
    bin_path = os.path.join(settings.MODELS_DIR, "binary_rf_model.joblib")
    joblib.dump(binary_model, bin_path)
    print(f"[+] Binary Model Accuracy: {bin_metrics['accuracy']:.4f}, F1: {bin_metrics['f1_weighted']:.4f}")
    print(f"[+] Saved to {bin_path}")

    # 4. Model 2: Multi-Class Attack Classifier
    print("\n[*] Training Multi-Class Attack Classifier (Random Forest)...")
    mc_classes = sorted(list(set(y_multiclass)))
    mc_model = RandomForestClassifier(
        n_estimators=120,
        max_depth=20,
        random_state=42,
        class_weight="balanced",
    )
    mc_model.fit(X_train, y_mc_train)
    y_mc_pred = mc_model.predict(X_test)
    mc_metrics = compute_classification_metrics(
        y_mc_test, y_mc_pred, labels=mc_classes, is_binary=False
    )
    mc_path = os.path.join(settings.MODELS_DIR, "multiclass_rf_model.joblib")
    joblib.dump(mc_model, mc_path)
    print(f"[+] Multi-Class Model Accuracy: {mc_metrics['accuracy']:.4f}, Macro F1: {mc_metrics['f1_macro']:.4f}")
    print(f"[+] Supported Attack Classes: {mc_classes}")
    print(f"[+] Saved to {mc_path}")

    # 5. Metadata & Reports
    metadata = {
        "model_version": "1.0.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "RandomForestClassifier",
        "features": ALL_FEATURE_COLUMNS,
        "classes": mc_classes,
        "dataset_sample_size": len(df),
        "dataset_provenance": "UNSW-NB15 Benchmark Samples & PRD Sec 12 Scenario Telemetry",
        "metrics_summary": {
            "binary_accuracy": bin_metrics["accuracy"],
            "binary_f1": bin_metrics["f1_weighted"],
            "binary_fpr": bin_metrics["false_positive_rate"],
            "multiclass_accuracy": mc_metrics["accuracy"],
            "multiclass_macro_f1": mc_metrics["f1_macro"],
        },
    }
    with open(os.path.join(settings.MODELS_DIR, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    evaluation_report = {
        "binary_classification": bin_metrics,
        "multiclass_classification": mc_metrics,
    }
    with open(os.path.join(settings.MODELS_DIR, "evaluation_report.json"), "w") as f:
        json.dump(evaluation_report, f, indent=2)

    print("\n[+] Metadata and Evaluation Reports written successfully.")
    print("==============================================================")
    print("      SENTRIQ ML THREAT DETECTION MODELS READY               ")
    print("==============================================================")


if __name__ == "__main__":
    train_models()

