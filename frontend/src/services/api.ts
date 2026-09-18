import axios from 'axios';
import {
  ActionApprovalRequest,
  ActionApprovalResponse,
  CopilotChatRequest,
  CopilotChatResponse,
  EventStats,
  HealthResponse,
  Incident,
  IncidentDetail,
  IncidentSummary,
  IncidentTimeline,
  InvestigationDossier,
  MLPredictionResponse,
  ModelInfoResponse,
  PaginatedResponse,
  ResponseAction,
  SecurityEvent,
  SimulateScenarioResponse,
  SimulationStatus,
  XAIExplanationResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const socApi = {
  // Health
  getHealth: async (): Promise<HealthResponse> => {
    const { data } = await apiClient.get<HealthResponse>('/health');
    return data;
  },

  // Incidents (Phase 1 & Phase 4)
  getIncidentSummary: async (): Promise<IncidentSummary> => {
    const { data } = await apiClient.get<IncidentSummary>('/incidents/summary');
    return data;
  },

  getIncidents: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    severity?: string;
    attack_category?: string;
  }): Promise<PaginatedResponse<Incident>> => {
    const { data } = await apiClient.get<PaginatedResponse<Incident>>('/incidents', { params });
    return data;
  },

  getIncidentById: async (id: string): Promise<Incident> => {
    const { data } = await apiClient.get<Incident>(`/incidents/${id}`);
    return data;
  },

  getIncidentDetail: async (id: string): Promise<IncidentDetail> => {
    const { data } = await apiClient.get<IncidentDetail>(`/incidents/${id}/detail`);
    return data;
  },

  getIncidentTimeline: async (id: string): Promise<IncidentTimeline> => {
    const { data } = await apiClient.get<IncidentTimeline>(`/incidents/${id}/timeline`);
    return data;
  },

  triggerCorrelation: async (): Promise<{ status: string; events_correlated: number; message: string }> => {
    const { data } = await apiClient.post('/incidents/correlate');
    return data;
  },

  updateIncidentStatus: async (id: string, status: string, notes?: string): Promise<Incident> => {
    const { data } = await apiClient.patch<Incident>(`/incidents/${id}/status`, { status, notes });
    return data;
  },

  // Security Events Telemetry (Phase 2)
  getEvents: async (params?: {
    page?: number;
    page_size?: number;
    severity?: string;
    attack_type?: string;
    source?: string;
    search?: string;
    is_attack?: boolean;
    is_simulated?: boolean;
  }): Promise<PaginatedResponse<SecurityEvent>> => {
    const { data } = await apiClient.get<PaginatedResponse<SecurityEvent>>('/events', { params });
    return data;
  },

  getEventStats: async (): Promise<EventStats> => {
    const { data } = await apiClient.get<EventStats>('/events/stats');
    return data;
  },

  getEventById: async (id: string): Promise<SecurityEvent> => {
    const { data } = await apiClient.get<SecurityEvent>(`/events/${id}`);
    return data;
  },

  simulateScenario: async (scenario: string, count: number = 8): Promise<SimulateScenarioResponse> => {
    const { data } = await apiClient.post<SimulateScenarioResponse>('/events/simulate', { scenario, count });
    return data;
  },

  ingestBenchmark: async (dataset: string = 'unsw'): Promise<{ status: string; benchmark_source: string; records_ingested: number }> => {
    const { data } = await apiClient.post('/events/ingest-benchmark', null, {
      params: { dataset },
    });
    return data;
  },

  uploadCsvDataset: async (file: File): Promise<{
    status: string;
    filename: string;
    detected_format: string;
    records_ingested: number;
    message: string;
  }> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await apiClient.post('/events/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },


  // Machine Learning Detection (Phase 3)
  getModelInfo: async (): Promise<ModelInfoResponse> => {
    const { data } = await apiClient.get<ModelInfoResponse>('/ml/model-info');
    return data;
  },

  predictThreat: async (payload: { event_id?: string; features?: Record<string, any> }): Promise<MLPredictionResponse> => {
    const { data } = await apiClient.post<MLPredictionResponse>('/ml/predict', payload);
    return data;
  },

  analyzeEventById: async (eventId: string): Promise<MLPredictionResponse> => {
    const { data } = await apiClient.post<MLPredictionResponse>(`/ml/analyze-event/${eventId}`);
    return data;
  },

  // Telemetry Stream Simulation (Phase 5)
  getSimulationStatus: async (): Promise<SimulationStatus> => {
    const { data } = await apiClient.get<SimulationStatus>('/simulation/status');
    return data;
  },

  startSimulation: async (): Promise<SimulationStatus> => {
    const { data } = await apiClient.post<SimulationStatus>('/simulation/start');
    return data;
  },

  stopSimulation: async (): Promise<SimulationStatus> => {
    const { data } = await apiClient.post<SimulationStatus>('/simulation/stop');
    return data;
  },

  setSimulationSpeed: async (speed: number): Promise<SimulationStatus> => {
    const { data } = await apiClient.post<SimulationStatus>('/simulation/speed', { speed });
    return data;
  },

  injectSimulationScenario: async (
    scenario: string
  ): Promise<{ status: string; scenario: string; events_queued: number; total_queue_size: number }> => {
    const { data } = await apiClient.post('/simulation/inject', { scenario });
    return data;
  },

  // Explainable AI (Phase 6)
  getEventExplanation: async (eventId: string): Promise<XAIExplanationResponse> => {
    const { data } = await apiClient.get<XAIExplanationResponse>(`/ml/explain/${eventId}`);
    return data;
  },

  explainFeatures: async (payload: {
    event_id?: string;
    features?: Record<string, any>;
  }): Promise<XAIExplanationResponse> => {
    const { data } = await apiClient.post<XAIExplanationResponse>('/ml/explain', payload);
    return data;
  },

  // AI-Assisted Investigation & Copilot (Phase 7)
  investigateIncident: async (incidentId: string): Promise<InvestigationDossier> => {
    const { data } = await apiClient.post<InvestigationDossier>(`/investigation/analyze/${incidentId}`);
    return data;
  },

  getIncidentActions: async (incidentId: string): Promise<ResponseAction[]> => {
    const { data } = await apiClient.get<ResponseAction[]>(`/investigation/actions/${incidentId}`);
    return data;
  },

  reviewAction: async (payload: ActionApprovalRequest): Promise<ActionApprovalResponse> => {
    const { data } = await apiClient.post<ActionApprovalResponse>('/investigation/actions/review', payload);
    return data;
  },

  chatCopilot: async (payload: CopilotChatRequest): Promise<CopilotChatResponse> => {
    const { data } = await apiClient.post<CopilotChatResponse>('/investigation/chat', payload);
    return data;
  },

  getIncidentReportText: async (incidentId: string): Promise<string> => {
    const { data } = await apiClient.get<string>(`/investigation/report/${incidentId}`, {
      responseType: 'text',
    });
    return data;
  },
};

