import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class SecurityEvent(Base, TimestampMixin):
    """
    Standardized security event model shared across Ingestion, ML Detection,
    Risk Scoring, and Correlation. Follows PRD Section 7.
    """
    __tablename__ = "security_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    source = Column(String(64), nullable=False, default="auth_service", index=True)
    event_type = Column(String(64), nullable=False, default="login_attempt", index=True)
    source_ip = Column(String(64), nullable=False, default="127.0.0.1", index=True)
    destination_ip = Column(String(64), nullable=False, default="10.0.0.1", index=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String(16), nullable=False, default="TCP")
    user_identity = Column(String(64), nullable=True, index=True)
    attack_type = Column(String(64), nullable=False, default="Normal", index=True)
    severity = Column(String(16), nullable=False, default="Low", index=True)
    message = Column(Text, nullable=False)
    raw_features = Column(JSON, nullable=True)
    is_attack = Column(Boolean, nullable=False, default=False, index=True)
    is_simulated = Column(Boolean, nullable=False, default=True, index=True)

    # Optional correlation link to parent incident
    incident_id = Column(String(36), ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    incident = relationship("Incident", back_populates="events")

