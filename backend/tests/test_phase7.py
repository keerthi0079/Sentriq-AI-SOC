import pytest
import uuid
from datetime import datetime, timezone
from app.core.database import AsyncSessionLocal
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.models.response_action import ResponseAction
from app.agents.orchestrator import MultiAgentOrchestrator
from app.services.data_generator import SecurityDataGenerator


async def create_sample_incident():
    """Seeds an incident with correlated attack events."""
    incident_id = str(uuid.uuid4())
    inc = Incident(
        id=incident_id,
        incident_code=f"INC-{uuid.uuid4().hex[:6].upper()}",
        title="Authentication Abuse Sequence (Brute Force from 192.168.1.150)",
        description="Correlated brute force security events targeting SSH gateway.",
        attack_category="Brute Force",
        severity="High",
        risk_score=82.5,
        risk_level="High",
        confidence=0.95,
        status="Open",
        source_ip="192.168.1.150",
        target_asset="10.0.0.25",
        event_count=3,
        created_at=datetime.now(timezone.utc),
    )

    ev1 = SecurityEvent(
        id=str(uuid.uuid4()),
        incident_id=incident_id,
        source="auth_service",
        event_type="failed_login",
        source_ip="192.168.1.150",
        destination_ip="10.0.0.25",
        destination_port=22,
        protocol="TCP",
        user_identity="admin",
        attack_type="Brute Force",
        severity="High",
        message="Failed password for admin from 192.168.1.150 port 54321 ssh2",
        is_attack=True,
        is_simulated=True,
    )
    ev2 = SecurityEvent(
        id=str(uuid.uuid4()),
        incident_id=incident_id,
        source="auth_service",
        event_type="failed_login",
        source_ip="192.168.1.150",
        destination_ip="10.0.0.25",
        destination_port=22,
        protocol="TCP",
        user_identity="root",
        attack_type="Brute Force",
        severity="High",
        message="Failed password for root from 192.168.1.150 port 54322 ssh2",
        is_attack=True,
        is_simulated=True,
    )

    async with AsyncSessionLocal() as session:
        session.add(inc)
        session.add(ev1)
        session.add(ev2)
        await session.commit()
        await session.refresh(inc)

    return inc


@pytest.mark.asyncio
async def test_multiagent_investigation_pipeline(async_client):
    """Verifies that the multi-agent pipeline extracts IOCs, calculates blast radius, and formulates actions."""
    inc = await create_sample_incident()
    async with AsyncSessionLocal() as session:
        dossier = await MultiAgentOrchestrator.get_or_run_investigation(inc.id, session)

    assert dossier is not None
    assert dossier.incident_id == inc.id
    assert dossier.incident_code == inc.incident_code
    assert "Brute" in dossier.attack_entry_vector or "SSH" in dossier.attack_entry_vector
    assert dossier.kill_chain_stage is not None
    assert len(dossier.indicators_of_compromise) > 0

    # Verify at least one IOC is the adversary IP
    ioc_values = [i.value for i in dossier.indicators_of_compromise]
    assert "192.168.1.150" in ioc_values
    assert "22" in ioc_values

    # Verify PRD FR-10: Actions are initially Pending
    assert len(dossier.recommended_actions) > 0
    for act in dossier.recommended_actions:
        assert act.status == "Pending"
        assert act.risk_level in ["Low", "Medium", "High"]
        assert act.command is not None

    # Verify PRD FR-11: Executive report markdown
    assert "#  Sentriq Autonomous AI-SOC Incident Dossier" in dossier.executive_summary_markdown
    assert inc.incident_code in dossier.executive_summary_markdown


