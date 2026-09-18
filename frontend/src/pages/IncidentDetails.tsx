import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  Shield,
  Server,
  AlertTriangle,
  Flame,
  CheckCircle2,
  RefreshCw,
  Send,
  Copy,
  Check,
  Activity,
  Layers,
  Bot,
  FileText,
} from 'lucide-react';
import { socApi } from '../services/api';
import {
  IncidentDetail,
  IncidentStatus,
  IncidentTimeline,
  InvestigationDossier,
  ResponseAction,
} from '../types';
import { SeverityBadge } from '../components/ui/SeverityBadge';
import { StatusBadge } from '../components/ui/StatusBadge';
import {
  MultiAgentDossierCard,
  ContainmentActionsCard,
  GroundedCopilotDrawer,
  ExecutiveReportModal,
} from '../components/investigation';
import { formatTimeIST } from '../utils/date';

export const IncidentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [detail, setDetail] = useState<IncidentDetail | null>(null);
  const [timeline, setTimeline] = useState<IncidentTimeline | null>(null);
  const [dossier, setDossier] = useState<InvestigationDossier | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newNote, setNewNote] = useState<string>('');
  const [updating, setUpdating] = useState<boolean>(false);
  const [copiedIp, setCopiedIp] = useState<boolean>(false);

  const [isCopilotOpen, setIsCopilotOpen] = useState<boolean>(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState<boolean>(false);

  const fetchIncidentData = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [detailData, timelineData, dossierData] = await Promise.all([
        socApi.getIncidentDetail(id),
        socApi.getIncidentTimeline(id),
        socApi.investigateIncident(id),
      ]);
      setDetail(detailData);
      setTimeline(timelineData);
      setDossier(dossierData);
    } catch (err: any) {
      console.error('Failed to load incident detail:', err);
      setError(err.response?.data?.detail || 'Unable to load incident information.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidentData();
  }, [id]);

  const handleStatusChange = async (newStatus: IncidentStatus) => {
    if (!detail) return;
    setUpdating(true);
    try {
      await socApi.updateIncidentStatus(detail.id, newStatus, newNote || undefined);
      setNewNote('');
      await fetchIncidentData();
    } catch (err) {
      console.error('Failed to update status:', err);
    } finally {
      setUpdating(false);
    }
  };

  const handleActionUpdated = (updatedAction: ResponseAction) => {
    if (!dossier) return;
    setDossier({
      ...dossier,
      recommended_actions: dossier.recommended_actions.map((act) =>
        act.id === updatedAction.id ? updatedAction : act
      ),
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedIp(true);
    setTimeout(() => setCopiedIp(false), 2000);
  };

  if (loading) {
    return (
      <div className="py-24 text-center space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin text-sky-400 mx-auto" />
        <p className="text-sm text-slate-400 font-mono">
          Orchestrating multi-agent investigation & correlation timeline...
        </p>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="bg-soc-card border border-soc-border rounded-lg p-8 text-center space-y-4 max-w-md mx-auto my-12">
        <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto" />
        <h2 className="text-lg font-bold text-white">Incident Not Found</h2>
        <p className="text-xs text-slate-400">{error || 'The requested incident could not be found.'}</p>
        <button
          onClick={() => navigate('/incidents')}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold"
        >
          Return to Incidents
        </button>
      </div>
    );
  }

  const riskFactors = detail.risk_breakdown?.factors;

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/incidents"
            className="p-2 rounded-md bg-soc-card border border-soc-border text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-sky-400">{detail.incident_code}</span>
              <SeverityBadge severity={detail.severity} size="sm" />
              <StatusBadge status={detail.status} />
            </div>
            <h1 className="text-xl font-bold text-white mt-1 tracking-tight">{detail.title}</h1>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
          {/* Consult Copilot Button */}
          <button
            onClick={() => setIsCopilotOpen(true)}
            className="px-3 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>AI Copilot</span>
          </button>

          {/* Export Executive Dossier Button */}
          {dossier && (
            <button
              onClick={() => setIsReportModalOpen(true)}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              <span>Dossier</span>
            </button>
          )}

          {/* Status Changer Dropdown */}
          <select
            disabled={updating}
            value={detail.status}
            onChange={(e) => handleStatusChange(e.target.value as IncidentStatus)}
            className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-3 py-2 text-xs font-medium focus:outline-none focus:border-sky-500"
          >
            <option value="Open">Status: Open</option>
            <option value="Investigating">Status: Investigating</option>
            <option value="Resolved">Status: Resolved</option>
            <option value="Closed">Status: Closed</option>
          </select>

          <button
            onClick={fetchIncidentData}
            className="p-2 rounded bg-soc-card border border-soc-border text-slate-400 hover:text-white transition-colors"
            title="Refresh incident data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Summary KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
        <div className="bg-soc-card border border-soc-border rounded-lg p-3.5 space-y-1">
          <span className="text-[10px] uppercase text-slate-500 tracking-wider flex items-center gap-1 font-sans">
            <Flame className="w-3 h-3 text-rose-400" /> Attack Classification
          </span>
          <p className="text-sm font-bold text-rose-400">{detail.attack_category}</p>
          <span className="text-[10px] text-slate-400">ML Conf: {(detail.confidence * 100).toFixed(0)}%</span>
        </div>

        <div className="bg-soc-card border border-soc-border rounded-lg p-3.5 space-y-1">
          <span className="text-[10px] uppercase text-slate-500 tracking-wider flex items-center gap-1 font-sans">
            <Shield className="w-3 h-3 text-sky-400" /> Attacker Endpoint
          </span>
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-sky-400 truncate">{detail.source_ip || 'Internal Host'}</p>
            {detail.source_ip && (
              <button
                onClick={() => copyToClipboard(detail.source_ip!)}
                className="text-slate-400 hover:text-white ml-1"
                title="Copy IP"
              >
                {copiedIp ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            )}
          </div>
          <span className="text-[10px] text-slate-500">Origin IP Identity</span>
        </div>

        <div className="bg-soc-card border border-soc-border rounded-lg p-3.5 space-y-1">
          <span className="text-[10px] uppercase text-slate-500 tracking-wider flex items-center gap-1 font-sans">
            <Server className="w-3 h-3 text-amber-400" /> Target Infrastructure
          </span>
          <p className="text-sm font-bold text-slate-200 truncate">{detail.target_asset || 'Unknown Target'}</p>
          <span className="text-[10px] text-slate-500">Asset Impacted</span>
        </div>

        <div className="bg-soc-card border border-soc-border rounded-lg p-3.5 space-y-1">
          <span className="text-[10px] uppercase text-slate-500 tracking-wider flex items-center gap-1 font-sans">
            <Clock className="w-3 h-3 text-emerald-400" /> Correlated Events
          </span>
          <p className="text-sm font-bold text-emerald-400">{timeline?.total_events || detail.event_count} Events</p>
          <span className="text-[10px] text-slate-400">Duration: {timeline?.duration_seconds || 0}s</span>
        </div>
      </div>

      {/* Phase 7: AI Multi-Agent Investigation Dossier */}
      {dossier && (
        <MultiAgentDossierCard
          dossier={dossier}
          onOpenReport={() => setIsReportModalOpen(true)}
          onOpenCopilot={() => setIsCopilotOpen(true)}
        />
      )}

      {/* Phase 7: Human-in-the-Loop Containment Actions Card (PRD FR-10) */}
      {dossier && (
        <ContainmentActionsCard
          actions={dossier.recommended_actions}
          onActionUpdated={handleActionUpdated}
        />
      )}

      {/* 2-Column Split: Attack Timeline vs 4-Factor Risk Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Attack Story & Chronological Timeline (7 cols) */}
        <div className="lg:col-span-7 bg-soc-card border border-soc-border rounded-lg p-5 space-y-5">
          <div className="flex items-center justify-between border-b border-soc-border pb-3">
            <div>
              <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                <Activity className="w-4 h-4 text-sky-400" />
                Correlated Attack Timeline (PRD Section 14)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Chronological sequence of security events grouped within 15-minute sliding window
              </p>
            </div>
            <span className="text-xs font-mono text-slate-500">
              {timeline?.events.length || 0} stages recorded
            </span>
          </div>

          {!timeline || timeline.events.length === 0 ? (
            <div className="py-12 text-center text-slate-500 text-xs font-sans">
              No individual event timeline records attached.
            </div>
          ) : (
            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
              {timeline.events.map((ev, idx) => (
                <div key={ev.id} className="relative group">
                  {/* Timeline Node Icon */}
                  <div
                    className={`absolute -left-6 top-1 w-5 h-5 rounded-full border-2 flex items-center justify-center text-[10px] font-bold ${
                      ev.severity === 'Critical'
                        ? 'bg-rose-950 border-rose-500 text-rose-400'
                        : ev.severity === 'High'
                        ? 'bg-orange-950 border-orange-500 text-orange-400'
                        : ev.severity === 'Medium'
                        ? 'bg-amber-950 border-amber-500 text-amber-400'
                        : 'bg-emerald-950 border-emerald-500 text-emerald-400'
                    }`}
                  >
                    {idx + 1}
                  </div>

                  {/* Event Content Card */}
                  <div className="bg-slate-900/80 border border-slate-800 hover:border-slate-700 rounded-lg p-4 space-y-2 transition-colors">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-sky-400 text-[11px] bg-slate-800 px-2 py-0.5 rounded">
                          {ev.time_offset}
                        </span>
                        <span className="font-semibold text-white font-mono text-xs">{ev.event_type}</span>
                        <SeverityBadge severity={ev.severity} size="sm" />
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {formatTimeIST(ev.timestamp, true)}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 font-sans leading-relaxed">{ev.message}</p>

                    <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400">
                      <span>Source: <strong className="text-slate-300">{ev.source}</strong></span>
                      <span>{ev.source_ip} → {ev.destination_ip}:{ev.destination_port || '—'}</span>
                      {ev.user_identity && (
                        <span className="text-amber-400">User: {ev.user_identity}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Transparent 4-Factor Risk Breakdown (5 cols) */}
        <div className="lg:col-span-5 space-y-5">
          {/* Risk Card */}
          <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-soc-border pb-3">
              <div>
                <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                  <Layers className="w-4 h-4 text-rose-400" />
                  Transparent Risk Scoring (PRD Section 13)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Deterministic 4-factor mathematical model</p>
              </div>
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded font-mono ${
                  detail.risk_level === 'Critical'
                    ? 'bg-rose-950 text-rose-400 border border-rose-800'
                    : detail.risk_level === 'High'
                    ? 'bg-orange-950 text-orange-400 border border-orange-800'
                    : 'bg-amber-950 text-amber-400 border border-amber-800'
                }`}
              >
                {detail.risk_level}
              </span>
            </div>

            {/* Total Score Display */}
            <div className="flex items-center justify-between p-3.5 rounded-lg bg-slate-900/80 border border-slate-800">
              <div>
                <span className="text-[10px] uppercase font-mono text-slate-500">Calculated Threat Priority</span>
                <div className="text-3xl font-bold font-mono text-white mt-0.5">
                  {detail.risk_score.toFixed(1)} <span className="text-xs text-slate-500">/ 100</span>
                </div>
              </div>
              <div className="w-16 h-16 rounded-full border-4 border-slate-800 flex items-center justify-center font-mono font-bold text-sm text-sky-400">
                {detail.risk_score.toFixed(0)}%
              </div>
            </div>

            {/* 4-Factor Breakdown Bars */}
            {riskFactors && (
              <div className="space-y-3 font-mono text-xs">
                {/* 1. Severity */}
                <div className="space-y-1">
                  <div className="flex justify-between text-slate-400 text-[11px]">
                    <span>1. Severity (30% weight) [{riskFactors.severity.value}]</span>
                    <span className="text-slate-200 font-bold">+{riskFactors.severity.contribution.toFixed(1)}</span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-rose-500 h-full rounded-full"
                      style={{ width: `${(riskFactors.severity.score / 100) * 100}%` }}
                    />
                  </div>
                </div>

                {/* 2. Confidence */}
                <div className="space-y-1">
                  <div className="flex justify-between text-slate-400 text-[11px]">
                    <span>2. ML Confidence (30% weight) [{riskFactors.confidence.value}%]</span>
                    <span className="text-slate-200 font-bold">+{riskFactors.confidence.contribution.toFixed(1)}</span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-sky-500 h-full rounded-full"
                      style={{ width: `${(riskFactors.confidence.score / 100) * 100}%` }}
                    />
                  </div>
                </div>

                {/* 3. Asset Importance */}
                <div className="space-y-1">
                  <div className="flex justify-between text-slate-400 text-[11px]">
                    <span className="truncate max-w-[200px]">3. Asset Importance (20%) [{riskFactors.asset_importance.asset}]</span>
                    <span className="text-slate-200 font-bold">+{riskFactors.asset_importance.contribution.toFixed(1)}</span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-amber-500 h-full rounded-full"
                      style={{ width: `${(riskFactors.asset_importance.score / 100) * 100}%` }}
                    />
                  </div>
                </div>

                {/* 4. Attack Impact */}
                <div className="space-y-1">
                  <div className="flex justify-between text-slate-400 text-[11px]">
                    <span>4. Attack Impact (20%) [{riskFactors.attack_impact.category}]</span>
                    <span className="text-slate-200 font-bold">+{riskFactors.attack_impact.contribution.toFixed(1)}</span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-emerald-500 h-full rounded-full"
                      style={{ width: `${(riskFactors.attack_impact.score / 100) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Narrative Explanation Card */}
            {detail.risk_breakdown?.explanation && (
              <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 font-sans leading-relaxed">
                <div className="flex items-center gap-1.5 font-semibold text-slate-200 text-[11px] mb-1 font-mono">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />
                  Factor Attribution Narrative:
                </div>
                {detail.risk_breakdown.explanation}
              </div>
            )}
          </div>

          {/* Analyst Notes & Investigation Box */}
          <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              Investigation Notes & Audit Log
            </h3>
            {detail.notes ? (
              <pre className="bg-slate-900/90 border border-slate-800 rounded p-3 text-[11px] font-mono text-slate-300 whitespace-pre-wrap max-h-40 overflow-y-auto">
                {detail.notes}
              </pre>
            ) : (
              <p className="text-xs text-slate-500 italic">No notes appended yet.</p>
            )}

            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Add investigation note..."
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
              <button
                disabled={updating || !newNote.trim()}
                onClick={() => handleStatusChange(detail.status)}
                className="px-3 py-2 bg-sky-600 hover:bg-sky-500 disabled:bg-slate-800 text-white rounded text-xs font-semibold flex items-center gap-1"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Save</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Grounded Copilot Slide-over Drawer */}
      <GroundedCopilotDrawer
        incidentId={detail.id}
        incidentCode={detail.incident_code}
        isOpen={isCopilotOpen}
        onClose={() => setIsCopilotOpen(false)}
      />

      {/* Executive Markdown Dossier Modal */}
      {dossier && (
        <ExecutiveReportModal
          incidentCode={detail.incident_code}
          markdownContent={dossier.executive_summary_markdown}
          isOpen={isReportModalOpen}
          onClose={() => setIsReportModalOpen(false)}
        />
      )}
    </div>
  );
};
