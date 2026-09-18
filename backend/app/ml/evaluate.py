from typing import Any, Dict, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def compute_classification_metrics(
    y_true: List[Any],
    y_pred: List[Any],
    labels: List[str] = None,
    is_binary: bool = False,
) -> Dict[str, Any]:
    """Computes comprehensive metrics following PRD Section 21."""
    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    prec_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    fpr = 0.0
    if is_binary and len(cm) == 2:
        # Binary confusion matrix: [[TN, FP], [FN, TP]]
        tn, fp = cm[0][0], cm[0][1]
        denom = fp + tn
        fpr = float(fp / denom) if denom > 0 else 0.0

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    return {
        "accuracy": round(acc, 4),
        "precision_macro": round(prec_macro, 4),
        "precision_weighted": round(prec_weighted, 4),
        "recall_macro": round(rec_macro, 4),
        "recall_weighted": round(rec_weighted, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "false_positive_rate": round(fpr, 4),
        "confusion_matrix": cm,
        "labels": labels,
        "detailed_report": report,
    }

