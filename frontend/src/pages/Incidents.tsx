import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertOctagon, Filter, RefreshCw, X, ArrowUpRight } from 'lucide-react';
import { socApi } from '../services/api';
import { Incident, IncidentStatus } from '../types';
import { SeverityBadge } from '../components/ui/SeverityBadge';
import { StatusBadge } from '../components/ui/StatusBadge';

export const Incidents: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [actionNotes, setActionNotes] = useState<string>('');
  const [updating, setUpdating] = useState<boolean>(false);

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const data = await socApi.getIncidents({
        status: statusFilter || undefined,
        severity: severityFilter || undefined,
        page_size: 50,
      });
      setIncidents(data.items);
    } catch (err) {
      console.error('Failed to fetch incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
  }, [statusFilter, severityFilter]);

  const handleStatusChange = async (newStatus: IncidentStatus) => {
    if (!selectedIncident) return;
    setUpdating(true);
    try {
      const updated = await socApi.updateIncidentStatus(
        selectedIncident.id,
        newStatus,
        actionNotes || undefined
      );
      setSelectedIncident(updated);
      setActionNotes('');
      await fetchIncidents();
    } catch (err) {
      console.error('Failed to update incident status:', err);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Incident Management</h1>
          <p className="text-sm text-slate-400 mt-1">
            Review, investigate, and transition correlated security incidents.
          </p>
        </div>
        <button
          onClick={fetchIncidents}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-md bg-soc-card border border-soc-border hover:border-slate-600 text-sm font-medium text-slate-300 transition-colors self-start"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-sky-400' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-4 flex flex-wrap items-center gap-4 text-xs">
        <div className="flex items-center gap-2 text-slate-400 font-semibold uppercase tracking-wider">
          <Filter className="w-4 h-4 text-sky-400" />
          <span>Filters:</span>
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-3 py-1.5 focus:outline-none focus:border-sky-500"
        >
          <option value="">All Statuses</option>
          <option value="Open">Open</option>
          <option value="Investigating">Investigating</option>
          <option value="Resolved">Resolved</option>
          <option value="Closed">Closed</option>
        </select>

        {/* Severity Filter */}
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-slate-200 rounded px-3 py-1.5 focus:outline-none focus:border-sky-500"
        >
          <option value="">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>

        {(statusFilter || severityFilter) && (
          <button
            onClick={() => {
              setStatusFilter('');
              setSeverityFilter('');
            }}
            className="text-sky-400 hover:text-sky-300 font-medium ml-auto"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Incidents Table */}
      <div className="bg-soc-card border border-soc-border rounded-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-soc-border">
            <tr>
              <th className="py-3 px-4">Code</th>
              <th className="py-3 px-4">Title & Context</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Risk</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Attacker IP</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {incidents.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-12 text-center text-slate-500 font-sans">
                  No incidents match the active filter criteria.
                </td>
              </tr>
            ) : (
              incidents.map((inc) => (
                <tr
                  key={inc.id}
                  onClick={() => navigate(`/incidents/${inc.id}`)}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                >
                  <td className="py-3.5 px-4 font-bold text-sky-400">{inc.incident_code}</td>
                  <td className="py-3.5 px-4 font-sans text-slate-200">
                    <p className="font-semibold text-white">{inc.title}</p>
                    <p className="text-xs text-slate-400 truncate max-w-sm">{inc.description}</p>
                  </td>
                  <td className="py-3.5 px-4 text-slate-300">{inc.attack_category}</td>
                  <td className="py-3.5 px-4">
                    <SeverityBadge severity={inc.severity} />
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-bold text-slate-100">{inc.risk_score.toFixed(0)}</span>
                    <span className="text-slate-500">/100</span>
                  </td>
                  <td className="py-3.5 px-4 font-sans">
                    <StatusBadge status={inc.status} />
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">{inc.source_ip || '—'}</td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/incidents/${inc.id}`);
                      }}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 text-xs font-sans"
                    >
                      <span>Investigate</span>
                      <ArrowUpRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Incident Detail Modal */}
      {selectedIncident && (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4">
          <div className="bg-soc-card border border-soc-border rounded-xl max-w-2xl w-full p-6 space-y-5 shadow-2xl relative">
            <button
              onClick={() => setSelectedIncident(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
                <AlertOctagon className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-sky-400">
                    {selectedIncident.incident_code}
                  </span>
                  <StatusBadge status={selectedIncident.status} />
                  <SeverityBadge severity={selectedIncident.severity} size="sm" />
                </div>
                <h2 className="text-lg font-bold text-white mt-1">{selectedIncident.title}</h2>
              </div>
            </div>

            <p className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              {selectedIncident.description || 'No detailed description provided.'}
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
              <div className="bg-slate-900/80 p-3 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Attack Class</span>
                <span className="text-slate-200 font-semibold">{selectedIncident.attack_category}</span>
              </div>
              <div className="bg-slate-900/80 p-3 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Risk Score</span>
                <span className="text-rose-400 font-semibold">{selectedIncident.risk_score} / 100</span>
              </div>
              <div className="bg-slate-900/80 p-3 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Confidence</span>
                <span className="text-sky-400 font-semibold">
                  {(selectedIncident.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="bg-slate-900/80 p-3 rounded border border-slate-800">
                <span className="text-slate-500 block text-[10px] uppercase">Correlated Events</span>
                <span className="text-slate-200 font-semibold">{selectedIncident.event_count}</span>
              </div>
            </div>

            {selectedIncident.notes && (
              <div className="text-xs space-y-1">
                <span className="text-slate-400 font-semibold uppercase text-[10px]">Analyst Notes:</span>
                <pre className="bg-slate-900/90 p-3 rounded border border-slate-800 font-mono text-slate-300 text-[11px] whitespace-pre-wrap">
                  {selectedIncident.notes}
                </pre>
              </div>
            )}

            {/* Lifecycle Transition Actions */}
            <div className="pt-4 border-t border-soc-border space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Update Lifecycle State:
                </span>
              </div>

              <input
                type="text"
                placeholder="Optional investigation comment..."
                value={actionNotes}
                onChange={(e) => setActionNotes(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />

              <div className="flex flex-wrap gap-2">
                {(['Open', 'Investigating', 'Resolved', 'Closed'] as IncidentStatus[]).map(
                  (st) => (
                    <button
                      key={st}
                      disabled={updating || selectedIncident.status === st}
                      onClick={() => handleStatusChange(st)}
                      className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                        selectedIncident.status === st
                          ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                          : 'bg-soc-panel hover:bg-slate-700 text-slate-200 border border-slate-600'
                      }`}
                    >
                      Set to {st}
                    </button>
                  )
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
