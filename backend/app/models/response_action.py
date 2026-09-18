import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class ResponseAction(Base):
    """
    Recommended containment and remediation actions formulated by the AI Response Agent.
    Strictly follows PRD FR-10 (Human-in-the-Loop Response Approval).
    """

    __tablename__ = "response_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(
        String(36),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type = Column(String(50), nullable=False)  # firewall_rule, account_lock, host_isolation, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    command = Column(Text, nullable=True)  # Concrete remediation command/script
    target_entity = Column(String(255), nullable=False)  # IP, username, hostname
    risk_level = Column(String(20), default="Medium")  # Low, Medium, High
    status = Column(String(20), default="Pending", index=True)  # Pending, Approved, Executed, Rejected
    analyst_comment = Column(Text, nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="response_actions")

    def __repr__(self) -> str:
        return f"<ResponseAction {self.action_type}:{self.title} status={self.status}>"

