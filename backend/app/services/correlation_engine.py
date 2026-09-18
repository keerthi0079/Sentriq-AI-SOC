import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.services.risk_engine import RiskEngine

logger = logging.getLogger(__name__)


class EventCorrelationEngine:
    """
    Groups related security events into unified incidents using a configurable
    sliding time window (default 15 minutes) and deterministic heuristic rules.
    Prevents duplicate alerts and maintains incident timelines.
    Follows PRD Section 14 and FR-06.
    """

    DEFAULT_WINDOW_MINUTES = 15

    @classmethod
    async def correlate_event(
        cls,
        event: SecurityEvent,
        db: AsyncSession,
        window_minutes: int = DEFAULT_WINDOW_MINUTES,
    ) -> Optional[Incident]:
        """
        Correlates a single security event against active incidents.
        If a matching incident exists, appends the event; otherwise creates a new incident.
        """
        # Normal benign events without attack signals are not elevated to security incidents
        if not event.is_attack or event.attack_type == "Normal":
            return None

        window_start = event.timestamp - timedelta(minutes=window_minutes)

        # 1. Search for existing active incident with compatible signature
        # Criteria: Matching source_ip or target_asset, within active lifecycle
        query = (
            select(Incident)
            .where(
                Incident.status.in_(["Open", "Investigating"]),
                (Incident.source_ip == event.source_ip) | (Incident.target_asset == event.destination_ip),
                Incident.created_at >= window_start,
            )
            .order_by(Incident.created_at.desc())
        )
        result = await db.execute(query)
        incident = result.scalars().first()

        severity_rank = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

        if incident:
            # Append event to existing incident
            event.incident_id = incident.id
            incident.event_count += 1

            # Escalate severity if incoming event is higher severity
            if severity_rank.get(event.severity, 1) > severity_rank.get(incident.severity, 1):
                incident.severity = event.severity

            # Escalate attack category if sequence escalates to Exploitation
            if event.attack_type == "Exploitation" and incident.attack_category != "Exploitation":
                incident.attack_category = "Exploitation"
                incident.title = f"Multi-Stage Attack: {incident.attack_category} escalated to Exploitation"

            # Recompute Risk Score using highest factor parameters
            risk_calc = RiskEngine.calculate_risk(
                severity=incident.severity,
                confidence=incident.confidence,
                attack_category=incident.attack_category,
                asset_identifier=incident.target_asset,
            )
            incident.risk_score = risk_calc["risk_score"]
            incident.risk_level = risk_calc["risk_level"]

            logger.info(f"Appended event {event.id} to existing incident {incident.incident_code}")
            return incident
        else:
            # Create new unified Incident
            count_q = await db.execute(select(func.count(Incident.id)))
            count = (count_q.scalar() or 0) + 1
            incident_code = f"INC-2026-{count:04d}"

            title = cls._generate_incident_title(event)
            description = (
                f"Automated incident triggered by {event.source} detecting {event.attack_type} "
                f"activity from {event.source_ip} directed at {event.destination_ip}."
            )

            risk_calc = RiskEngine.calculate_risk(
                severity=event.severity,
                confidence=0.92,
                attack_category=event.attack_type,
                asset_identifier=event.destination_ip,
            )

            new_incident = Incident(
                id=str(uuid.uuid4()),
                incident_code=incident_code,
                title=title,
                description=description,
                attack_category=event.attack_type,
                severity=event.severity,
                risk_score=risk_calc["risk_score"],
                risk_level=risk_calc["risk_level"],
                confidence=0.92,
                status="Open",
                source_ip=event.source_ip,
                target_asset=event.destination_ip,
                event_count=1,
                notes=f"[System]: Correlated from initial event {event.id} ({event.event_type}).",
                created_at=event.timestamp,
            )
            db.add(new_incident)
            await db.flush()

            event.incident_id = new_incident.id
            logger.info(f"Created new incident {incident_code} for attack {event.attack_type}")
            return new_incident

    @classmethod
    async def correlate_unassigned_events(cls, db: AsyncSession) -> int:
        """Finds all unassigned malicious events and runs correlation pipeline."""
        query = (
            select(SecurityEvent)
            .where(
                SecurityEvent.incident_id.is_(None),
                SecurityEvent.is_attack == True,
                SecurityEvent.attack_type != "Normal",
            )
            .order_by(SecurityEvent.timestamp.asc())
        )
        result = await db.execute(query)
        unassigned_events = result.scalars().all()

        correlated_count = 0
        for ev in unassigned_events:
            inc = await cls.correlate_event(ev, db)
            if inc:
                correlated_count += 1

        await db.commit()
        return correlated_count

    @classmethod
    def _generate_incident_title(cls, event: SecurityEvent) -> str:
        cat = event.attack_type
        if cat == "Brute Force":
            return f"Authentication Abuse Sequence (Brute Force from {event.source_ip})"
        elif cat == "DoS":
            return f"Volumetric Traffic Disruption ({event.protocol} Flood targeting {event.destination_ip})"
        elif cat == "Port Scan":
            return f"Perimeter Reconnaissance Probe (Port Scan from {event.source_ip})"
        elif cat == "Exploitation":
            return f"Host Exploitation Attempt (Targeting {event.destination_ip})"
        elif cat == "Web Attack":
            return f"Application Layer Attack on {event.destination_ip}"
        else:
            return f"Anomalous Threat Sequence: {cat} from {event.source_ip}"

