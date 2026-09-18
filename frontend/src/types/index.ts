export type Severity = 'Low' | 'Medium' | 'High' | 'Critical';
export type IncidentStatus = 'Open' | 'Investigating' | 'Resolved' | 'Closed';

export interface Incident {
  id: string;
  incident_code: string;
  title: string;
  description: string | null;
  attack_category: string;
  severity: Severity;
  risk_score: number;
  risk_level: Severity;
  confidence: number;
  status: IncidentStatus;
  source_ip: string | null;
  target_asset: string | null;
  event_count: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface RiskFactorItem {
  value?: string | number;
  score: number;
  weight: number;
  contribution: number;
  asset?: string;
  category?: string;
}

export interface RiskBreakdown {
  risk_score: number;
  risk_level: Severity;
  factors: {
    severity: RiskFactorItem;
    confidence: RiskFactorItem;
    asset_importance: RiskFactorItem;
    attack_impact: RiskFactorItem;
  };
  explanation: string;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  delta_seconds: number;
  time_offset: string;
  event_type: string;
  source: string;
  severity: Severity;
  source_ip: string;
  destination_ip: string;
  destination_port: number | null;
  message: string;
  attack_type: string;
  user_identity: string | null;
}

export interface IncidentTimeline {
  incident_id: string;
  incident_code: string;
  title: string;
  total_events: number;
  duration_seconds: number;
  events: TimelineEvent[];
}

export interface IncidentDetail extends Incident {
  risk_breakdown: RiskBreakdown | null;
  events: SecurityEvent[];
}

export interface IncidentSummary {
  total_incidents: number;
  open_incidents: number;
  critical_incidents: number;
  high_risk_incidents: number;
}

export interface SecurityEvent {
  id: string;
  timestamp: string;
  source: string;
  event_type: string;
  source_ip: string;
  destination_ip: string;
  source_port: number | null;
  destination_port: number | null;
  protocol: string;
  user_identity: string | null;
  attack_type: string;
  severity: Severity;
  message: string;
  raw_features: Record<string, any> | null;
  is_attack: boolean;
  is_simulated: boolean;
  incident_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface EventStats {
  total_events: number;
  threat_events: number;
  benign_events: number;
  attack_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
}

export interface SimulateScenarioResponse {
  scenario: string;
  generated_events_count: number;
  message: string;
  events: SecurityEvent[];
}

export interface MLPredictionResponse {
  is_threat: boolean;
  verdict: 'MALICIOUS' | 'BENIGN';
  threat_probability: number;
  predicted_attack_category: string;
  confidence: number;
  class_probabilities: Record<string, number>;
  detection_reasons: string[];
  model_version: string;
  evaluated_features: Record<string, any>;
}

export interface ModelInfoResponse {
  model_version: string;
  algorithm: string;
  trained_at: string;
  supported_classes: string[];
  features_used: string[];
  dataset_sample_size: number;
  metrics_summary: Record<string, number>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface HealthResponse {
  status: string;
  project: string;
  version: string;
  database: string;
  database_engine: string;
  timestamp: string;
}

export interface SimulationStatus {
  is_running: boolean;
  speed: number;
  events_generated: number;
  threats_detected: number;
  incidents_triggered: number;
  queue_size: number;
  active_clients: number;
  uptime_seconds: number;
}

export interface WsDetectionAlert {
  event_id: string;
  timestamp: string;
  attack_category: string;
  severity: Severity;
  confidence: number;
  source_ip: string;
  target_asset: string;
  message: string;
  detection_reasons: string[];
}

export interface WsMetricsUpdate {
  total_events: number;
  threats_detected: number;
  incidents_triggered: number;
  stream_speed: number;
  is_running: boolean;
}

export interface WsTelemetryEnvelope {
  type:
    | 'EVENT_INGESTED'
    | 'DETECTION_ALERT'
    | 'INCIDENT_CREATED'
    | 'INCIDENT_UPDATED'
    | 'METRICS_UPDATE'
    | 'STREAM_STATUS'
    | 'PONG'
    | 'SYSTEM_MESSAGE';
  data: any;
}

export interface FeatureAttribution {
  feature_name: string;
  display_name: string;
  feature_value: any;
  shap_value: number;
  contribution_percent: number;
  direction: 'positive' | 'negative';
  baseline_mean?: number | null;
}

export interface XAIExplanationResponse {
  event_id: string | null;
  model_version: string;
  predicted_category: string;
  attack_probability: number;
  base_value: number;
  positive_contributors: FeatureAttribution[];
  negative_contributors: FeatureAttribution[];
  all_features: FeatureAttribution[];
  narrative: string;
  rule_agreement: boolean;
  rule_reasons: string[];
  inference_latency_ms: number;
}

export interface IOCDetail {
  type: string;
  value: string;
  reputation: string;
  description: string;
  first_seen: string | null;
  last_seen: string | null;
}

export interface ResponseAction {
  id: string;
  incident_id: string;
  action_type: string;
  title: string;
  description: string;
  command: string | null;
  target_entity: string;
  risk_level: string;
  status: 'Pending' | 'Approved' | 'Executed' | 'Rejected';
  analyst_comment: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
}

export interface ActionApprovalRequest {
  action_id: string;
  decision: 'Approved' | 'Rejected';
  analyst_name?: string;
  comment?: string;
}

export interface ActionApprovalResponse {
  success: boolean;
  message: string;
  action: ResponseAction;
}

export interface InvestigationDossier {
  incident_id: string;
  incident_code: string;
  title: string;
  severity: Severity;
  risk_score: number;
  attack_entry_vector: string;
  kill_chain_stage: string;
  blast_radius_summary: string;
  affected_assets: string[];
  indicators_of_compromise: IOCDetail[];
  agent_findings: Record<string, any>;
  recommended_actions: ResponseAction[];
  executive_summary_markdown: string;
}

export interface CopilotChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  grounded_facts?: string[];
  citations?: string[];
  suggested_follow_ups?: string[];
  timestamp: string;
}

export interface CopilotChatRequest {
  incident_id: string;
  question: string;
  history?: Array<{ role: string; content: string }>;
}

export interface CopilotChatResponse {
  answer: string;
  grounded_facts: string[];
  citations: string[];
  suggested_follow_ups: string[];
}


