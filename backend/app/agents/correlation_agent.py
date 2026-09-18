import logging
from datetime import datetime
from typing import Any, Dict, List
from app.models.event import SecurityEvent
from app.models.incident import Incident

logger = logging.getLogger(__name__)


class CorrelationAgent:
    """
    Kill-Chain & Blast Radius Correlation Agent.
    Maps attack progression across the MITRE ATT&CK lifecycle, assesses blast radius
    across network assets, and tracks threat escalation.
    """

    NAME = "Sentriq-Correlation-Agent"
    ROLE = "Kill-Chain Progression & Blast Radius Specialist"

    MITRE_MAPPING = {
        "Port Scan": {
            "stage": "Reconnaissance",
            "technique_id": "T1595",
            "technique_name": "Active Scanning",
            "tactic": "TA0043 - Reconnaissance",
        },
        "Brute Force": {
            "stage": "Initial Access & Credential Access",
            "technique_id": "T1110",
            "technique_name": "Brute Force / Password Guessing",
            "tactic": "TA0006 - Credential Access",
        },
        "DoS": {
            "stage": "Impact",
            "technique_id": "T1498",
            "technique_name": "Network Denial of Service",
            "tactic": "TA0040 - Impact",
        },
        "Exploitation": {
            "stage": "Execution & Defense Evasion",
            "technique_id": "T1203",
            "technique_name": "Exploitation for Client/Server Execution",
            "tactic": "TA0002 - Execution",
        },
        "Web Attack": {
            "stage": "Initial Access",
            "technique_id": "T1190",
            "technique_name": "Exploit Public-Facing Application",
            "tactic": "TA0001 - Initial Access",
        },
        "Normal": {
            "stage": "Benign Telemetry",
            "technique_id": "N/A",
            "technique_name": "Standard Operational Baseline",
            "tactic": "None",
        },
    }

    @classmethod
    def correlate(
        cls,
        incident: Incident,
        events: List[SecurityEvent],
        investigation_finding: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluates kill-chain progression and computes blast radius across network assets.
        """
        # 1. Distinct target assets (blast radius)
        affected_assets = list(
            set(
                [ev.destination_ip for ev in events if ev.destination_ip]
                + ([incident.target_asset] if incident.target_asset else [])
            )
        )

        # 2. MITRE ATT&CK Mapping
        mitre_info = cls.MITRE_MAPPING.get(
            incident.attack_category,
            {
                "stage": "Anomalous Execution",
                "technique_id": "T1059",
                "technique_name": "Command and Scripting Interpreter",
                "tactic": "TA0002 - Execution",
            },
        )

        # 3. Calculate attack duration and velocity
        duration_seconds = 0
        velocity_events_per_min = 0.0

        sorted_events = sorted(events, key=lambda e: e.timestamp or datetime.min)
        if len(sorted_events) >= 2:
            start_t = sorted_events[0].timestamp
            end_t = sorted_events[-1].timestamp
            if start_t and end_t:
                duration_seconds = max(1, int((end_t - start_t).total_seconds()))
                velocity_events_per_min = round((len(sorted_events) / (duration_seconds / 60.0)), 2)
        elif len(sorted_events) == 1:
            velocity_events_per_min = 1.0

        # 4. Blast Radius Assessment
        asset_count = len(affected_assets)
        if asset_count > 3:
            blast_severity = "Wide Subnet Exposure (High Blast Radius)"
            blast_desc = (
                f"Incident impacts {asset_count} network nodes ({', '.join(affected_assets[:3])} + {asset_count - 3} others). "
                f"Elevated risk of lateral movement across enterprise segments."
            )
        elif asset_count > 1:
            blast_severity = "Multi-Host Cluster (Moderate Blast Radius)"
            blast_desc = (
                f"Hostile activity confirmed against {asset_count} internal hosts ({', '.join(affected_assets)}). "
                f"Adversary attempting pivot across local network boundary."
            )
        else:
            target_str = affected_assets[0] if affected_assets else "target host"
            blast_severity = "Targeted Single-Host (Localized Blast Radius)"
            blast_desc = (
                f"Activity currently localized to single host {target_str}. "
                f"No confirmed east-west lateral spread detected at this time."
            )

        # 5. Kill-chain stage progression sequence
        stages_detected = []
        # Check event types present
        attack_types_present = set(e.attack_type for e in events)
        if "Port Scan" in attack_types_present:
            stages_detected.append("1. Reconnaissance (Port Scan)")
        if "Brute Force" in attack_types_present or "Web Attack" in attack_types_present:
            stages_detected.append("2. Initial Access / Credential Probing")
        if "Exploitation" in attack_types_present:
            stages_detected.append("3. Execution & Defense Evasion")
        if "DoS" in attack_types_present:
            stages_detected.append("4. Service Disruption & Impact")

        if not stages_detected:
            stages_detected.append(f"1. Active {mitre_info['stage']}")

        kill_chain_summary = " -> ".join(stages_detected)

        summary = (
            f"Evaluated kill-chain stage as '{mitre_info['stage']}' ({mitre_info['technique_id']}). "
            f"Blast radius: {blast_severity}. Velocity: {velocity_events_per_min} events/min across {asset_count} asset(s)."
        )

        return {
            "agent_name": cls.NAME,
            "role": cls.ROLE,
            "summary": summary,
            "confidence": 0.91,
            "kill_chain_stage": mitre_info["stage"],
            "mitre_technique_id": mitre_info["technique_id"],
            "mitre_technique_name": mitre_info["technique_name"],
            "mitre_tactic": mitre_info["tactic"],
            "blast_radius_summary": blast_desc,
            "blast_radius_tier": blast_severity,
            "affected_assets": affected_assets,
            "asset_count": asset_count,
            "duration_seconds": duration_seconds,
            "velocity_events_per_min": velocity_events_per_min,
            "kill_chain_stages_sequence": stages_detected,
            "kill_chain_progression": kill_chain_summary,
        }

