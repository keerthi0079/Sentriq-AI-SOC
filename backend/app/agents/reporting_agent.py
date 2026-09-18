import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.models.response_action import ResponseAction
from app.schemas.investigation import IOCDetail

logger = logging.getLogger(__name__)


class ReportingAgent:
    """
    Executive Incident Summarizer Agent.
    Synthesizes findings from Triage, Correlation, and Response agents into a polished,
    executive-ready Markdown Incident Dossier for SOC leadership and compliance.
    Follows PRD FR-11.
    """

    NAME = "Sentriq-Reporting-Agent"
    ROLE = "Executive Incident Dossier & Compliance Reporting Specialist"

    @classmethod
    def generate_report(
        cls,
        incident: Incident,
        events: List[SecurityEvent],
        investigation_findings: Dict[str, Any],
        correlation_findings: Dict[str, Any],
        response_actions: List[ResponseAction],
    ) -> str:
        """
        Generates a comprehensive executive markdown dossier for the incident.
        """
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        iocs: List[IOCDetail] = investigation_findings.get("iocs", [])
        entry_vector = investigation_findings.get("attack_entry_vector", "Unknown entry vector")
        kill_chain_stage = correlation_findings.get("kill_chain_stage", "Active Intrusion")
        mitre_tech = correlation_findings.get("mitre_technique_id", "T1059")
        mitre_name = correlation_findings.get("mitre_technique_name", "Command Execution")
        mitre_tactic = correlation_findings.get("mitre_tactic", "Execution")
        blast_radius = correlation_findings.get("blast_radius_summary", "Localized to target asset.")
        affected_assets = correlation_findings.get("affected_assets", [])
        velocity = correlation_findings.get("velocity_events_per_min", 0.0)
        stages_seq = correlation_findings.get("kill_chain_progression", "1. Active Intrusion")

        # Build IOC table
        ioc_rows = []
        for ioc in iocs:
            ioc_rows.append(
                f"| `{ioc.type}` | `{ioc.value}` | **{ioc.reputation}** | {ioc.description} |"
            )
        ioc_table = (
            "| IOC Type | Indicator Value | Classification | Details |\n"
            "|:---|:---|:---|:---|\n"
            + ("\n".join(ioc_rows) if ioc_rows else "| None | N/A | Benign | No external IOCs recorded |")
        )

        # Build Actions table
        action_rows = []
        for act in response_actions:
            badge = f"**{act.status}**"
            if act.status == "Approved":
                badge = " APPROVED"
            elif act.status == "Rejected":
                badge = " REJECTED"
            elif act.status == "Pending":
                badge = " PENDING REVIEW"

            cmd_snippet = f"`{act.command[:45]}...`" if act.command and len(act.command) > 45 else f"`{act.command or 'N/A'}`"
            action_rows.append(
                f"| {act.title} | `{act.target_entity}` | `{act.risk_level}` | {badge} | {cmd_snippet} |"
            )
        action_table = (
            "| Action | Target Entity | Risk Level | Status | Executable Command |\n"
            "|:---|:---|:---|:---|:---|\n"
            + ("\n".join(action_rows) if action_rows else "| No containment actions formulated | - | - | - | - |")
        )

        report = f"""#  Sentriq Autonomous AI-SOC Incident Dossier
**Incident Reference:** `{incident.incident_code}`  
**Report Generated:** {now_str}  
**Investigation Status:** `{incident.status}` | **Severity:** `{incident.severity}` | **Calculated Risk:** `{incident.risk_score:.1f}/100 ({incident.risk_level})`

---

## 1. Executive Summary
On `{incident.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if incident.created_at else "recent timestamp"}`, the Sentriq AI-SOC correlation engine intercepted a confirmed threat sequence classified as **{incident.attack_category}**. 
A total of **{len(events)} correlated security event(s)** were triaged across **{len(affected_assets)} network node(s)** with an attack velocity of **{velocity} events/min**.

- **Primary Entry Vector:** {entry_vector}
- **MITRE ATT&CK Alignment:** {mitre_tactic} ({mitre_tech} - {mitre_name})
- **Blast Radius Assessment:** {blast_radius}

---

## 2. Attack Lifecycle & Kill-Chain Progression
The adversary followed the multi-stage path summarized below:

```mermaid
graph LR
    A["{stages_seq.replace(' -> ', '"] --> B["')}"]
```

- **Observed Kill-Chain Stage:** `{kill_chain_stage}`
- **Progression Sequence:** {stages_seq}
- **Telemetry Sources:** {", ".join(set(e.source for e in events)) if events else "Autonomous Ingestion Hub"}

---

## 3. Indicators of Compromise (IOCs)
Autonomous multi-agent triage extracted the following deterministic forensic indicators:

{ioc_table}

---

## 4. Blast Radius & Network Impact
- **Impacted Assets:** {", ".join([f"`{a}`" for a in affected_assets]) if affected_assets else "`None`"}
- **Blast Radius Tier:** {correlation_findings.get("blast_radius_tier", "Localized")}
- **Operational Impact:** {blast_radius}

---

## 5. Recommended Containment & Remediation Playbooks
*In strict accordance with PRD FR-10, all automated containment measures require explicit human-in-the-loop analyst authorization before execution.*

{action_table}

---

## 6. Post-Incident Hardening Recommendations
1. **Perimeter Hardening:** Enforce ingress drop filters for confirmed malicious subnet origins.
2. **Access Control:** Mandate MFA and rotate all authentication secrets associated with targeted identities.
3. **Segmentation:** Verify microsegmentation boundaries between DMZ web tiers and sensitive database subnets.
4. **Audit & Forensics:** Retain PCAP traces and host forensic snapshots for 90 days in compliance with enterprise retention standards.

---
*Report autonomously compiled by Sentriq AI Multi-Agent SOC Suite.*
"""
        return report.strip()

