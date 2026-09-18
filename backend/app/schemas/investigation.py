from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class IOCDetail(BaseModel):
    type: str = Field(..., description="Type of IOC: ip, port, user, protocol, volume, etc.")
    value: str = Field(..., description="Extracted indicator value")
    reputation: str = Field(default="Suspicious", description="Malicious, Suspicious, Internal, or Compromised")
    description: str = Field(..., description="Contextual significance of this IOC")
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class ResponseActionResponse(BaseModel):
    id: str
    incident_id: str
    action_type: str
    title: str
    description: str
    command: Optional[str] = None
    target_entity: str
    risk_level: str
    status: str
    analyst_comment: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionApprovalRequest(BaseModel):
    action_id: str
    decision: str = Field(..., pattern="^(Approved|Rejected)$")
    analyst_name: str = Field(default="Senior SOC Analyst", max_length=100)
    comment: Optional[str] = Field(default=None, max_length=1000)


class ActionApprovalResponse(BaseModel):
    success: bool
    message: str
    action: ResponseActionResponse


class AgentFinding(BaseModel):
    agent_name: str
    role: str
    summary: str
    confidence: float
    details: Dict[str, Any] = {}


class InvestigationDossier(BaseModel):
    incident_id: str
    incident_code: str
    title: str
    severity: str
    risk_score: float
    attack_entry_vector: str
    kill_chain_stage: str
    blast_radius_summary: str
    affected_assets: List[str]
    indicators_of_compromise: List[IOCDetail]
    agent_findings: Dict[str, Any]
    recommended_actions: List[ResponseActionResponse]
    executive_summary_markdown: str


class CopilotChatRequest(BaseModel):
    incident_id: str
    question: str = Field(..., min_length=1, max_length=2000)
    history: Optional[List[Dict[str, str]]] = None


class CopilotChatResponse(BaseModel):
    answer: str
    grounded_facts: List[str]
    citations: List[str]
    suggested_follow_ups: List[str]

