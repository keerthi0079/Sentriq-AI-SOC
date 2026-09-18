from typing import Any, Dict, Tuple


class RiskEngine:
    """
    Implements the deterministic, transparent 4-factor risk scoring engine
    defined in PRD Section 13 and FR-05.
    Formula: Total Risk = (Severity * 0.3) + (ML_Confidence * 0.3) + (Asset_Importance * 0.2) + (Attack_Impact * 0.2)
    """

    SEVERITY_SCORES = {
        "Low": 20.0,
        "Medium": 50.0,
        "High": 75.0,
        "Critical": 100.0,
    }

    ATTACK_IMPACT_SCORES = {
        "Exploitation": 95.0,
        "DoS": 80.0,
        "Web Attack": 75.0,
        "Brute Force": 65.0,
        "Port Scan": 40.0,
        "Reconnaissance": 40.0,
        "Normal": 0.0,
    }

    ASSET_IMPORTANCE_REGISTRY = {
        "domain-controller": 95.0,
        "core-database": 95.0,
        "database": 90.0,
        "auth-portal.sentriq.local": 85.0,
        "auth_service": 85.0,
        "api-gateway.sentriq.local": 75.0,
        "api_gateway": 75.0,
        "dmz-firewall.sentriq.local": 70.0,
        "perimeter_firewall": 70.0,
        "web_server": 65.0,
        "internal-workstation": 40.0,
        "guest-wifi": 20.0,
    }

    @classmethod
    def get_asset_importance(cls, asset_identifier: str = None) -> float:
        """Looks up asset criticality in registry with default fallback."""
        if not asset_identifier:
            return 50.0
        ident_lower = asset_identifier.lower()
        for key, score in cls.ASSET_IMPORTANCE_REGISTRY.items():
            if key in ident_lower:
                return score
        return 50.0

    @classmethod
    def calculate_risk(
        cls,
        severity: str,
        confidence: float,
        attack_category: str,
        asset_identifier: str = None,
    ) -> Dict[str, Any]:
        """Calculates deterministic risk score, factor breakdown, level, and explanation."""
        # 1. Severity Factor (30%)
        sev_score = cls.SEVERITY_SCORES.get(severity, 50.0)
        sev_contrib = sev_score * 0.30

        # 2. ML Confidence Factor (30%)
        # Ensure confidence is 0-100 scale
        conf_scaled = (confidence * 100.0) if confidence <= 1.0 else confidence
        conf_scaled = max(0.0, min(100.0, conf_scaled))
        conf_contrib = conf_scaled * 0.30

        # 3. Asset Importance Factor (20%)
        asset_score = cls.get_asset_importance(asset_identifier)
        asset_contrib = asset_score * 0.20

        # 4. Attack Impact Factor (20%)
        impact_score = cls.ATTACK_IMPACT_SCORES.get(attack_category, 50.0)
        impact_contrib = impact_score * 0.20

        # Total Risk Score (0 - 100)
        total_risk = round(sev_contrib + conf_contrib + asset_contrib + impact_contrib, 1)
        total_risk = max(0.0, min(100.0, total_risk))

        # Risk Level Mapping (PRD 13.4)
        if total_risk >= 80.0:
            risk_level = "Critical"
        elif total_risk >= 60.0:
            risk_level = "High"
        elif total_risk >= 30.0:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Narrative Explanation (PRD 13.5)
        explanation = cls._generate_explanation(
            total_risk,
            risk_level,
            severity,
            sev_contrib,
            conf_scaled,
            conf_contrib,
            asset_identifier,
            asset_score,
            asset_contrib,
            attack_category,
            impact_contrib,
        )

        return {
            "risk_score": total_risk,
            "risk_level": risk_level,
            "factors": {
                "severity": {
                    "value": severity,
                    "score": sev_score,
                    "weight": 0.30,
                    "contribution": round(sev_contrib, 1),
                },
                "confidence": {
                    "value": round(conf_scaled, 1),
                    "score": round(conf_scaled, 1),
                    "weight": 0.30,
                    "contribution": round(conf_contrib, 1),
                },
                "asset_importance": {
                    "asset": asset_identifier or "Generic Asset",
                    "score": asset_score,
                    "weight": 0.20,
                    "contribution": round(asset_contrib, 1),
                },
                "attack_impact": {
                    "category": attack_category,
                    "score": impact_score,
                    "weight": 0.20,
                    "contribution": round(impact_contrib, 1),
                },
            },
            "explanation": explanation,
        }

    @classmethod
    def _generate_explanation(
        cls,
        total: float,
        level: str,
        severity: str,
        sev_c: float,
        conf_val: float,
        conf_c: float,
        asset_id: str,
        asset_score: float,
        asset_c: float,
        category: str,
        impact_c: float,
    ) -> str:
        asset_label = asset_id if asset_id else "infrastructure asset"
        return (
            f"Overall risk calculated at {total}/100 ({level}). Primary drivers: "
            f"{severity} event severity (+{sev_c:.1f}), {conf_val:.0f}% ML threat confidence (+{conf_c:.1f}), "
            f"criticality of '{asset_label}' (score {asset_score:.0f}, +{asset_c:.1f}), and "
            f"inherent severity impact of {category} (+{impact_c:.1f})."
        )

