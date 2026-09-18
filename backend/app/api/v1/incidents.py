import math
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.schemas.common import PaginatedResponse
from app.schemas.incident import (
    IncidentCreate,
    IncidentDetailResponse,
    IncidentResponse,
    IncidentStatusUpdate,
    IncidentSummary,
    IncidentTimelineResponse,
    TimelineEventItem,
)
from app.services.correlation_engine import EventCorrelationEngine
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("/summary", response_model=IncidentSummary)
async def get_incident_summary(db: AsyncSession = Depends(get_db)):
    """Provides high-level KPI counts for the SOC dashboard."""
    total_q = await db.execute(select(func.count(Incident.id)))
    total = total_q.scalar() or 0

    open_q = await db.execute(select(func.count(Incident.id)).where(Incident.status.in_(["Open", "Investigating"])))
    open_count = open_q.scalar() or 0

    critical_q = await db.execute(select(func.count(Incident.id)).where(Incident.severity == "Critical"))
    critical = critical_q.scalar() or 0

    high_risk_q = await db.execute(select(func.count(Incident.id)).where(Incident.risk_score >= 60.0))
    high_risk = high_risk_q.scalar() or 0

    return IncidentSummary(
        total_incidents=total,
        open_incidents=open_count,
        critical_incidents=critical,
        high_risk_incidents=high_risk,
    )


@router.post("/correlate")
async def trigger_event_correlation(db: AsyncSession = Depends(get_db)):
    """Runs correlation engine across unassigned security events in the database."""
    correlated_count = await EventCorrelationEngine.correlate_unassigned_events(db)
    return {
        "status": "success",
        "events_correlated": correlated_count,
        "message": f"Successfully correlated {correlated_count} security events into incidents.",
    }


@router.get("", response_model=PaginatedResponse[IncidentResponse])
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    attack_category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lists security incidents with pagination and filtering."""
    query = select(Incident).order_by(Incident.created_at.desc())

    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    if attack_category:
        query = query.where(Incident.attack_category == attack_category)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count_res = await db.execute(count_query)
    total = count_res.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves single incident detail by ID or incident_code."""
    query = select(Incident).where(
        (Incident.id == incident_id) | (Incident.incident_code == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found",
        )
    return incident


@router.get("/{incident_id}/detail", response_model=IncidentDetailResponse)
async def get_incident_detail(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves single incident detail with transparent 4-factor risk breakdown and correlated events."""
    query = (
        select(Incident)
        .options(selectinload(Incident.events))
        .where((Incident.id == incident_id) | (Incident.incident_code == incident_id))
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found",
        )

    # Calculate transparent 4-factor risk breakdown
    risk_breakdown = RiskEngine.calculate_risk(
        severity=incident.severity,
        confidence=incident.confidence,
        attack_category=incident.attack_category,
        asset_identifier=incident.target_asset,
    )

    return IncidentDetailResponse(
        id=incident.id,
        incident_code=incident.incident_code,
        title=incident.title,
        description=incident.description,
        attack_category=incident.attack_category,
        severity=incident.severity,
        risk_score=incident.risk_score,
        risk_level=incident.risk_level,
        confidence=incident.confidence,
        status=incident.status,
        source_ip=incident.source_ip,
        target_asset=incident.target_asset,
        event_count=incident.event_count,
        notes=incident.notes,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        risk_breakdown=risk_breakdown,
        events=incident.events,
    )


@router.get("/{incident_id}/timeline", response_model=IncidentTimelineResponse)
async def get_incident_timeline(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Generates an attack timeline with chronological events and calculated time deltas."""
    query = (
        select(Incident)
        .options(selectinload(Incident.events))
        .where((Incident.id == incident_id) | (Incident.incident_code == incident_id))
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found",
        )

    sorted_events = sorted(incident.events, key=lambda ev: ev.timestamp)
    timeline_items = []
    base_time = sorted_events[0].timestamp if sorted_events else incident.created_at

    for ev in sorted_events:
        delta_sec = int((ev.timestamp - base_time).total_seconds())
        if delta_sec < 60:
            offset_str = f"+{delta_sec}s"
        else:
            mins = delta_sec // 60
            secs = delta_sec % 60
            offset_str = f"+{mins}m {secs}s"

        timeline_items.append(
            TimelineEventItem(
                id=ev.id,
                timestamp=ev.timestamp,
                delta_seconds=delta_sec,
                time_offset=offset_str,
                event_type=ev.event_type,
                source=ev.source,
                severity=ev.severity,
                source_ip=ev.source_ip,
                destination_ip=ev.destination_ip,
                destination_port=ev.destination_port,
                message=ev.message,
                attack_type=ev.attack_type,
                user_identity=ev.user_identity,
            )
        )

    duration = int((sorted_events[-1].timestamp - base_time).total_seconds()) if sorted_events else 0

    return IncidentTimelineResponse(
        incident_id=incident.id,
        incident_code=incident.incident_code,
        title=incident.title,
        total_events=len(sorted_events),
        duration_seconds=duration,
        events=timeline_items,
    )


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(payload: IncidentCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new incident record."""
    incident_code = payload.incident_code
    if not incident_code:
        count_q = await db.execute(select(func.count(Incident.id)))
        count = (count_q.scalar() or 0) + 1
        incident_code = f"INC-2026-{count:04d}"

    incident = Incident(
        id=str(uuid.uuid4()),
        incident_code=incident_code,
        title=payload.title,
        description=payload.description,
        attack_category=payload.attack_category,
        severity=payload.severity,
        risk_score=payload.risk_score,
        risk_level=payload.risk_level,
        confidence=payload.confidence,
        status=payload.status,
        source_ip=payload.source_ip,
        target_asset=payload.target_asset,
        event_count=payload.event_count,
        notes=payload.notes,
    )
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Updates an incident's lifecycle status (Open -> Investigating -> Resolved -> Closed)."""
    query = select(Incident).where(
        (Incident.id == incident_id) | (Incident.incident_code == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found",
        )

    incident.status = payload.status
    if payload.notes:
        if incident.notes:
            incident.notes += f"\n[Status -> {payload.status}]: {payload.notes}"
        else:
            incident.notes = f"[Status -> {payload.status}]: {payload.notes}"

    await db.commit()
    await db.refresh(incident)
    return incident
