import uuid
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Incident(Base, TimestampMixin):
    """
    Represents a unified security incident composed of one or more
    correlated security events. Follows PRD Section 15 and FR-07.
    """
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    incident_code = Column(String(32), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    attack_category = Column(String(64), nullable=False, default="Unknown", index=True)
    severity = Column(String(16), nullable=False, default="Medium", index=True)  # Low, Medium, High, Critical
    risk_score = Column(Float, nullable=False, default=50.0)  # 0 to 100
    risk_level = Column(String(16), nullable=False, default="Medium")  # Low, Medium, High, Critical
    confidence = Column(Float, nullable=False, default=0.85)  # 0.0 to 1.0
    status = Column(String(16), nullable=False, default="Open", index=True)  # Open, Investigating, Resolved, Closed
    source_ip = Column(String(64), nullable=True, index=True)
    target_asset = Column(String(128), nullable=True)
    event_count = Column(Integer, nullable=False, default=1)
    notes = Column(Text, nullable=True)

    # Relationship to SecurityEvent
    events = relationship("SecurityEvent", back_populates="incident", lazy="selectin")
    response_actions = relationship("ResponseAction", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")

