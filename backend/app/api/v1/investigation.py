import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import MultiAgentOrchestrator
from app.core.database import get_db
from app.schemas.investigation import (
    ActionApprovalRequest,
    ActionApprovalResponse,
    CopilotChatRequest,
    CopilotChatResponse,
    InvestigationDossier,
    ResponseActionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/investigation", tags=["AI SOC Investigation & Copilot"])


@router.post("/analyze/{incident_id}", response_model=InvestigationDossier)
async def analyze_incident(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes the multi-agent investigation pipeline on an incident:
    - Triage & IOC Extraction Agent
    - Kill-Chain & Blast Radius Correlation Agent
    - Response Playbook Formulation Agent (Human-in-the-Loop)
    - Executive Report Generator Agent
    """
    try:
        dossier = await MultiAgentOrchestrator.get_or_run_investigation(incident_id, db)
        return dossier
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error during incident investigation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}",
        )


@router.get("/actions/{incident_id}", response_model=List[ResponseActionResponse])
async def get_incident_actions(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves all containment and remediation actions associated with an incident.
    """
    try:
        dossier = await MultiAgentOrchestrator.get_or_run_investigation(incident_id, db)
        return dossier.recommended_actions
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error retrieving actions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not fetch actions: {str(e)}",
        )


@router.post("/actions/review", response_model=ActionApprovalResponse)
async def review_action(
    payload: ActionApprovalRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Processes human-in-the-loop analyst review (Approve / Reject) for a containment action (PRD FR-10).
    Enforces that actions are never auto-executed without explicit analyst authorization.
    """
    try:
        updated_action = await MultiAgentOrchestrator.review_action(
            action_id=payload.action_id,
            decision=payload.decision,
            analyst_name=payload.analyst_name,
            comment=payload.comment,
            db=db,
        )
        return ActionApprovalResponse(
            success=True,
            message=f"Action '{updated_action.title}' successfully marked as {payload.decision}.",
            action=ResponseActionResponse.model_validate(updated_action),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error reviewing containment action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Action review failed: {str(e)}",
        )


@router.post("/chat", response_model=CopilotChatResponse)
async def chat_copilot(
    payload: CopilotChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Zero-hallucination Grounded SOC Copilot (PRD FR-09).
    Answers analyst questions strictly based on database telemetry, timestamps,
    ML confidence, and containment actions.
    """
    try:
        response = await MultiAgentOrchestrator.chat_copilot(
            incident_id=payload.incident_id,
            question=payload.question,
            history=payload.history,
            db=db,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error in copilot chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Copilot query failed: {str(e)}",
        )


@router.get("/report/{incident_id}")
async def get_incident_report(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Exports executive markdown dossier for an incident (PRD FR-11).
    """
    try:
        dossier = await MultiAgentOrchestrator.get_or_run_investigation(incident_id, db)
        return PlainTextResponse(
            content=dossier.executive_summary_markdown,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=Dossier-{dossier.incident_code}.md"
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Error generating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report export failed: {str(e)}",
        )