@pytest.mark.asyncio
async def test_human_in_the_loop_approval(async_client):
    """Verifies PRD FR-10: analyst can Approve or Reject a containment action."""
    inc = await create_sample_incident()
    async with AsyncSessionLocal() as session:
        dossier = await MultiAgentOrchestrator.get_or_run_investigation(inc.id, session)
        action_to_review = dossier.recommended_actions[0]

        # 1. Approve action
        updated = await MultiAgentOrchestrator.review_action(
            action_id=action_to_review.id,
            decision="Approved",
            analyst_name="Tier-2 SOC Lead",
            comment="Approved ingress drop filter after verifying source IP reputation.",
            db=session,
        )
        assert updated.status == "Approved"
        assert updated.approved_by == "Tier-2 SOC Lead"
        assert updated.approved_at is not None
        assert "verifying" in updated.analyst_comment

        # 2. Reject another action if available
        if len(dossier.recommended_actions) > 1:
            action_to_reject = dossier.recommended_actions[1]
            rejected = await MultiAgentOrchestrator.review_action(
                action_id=action_to_reject.id,
                decision="Rejected",
                analyst_name="Tier-2 SOC Lead",
                comment="Rejecting service isolation to avoid customer downtime.",
                db=session,
            )
            assert rejected.status == "Rejected"
            assert rejected.approved_by == "Tier-2 SOC Lead"


@pytest.mark.asyncio
async def test_grounded_copilot_chat(async_client):
    """Verifies PRD FR-09: Copilot answers with zero hallucination and grounded facts."""
    inc = await create_sample_incident()
    async with AsyncSessionLocal() as session:
        # Question 1: Attack entry vector
        resp1 = await MultiAgentOrchestrator.chat_copilot(
            incident_id=inc.id,
            question="How did the attacker enter the system?",
            history=None,
            db=session,
        )
        assert resp1.answer is not None
        assert "192.168.1.150" in resp1.answer or "Entry Vector" in resp1.answer
        assert len(resp1.grounded_facts) > 0
        assert len(resp1.citations) > 0
        assert len(resp1.suggested_follow_ups) > 0

        # Question 2: Recommended actions
        resp2 = await MultiAgentOrchestrator.chat_copilot(
            incident_id=inc.id,
            question="What containment actions are recommended?",
            history=None,
            db=session,
        )
        assert "Playbook" in resp2.answer or "Pending" in resp2.answer or "action" in resp2.answer.lower()

        # Question 3: IOCs
        resp3 = await MultiAgentOrchestrator.chat_copilot(
            incident_id=inc.id,
            question="What are the extracted IOCs?",
            history=None,
            db=session,
        )
        assert "192.168.1.150" in resp3.answer


@pytest.mark.asyncio
async def test_investigation_api_endpoints(async_client):
    """Verifies all Phase 7 REST API endpoints."""
    inc = await create_sample_incident()

    # 1. POST /api/v1/investigation/analyze/{incident_id}
    res = await async_client.post(f"/api/v1/investigation/analyze/{inc.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["incident_id"] == inc.id
    assert len(data["recommended_actions"]) > 0

    action_id = data["recommended_actions"][0]["id"]

    # 2. GET /api/v1/investigation/actions/{incident_id}
    actions_res = await async_client.get(f"/api/v1/investigation/actions/{inc.id}")
    assert actions_res.status_code == 200
    actions_list = actions_res.json()
    assert len(actions_list) > 0

    # 3. POST /api/v1/investigation/actions/review
    review_res = await async_client.post(
        "/api/v1/investigation/actions/review",
        json={
            "action_id": action_id,
            "decision": "Approved",
            "analyst_name": "Senior SOC Analyst",
            "comment": "Firewall containment approved via API test.",
        },
    )
    assert review_res.status_code == 200
    review_data = review_res.json()
    assert review_data["success"] is True
    assert review_data["action"]["status"] == "Approved"

    # 4. POST /api/v1/investigation/chat
    chat_res = await async_client.post(
        "/api/v1/investigation/chat",
        json={
            "incident_id": inc.id,
            "question": "Can you summarize the attack origin?",
        },
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "answer" in chat_data
    assert len(chat_data["grounded_facts"]) > 0

    # 5. GET /api/v1/investigation/report/{incident_id}
    report_res = await async_client.get(f"/api/v1/investigation/report/{inc.id}")
    assert report_res.status_code == 200
    assert report_res.headers["content-type"].startswith("text/markdown")
    assert "Sentriq Autonomous AI-SOC" in report_res.text
