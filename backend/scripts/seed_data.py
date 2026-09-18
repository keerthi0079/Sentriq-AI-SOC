import asyncio
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.models.incident import Incident
from app.models.event import SecurityEvent


async def seed():
    print("Initializing tables...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Incident))
        if result.scalars().first():
            print("Database already contains incidents. Skipping seed.")
            return

        print("Seeding initial demonstration incidents and security events...")
        now = datetime.now(timezone.utc)

        inc1 = Incident(
            id=str(uuid.uuid4()),
            incident_code="INC-2026-0001",
            title="Credential Compromise Sequence (SSH Brute Force)",
            description="Repeated failed SSH authentications from external IP 198.51.100.45 followed by successful root session escalation.",
            attack_category="Brute Force",
            severity="Critical",
            risk_score=85.0,
            risk_level="Critical",
            confidence=0.96,
            status="Investigating",
            source_ip="198.51.100.45",
            target_asset="auth-portal.sentriq.local",
            event_count=8,
            notes="Analyst investigating anomalous login from foreign ASN.",
            created_at=now - timedelta(minutes=25),
        )

        inc2 = Incident(
            id=str(uuid.uuid4()),
            incident_code="INC-2026-0002",
            title="Volumetric SYN Flood Traffic Spike",
            description="High packet rate SYN burst targeting public API gateway, exceeding baseline threshold by 450%.",
            attack_category="DoS",
            severity="High",
            risk_score=74.5,
            risk_level="High",
            confidence=0.91,
            status="Open",
            source_ip="203.0.113.88",
            target_asset="api-gateway.sentriq.local",
            event_count=14,
            notes="Automatic rate-limiting triggered at edge load balancer.",
            created_at=now - timedelta(hours=1, minutes=10),
        )

        inc3 = Incident(
            id=str(uuid.uuid4()),
            incident_code="INC-2026-0003",
            title="Sequential Port Reconnaissance Probe",
            description="Scanning ports 21, 22, 23, 80, 443, 3389, 8080 within 12 seconds across DMZ perimeter subnet.",
            attack_category="Port Scan",
            severity="Medium",
            risk_score=48.0,
            risk_level="Medium",
            confidence=0.88,
            status="Resolved",
            source_ip="192.0.2.144",
            target_asset="dmz-firewall.sentriq.local",
            event_count=7,
            notes="Source IP dropped by perimeter firewall rule FW-DENY-SCAN.",
            created_at=now - timedelta(hours=3),
        )

        session.add_all([inc1, inc2, inc3])

        # Add sample events
        for i in range(5):
            event = SecurityEvent(
                id=str(uuid.uuid4()),
                timestamp=now - timedelta(minutes=25 - i * 2),
                source="auth_service",
                event_type="failed_login",
                source_ip="198.51.100.45",
                destination_ip="10.0.1.50",
                source_port=49152 + i,
                destination_port=22,
                protocol="TCP",
                user_identity="root",
                attack_type="Brute Force",
                severity="High",
                message=f"[SIMULATED DEMO DATA] Failed SSH authentication attempt {i+1} for user root from 198.51.100.45",
                is_attack=True,
                is_simulated=True,
                incident_id=inc1.id,
            )
            session.add(event)

        await session.commit()
        print("Initial demo data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())

