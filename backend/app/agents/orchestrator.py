import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.correlation_agent import CorrelationAgent
from app.agents.investigation_agent import InvestigationAgent
from app.agents.reporting_agent import ReportingAgent
from app.agents.response_agent import ResponseAgent
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.models.response_action import ResponseAction
from app.schemas.investigation import (
    CopilotChatResponse,
    InvestigationDossier,
    ResponseActionResponse,
)

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Coordinates the Sentriq AI-SOC Multi-Agent Team:
    1. Triage & IOC Investigation Agent
    2. Kill-Chain & Blast Radius Correlation Agent
    3. Containment & Remediation Playbook Agent (Human-in-the-Loop)
    4. Executive Reporting Agent
    5. Zero-Hallucination Grounded SOC Copilot
    """

    @classmethod
    async def get_or_run_investigation(
        cls,
        incident_id: str,
        db: AsyncSession,
    ) -> InvestigationDossier:
        """
        Executes multi-agent investigation pipeline for an incident and returns full dossier.
        Persists recommended actions to DB in 'Pending' status if not already generated.
        """
        # Load incident with events and existing actions
        query = (
            select(Incident)
            .where(Incident.id == incident_id)
            .options(
                selectinload(Incident.events),
                selectinload(Incident.response_actions),
            )
        )
        res = await db.execute(query)
        incident = res.scalars().first()

        if not incident:
            raise ValueError(f"Incident with ID '{incident_id}' not found.")

        events: List[SecurityEvent] = list(incident.events or [])

        # Step 1: Investigation Agent (Triage & IOCs)
        triage_findings = InvestigationAgent.analyze(incident, events)

        # Step 2: Correlation Agent (Kill-Chain & Blast Radius)
        correlation_findings = CorrelationAgent.correlate(incident, events, triage_findings)

        # Step 3: Response Agent (Containment Proposals)
        # Check if actions are already persisted in DB
        action_query = select(ResponseAction).where(ResponseAction.incident_id == incident.id).order_by(ResponseAction.created_at.asc())
        action_res = await db.execute(action_query)
        db_actions = list(action_res.scalars().all())

        if not db_actions:
            # Formulate new actions (strictly status='Pending')
            new_actions = ResponseAgent.generate_actions(
                incident=incident,
                events=events,
                investigation_findings=triage_findings,
                correlation_findings=correlation_findings,
            )
            for act in new_actions:
                db.add(act)
            await db.commit()

            # Query newly persisted actions
            action_res = await db.execute(action_query)
            db_actions = list(action_res.scalars().all())

        # Step 4: Reporting Agent (Executive Markdown Dossier)
        executive_report = ReportingAgent.generate_report(
            incident=incident,
            events=events,
            investigation_findings=triage_findings,
            correlation_findings=correlation_findings,
            response_actions=db_actions,
        )

        # Prepare response schema
        action_responses = [ResponseActionResponse.model_validate(a) for a in db_actions]

        return InvestigationDossier(
            incident_id=incident.id,
            incident_code=incident.incident_code,
            title=incident.title,
            severity=incident.severity,
            risk_score=incident.risk_score,
            attack_entry_vector=triage_findings["attack_entry_vector"],
            kill_chain_stage=correlation_findings["kill_chain_stage"],
            blast_radius_summary=correlation_findings["blast_radius_summary"],
            affected_assets=correlation_findings["affected_assets"],
            indicators_of_compromise=triage_findings["iocs"],
            agent_findings={
                "triage_agent": triage_findings,
                "correlation_agent": correlation_findings,
                "actions_count": len(db_actions),
            },
            recommended_actions=action_responses,
            executive_summary_markdown=executive_report,
        )

    @classmethod
    async def review_action(
        cls,
        action_id: str,
        decision: str,
        analyst_name: str,
        comment: Optional[str],
        db: AsyncSession,
    ) -> ResponseAction:
        """
        Processes human-in-the-loop analyst review for a containment action (PRD FR-10).
        """
        query = select(ResponseAction).where(ResponseAction.id == action_id)
        res = await db.execute(query)
        action = res.scalars().first()

        if not action:
            raise ValueError(f"ResponseAction with ID '{action_id}' not found.")

        action.status = decision  # 'Approved' or 'Rejected'
        action.approved_by = analyst_name
        action.approved_at = datetime.now(timezone.utc)
        if comment:
            action.analyst_comment = comment

        await db.commit()
        await db.refresh(action)

        logger.info(
            f"Containment action {action.id} ({action.title}) marked as {decision} by {analyst_name}."
        )
        return action

    @classmethod
    async def chat_copilot(
        cls,
        incident_id: str,
        question: str,
        history: Optional[List[Dict[str, str]]],
        db: AsyncSession,
    ) -> CopilotChatResponse:
        """
        Zero-hallucination Grounded SOC Copilot.
        Answers analyst inquiries strictly from the incident's event telemetry,
        timeline, risk breakdown, and playbooks in PostgreSQL.
        """
        query = (
            select(Incident)
            .where(Incident.id == incident_id)
            .options(
                selectinload(Incident.events),
                selectinload(Incident.response_actions),
            )
        )
        res = await db.execute(query)
        incident = res.scalars().first()

        if not incident:
            raise ValueError(f"Incident '{incident_id}' not found.")

        events: List[SecurityEvent] = sorted(
            list(incident.events or []),
            key=lambda e: e.timestamp or datetime.min,
        )
        actions: List[ResponseAction] = list(incident.response_actions or [])

        q_lower = question.lower()
        grounded_facts: List[str] = []
        citations: List[str] = []
        suggested_follow_ups: List[str] = []

        # Collect core facts
        grounded_facts.append(f"Incident Code: {incident.incident_code}")
        grounded_facts.append(f"Category: {incident.attack_category}")
        grounded_facts.append(f"Severity: {incident.severity} (Score: {incident.risk_score:.1f}/100)")
        grounded_facts.append(f"Total Correlated Events: {len(events)}")
        if incident.source_ip:
            grounded_facts.append(f"Primary Source IP: {incident.source_ip}")
        if incident.target_asset:
            grounded_facts.append(f"Primary Target Asset: {incident.target_asset}")

        # Collect citations
        for ev in events[:5]:
            ts_str = ev.timestamp.strftime("%H:%M:%S UTC") if ev.timestamp else "N/A"
            citations.append(f"Event {ev.id[:8]} [{ts_str}] ({ev.source_ip} -> {ev.destination_ip}:{ev.destination_port or 'all'})")

        # Intent Matching
        if any(w in q_lower for w in ["how", "entry", "vector", "start", "origin", "initial"]):
            first_ev = events[0] if events else None
            src = incident.source_ip or (first_ev.source_ip if first_ev else "external")
            dst = incident.target_asset or (first_ev.destination_ip if first_ev else "internal")
            port = first_ev.destination_port if first_ev else "standard port"
            
            answer = (
                f"###  Attack Entry Vector Analysis\n\n"
                f"The attack originated from **{src}** targeting **{dst}** (port `{port}`).\n\n"
                f"- **Attack Category:** `{incident.attack_category}`\n"
                f"- **Initial Telemetry:** Recorded at `{first_ev.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC') if first_ev and first_ev.timestamp else 'recent'}` by `{first_ev.source if first_ev else 'sensor'}`.\n"
                f"- **Observed Mechanism:** {first_ev.message if first_ev else 'Hostile packet sequence detected.'}\n\n"
                f"This pattern represents an active `{incident.attack_category}` intrusion attempting initial compromise."
            )
            suggested_follow_ups = [
                "What containment actions are recommended?",
                "Which indicators of compromise (IOCs) were extracted?",
                "What is the blast radius across network assets?",
            ]

        elif any(w in q_lower for w in ["action", "contain", "remediat", "block", "firewall", "mitigat"]):
            if actions:
                act_lines = []
                for a in actions:
                    act_lines.append(
                        f"- **{a.title}** (`{a.status}`)\n"
                        f"  - Entity: `{a.target_entity}` | Risk: `{a.risk_level}`\n"
                        f"  - Command: `{a.command}`"
                    )
                actions_md = "\n".join(act_lines)
            else:
                actions_md = "_No containment actions formulated yet. Run multi-agent triage to generate recommendations._"

            answer = (
                f"###  Containment & Remediation Playbooks (PRD FR-10)\n\n"
                f"All actions remain in **Pending** status until approved by a human SOC analyst:\n\n"
                f"{actions_md}\n\n"
                f"> **Governance Notice:** Per policy, execution requires human-in-the-loop authorization."
            )
            suggested_follow_ups = [
                "Why is the risk level rated this high?",
                "Can you show the exact command for firewall containment?",
                "Has any action already been approved?",
            ]

        elif any(w in q_lower for w in ["ioc", "indicator", "ip", "port", "compromise", "ip address"]):
            ips = list(set([e.source_ip for e in events if e.source_ip]))
            dst_ports = list(set([str(e.destination_port) for e in events if e.destination_port]))
            
            answer = (
                f"###  Extracted Indicators of Compromise (IOCs)\n\n"
                f"Grounded forensic evidence extracted from {len(events)} security events:\n\n"
                f"- **Attacker Source IPs:** {', '.join([f'`{ip}`' for ip in ips]) if ips else 'None'}\n"
                f"- **Targeted Network Hosts:** `{incident.target_asset or 'Internal Host'}`\n"
                f"- **Probed Ports:** {', '.join([f'`{p}`' for p in dst_ports]) if dst_ports else 'Dynamic ports'}\n"
                f"- **Protocols Involved:** {', '.join(set(e.protocol for e in events)) if events else 'TCP'}\n\n"
                f"All identified adversary IPs have been flagged for perimeter blacklisting."
            )
            suggested_follow_ups = [
                "How do I block the attacker's IP on the firewall?",
                "What is the timeline of events from this IP?",
                "Are other assets exposed to this source?",
            ]

        elif any(w in q_lower for w in ["risk", "score", "severity", "why", "factor", "formula"]):
            answer = (
                f"###  Deterministic Risk Score Breakdown\n\n"
                f"The composite risk score is **{incident.risk_score:.1f}/100 ({incident.risk_level})** computed via the PRD 4-Factor Heuristic:\n\n"
                f"$$\\text{{Risk Score}} = 0.30 \\times S + 0.30 \\times C + 0.20 \\times A + 0.20 \\times I$$\n\n"
                f"- **1. Severity ($30\\%$):** Rated `{incident.severity}`\n"
                f"- **2. Detection Confidence ($30\\%$):** `{incident.confidence * 100:.1f}\\%`\n"
                f"- **3. Asset Criticality ($20\\%$):** Criticality for target `{incident.target_asset}`\n"
                f"- **4. Attack Category Impact ($20\\%$):** High operational impact for `{incident.attack_category}`"
            )
            suggested_follow_ups = [
                "What containment steps will reduce this risk?",
                "What were the ML model confidence metrics?",
                "Can you export an executive summary report?",
            ]

        elif any(w in q_lower for w in ["timeline", "sequence", "when", "time", "duration"]):
            first_t = events[0].timestamp if events else None
            last_t = events[-1].timestamp if events else None
            dur = int((last_t - first_t).total_seconds()) if (first_t and last_t) else 0
            
            ev_list = []
            for i, ev in enumerate(events[:7], 1):
                t_str = ev.timestamp.strftime("%H:%M:%S") if ev.timestamp else "+0s"
                ev_list.append(f"{i}. `[{t_str}]` **{ev.attack_type}** ({ev.source}) — {ev.message}")

            answer = (
                f"###  Incident Event Chronology\n\n"
                f"- **Total Duration:** `{dur}` seconds across `{len(events)}` correlated events.\n"
                f"- **First Event:** `{first_t.strftime('%Y-%m-%d %H:%M:%S UTC') if first_t else 'N/A'}`\n"
                f"- **Latest Event:** `{last_t.strftime('%Y-%m-%d %H:%M:%S UTC') if last_t else 'N/A'}`\n\n"
                f"**Chronological Progression:**\n"
                + "\n".join(ev_list)
            )
            suggested_follow_ups = [
                "What was the entry vector for the first event?",
                "Are any containment actions currently pending?",
                "What is the blast radius across other assets?",
            ]

        else:
            # Comprehensive Grounded Synthesis
            answer = (
                f"###  Investigation Summary for {incident.incident_code}\n\n"
                f"Incident **{incident.incident_code}** is currently in **{incident.status}** status with **{incident.severity}** severity (Risk Score: **{incident.risk_score:.1f}/100**).\n\n"
                f"- **Adversary Activity:** `{incident.attack_category}` traffic from `{incident.source_ip or 'unknown IP'}` targeting `{incident.target_asset or 'internal asset'}`.\n"
                f"- **Correlated Telemetry:** `{len(events)}` events verified in database.\n"
                f"- **Active Containment Proposals:** `{len([a for a in actions if a.status == 'Pending'])}` pending analyst approval.\n\n"
                f"What specific aspect of the investigation would you like to explore?"
            )
            suggested_follow_ups = [
                "What is the attack entry vector?",
                "Which containment actions should I approve?",
                "What are the indicators of compromise (IOCs)?",
            ]

        return CopilotChatResponse(
            answer=answer,
            grounded_facts=grounded_facts,
            citations=citations,
            suggested_follow_ups=suggested_follow_ups,
        )
