import math
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.event import SecurityEvent
from app.schemas.common import PaginatedResponse
from app.schemas.event import (
    DatasetSummaryResponse,
    DatasetUpdateRequest,
    EventStatsResponse,
    SecurityEventCreate,
    SecurityEventResponse,
    SecurityEventUpdate,
    SimulateScenarioRequest,
    SimulateScenarioResponse,
)
from app.services.benchmark_loader import BenchmarkLoader
from app.services.data_generator import SecurityDataGenerator

router = APIRouter(prefix="/events", tags=["Security Events"])


@router.get("/stats", response_model=EventStatsResponse)
async def get_event_stats(db: AsyncSession = Depends(get_db)):
    """Computes aggregate distribution metrics across all ingested security events."""
    total_q = await db.execute(select(func.count(SecurityEvent.id)))
    total = total_q.scalar() or 0

    threat_q = await db.execute(select(func.count(SecurityEvent.id)).where(SecurityEvent.is_attack == True))
    threat_count = threat_q.scalar() or 0

    benign_count = total - threat_count

    # Attack category breakdown
    attack_q = await db.execute(
        select(SecurityEvent.attack_type, func.count(SecurityEvent.id)).group_by(SecurityEvent.attack_type)
    )
    attack_distribution = {row[0]: row[1] for row in attack_q.all()}

    # Severity breakdown
    sev_q = await db.execute(
        select(SecurityEvent.severity, func.count(SecurityEvent.id)).group_by(SecurityEvent.severity)
    )
    severity_distribution = {row[0]: row[1] for row in sev_q.all()}

    # Source breakdown
    src_q = await db.execute(
        select(SecurityEvent.source, func.count(SecurityEvent.id)).group_by(SecurityEvent.source)
    )
    source_distribution = {row[0]: row[1] for row in src_q.all()}

    return EventStatsResponse(
        total_events=total,
        threat_events=threat_count,
        benign_events=benign_count,
        attack_distribution=attack_distribution,
        severity_distribution=severity_distribution,
        source_distribution=source_distribution,
    )


@router.get("", response_model=PaginatedResponse[SecurityEventResponse])
async def list_security_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    severity: Optional[str] = Query(None),
    attack_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_attack: Optional[bool] = Query(None),
    is_simulated: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves paginated and filtered security events from PostgreSQL."""
    query = select(SecurityEvent).order_by(SecurityEvent.timestamp.desc())

    if severity:
        query = query.where(SecurityEvent.severity == severity)
    if attack_type:
        query = query.where(SecurityEvent.attack_type == attack_type)
    if source:
        query = query.where(SecurityEvent.source == source)
    if is_attack is not None:
        query = query.where(SecurityEvent.is_attack == is_attack)
    if is_simulated is not None:
        query = query.where(SecurityEvent.is_simulated == is_simulated)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                SecurityEvent.message.ilike(search_pattern),
                SecurityEvent.source_ip.ilike(search_pattern),
                SecurityEvent.destination_ip.ilike(search_pattern),
                SecurityEvent.user_identity.ilike(search_pattern),
                SecurityEvent.event_type.ilike(search_pattern),
            )
        )

    # Count total matching
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


@router.get("/{event_id}", response_model=SecurityEventResponse)
async def get_security_event(event_id: str, db: AsyncSession = Depends(get_db)):
    """Fetches full security event record including raw features JSON."""
    query = select(SecurityEvent).where(SecurityEvent.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security event '{event_id}' not found",
        )
    return event


@router.post("/simulate", response_model=SimulateScenarioResponse)
async def simulate_scenario(
    payload: SimulateScenarioRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers on-demand generation of realistic security event sequences:
    'brute_force' (PRD Section 12), 'dos', 'port_scan', or 'benign'.
    """
    scenario_type = payload.scenario.lower()
    events = []

    if scenario_type == "brute_force":
        events = SecurityDataGenerator.generate_brute_force_scenario(fail_count=payload.count)
        msg = f"Generated PRD Section 12 Brute Force compromise scenario with {len(events)} events."
    elif scenario_type == "dos":
        events = SecurityDataGenerator.generate_dos_scenario(packet_burst=payload.count)
        msg = f"Generated volumetric DoS flood burst scenario with {len(events)} events."
    elif scenario_type == "port_scan":
        events = SecurityDataGenerator.generate_port_scan_scenario()
        msg = f"Generated sequential port reconnaissance scan scenario with {len(events)} events."
    else:  # benign
        for _ in range(payload.count):
            events.append(SecurityDataGenerator.generate_benign_event())
        msg = f"Generated {len(events)} routine benign network telemetry events."

    db.add_all(events)
    await db.commit()

    # Refresh newly added items
    for ev in events:
        await db.refresh(ev)

    return SimulateScenarioResponse(
        scenario=scenario_type,
        generated_events_count=len(events),
        message=msg,
        events=events,
    )


@router.post("/ingest-benchmark", status_code=status.HTTP_201_CREATED)
async def ingest_benchmark_data(
    dataset: str = Query(default="unsw", description="Dataset to ingest: 'unsw', 'cic', or 'all'"),
    db: AsyncSession = Depends(get_db),
):
    """Loads and normalizes public benchmark records (UNSW-NB15 and/or CIC-IDS2017) into PostgreSQL."""
    events = []
    dataset_lower = dataset.lower().strip()

    if dataset_lower in ["unsw", "all"]:
        unsw_events = BenchmarkLoader.load_unsw_sample()
        events.extend(unsw_events)

    if dataset_lower in ["cic", "all"]:
        cic_events = BenchmarkLoader.load_cic_sample()
        events.extend(cic_events)

    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark dataset sample for '{dataset}' not found or empty.",
        )

    db.add_all(events)
    await db.commit()

    source_label = "UNSW-NB15 & CIC-IDS2017" if dataset_lower == "all" else (
        "CIC-IDS2017" if dataset_lower == "cic" else "UNSW-NB15"
    )

    return {
        "status": "success",
        "benchmark_source": source_label,
        "records_ingested": len(events),
        "is_simulated": False,
    }


@router.post("/upload-csv", status_code=status.HTTP_201_CREATED)
async def upload_csv_dataset(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Accepts a manually uploaded CSV dataset file (UNSW-NB15, CIC-IDS2017, or custom security logs),
    validates the schema, normalizes records, and ingests them into PostgreSQL.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a .csv file.",
        )

    content_bytes = await file.read()
    try:
        csv_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        csv_text = content_bytes.decode("latin-1")

    if not csv_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded CSV file is empty.",
        )

    try:
        events, detected_dataset = BenchmarkLoader.parse_csv_content(csv_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse CSV dataset: {str(e)}",
        )

    if not events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid security records could be parsed from the CSV file.",
        )

    db.add_all(events)
    await db.commit()

    return {
        "status": "success",
        "filename": file.filename,
        "detected_format": detected_dataset,
        "records_ingested": len(events),
        "is_simulated": False,
        "message": f"Successfully ingested {len(events)} records in {detected_dataset} format.",
    }


