import React, { useEffect, useState } from 'react';
import {
  Search,
  RefreshCw,
  X,
  Play,
  Database,
  CheckCircle2,
  Copy,
  Check,
  BrainCircuit,
  Upload,
} from 'lucide-react';
import { socApi } from '../services/api';
import { EventStats, SecurityEvent } from '../types';
import { SeverityBadge } from '../components/ui/SeverityBadge';
import { ExplainabilityDrawer } from '../components/xai/ExplainabilityDrawer';
import { formatDateTimeIST } from '../utils/date';

export const SecurityLogs: React.FC = () => {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [stats, setStats] = useState<EventStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalCount, setTotalCount] = useState<number>(0);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [attackTypeFilter, setAttackTypeFilter] = useState<string>('');
  const [sourceFilter, setSourceFilter] = useState<string>('');
  const [simulatedFilter, setSimulatedFilter] = useState<string>('');

  // Drawer / Inspection
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);
  const [explainEventId, setExplainEventId] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [notification, setNotification] = useState<string | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const [eventsRes, statsRes] = await Promise.all([
        socApi.getEvents({
          page,
          page_size: 15,
          search: searchTerm || undefined,
          severity: severityFilter || undefined,
          attack_type: attackTypeFilter || undefined,
          source: sourceFilter || undefined,
          is_simulated: simulatedFilter === '' ? undefined : simulatedFilter === 'true',
        }),
        socApi.getEventStats(),
      ]);
      setEvents(eventsRes.items);
      setTotalPages(eventsRes.total_pages);
      setTotalCount(eventsRes.total);
      setStats(statsRes);
    } catch (err) {
      console.error('Failed to load security events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, severityFilter, attackTypeFilter, sourceFilter, simulatedFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  const handleSimulate = async (scenario: string, count: number = 8) => {
    setSimulating(true);
    try {
      const res = await socApi.simulateScenario(scenario, count);
      setNotification(res.message);
      await fetchLogs();
      setTimeout(() => setNotification(null), 5000);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleIngestBenchmark = async (dataset: string = 'unsw') => {
    setSimulating(true);
    try {
      const res = await socApi.ingestBenchmark(dataset);
      setNotification(`Ingested ${res.records_ingested} authentic records from ${res.benchmark_source} benchmark dataset.`);
      await fetchLogs();
      setTimeout(() => setNotification(null), 5000);
    } catch (err) {
      console.error('Benchmark ingestion failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSimulating(true);
    try {
      const res = await socApi.uploadCsvDataset(file);
      setNotification(res.message);
      await fetchLogs();
      setTimeout(() => setNotification(null), 6000);
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'File upload failed';
      setNotification(`Upload Error: ${detail}`);
    } finally {
      setSimulating(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const copyJson = (data: any) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Security Logs Explorer</h1>
          <p className="text-sm text-slate-400 mt-1">
            Standardized, normalized security telemetry from public benchmark datasets and simulated streams.
            Standardized, normalized security telemetry from public benchmark datasets (UNSW-NB15 & CIC-IDS2017) and simulated streams.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchLogs()}
            disabled={loading}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-md bg-soc-card border border-soc-border hover:border-slate-600 text-sm font-medium text-slate-300 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Notification Toast Banner */}
      {notification && (
        <div className="bg-sky-950/60 border border-sky-800/80 rounded-lg p-3 text-xs text-sky-300 flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-sky-400 shrink-0" />
            <span>{notification}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-sky-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Telemetry Stats Banner */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="bg-soc-card border border-soc-border rounded-lg p-3.5">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 block">Total Processed Events</span>
            <span className="text-xl font-bold font-mono text-white mt-1 block">{stats.total_events}</span>
          </div>
          <div className="bg-soc-card border border-soc-border rounded-lg p-3.5">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 block">Threat Detections</span>
            <span className="text-xl font-bold font-mono text-rose-400 mt-1 block">{stats.threat_events}</span>
          </div>
          <div className="bg-soc-card border border-soc-border rounded-lg p-3.5">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 block">Benign Network Flows</span>
            <span className="text-xl font-bold font-mono text-emerald-400 mt-1 block">{stats.benign_events}</span>
          </div>
          <div className="bg-soc-card border border-soc-border rounded-lg p-3.5">
            <span className="text-[10px] uppercase tracking-wider text-slate-500 block">UNSW-NB15 Benchmark Flows</span>
            <span className="text-[10px] uppercase tracking-wider text-slate-500 block">Benchmark Flow Records</span>
            <span className="text-xl font-bold font-mono text-sky-400 mt-1 block">
              {stats.source_distribution['unsw_nb15_network_tap'] || 0}
              {(stats.source_distribution['unsw_nb15_network_tap'] || 0) + (stats.source_distribution['cic_ids2017_network_tap'] || 0)}
              <span className="text-[11px] font-normal text-slate-400 ml-2">
                (UNSW: {stats.source_distribution['unsw_nb15_network_tap'] || 0} | CIC: {stats.source_distribution['cic_ids2017_network_tap'] || 0})
              </span>
            </span>
          </div>
        </div>
      )}

      {/* Scenario Injection & Action Bar */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Play className="w-3.5 h-3.5 text-sky-400" />
            Generate Security Scenario:
            Security Ingestion & Scenarios:
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            disabled={simulating}
            onClick={() => handleSimulate('brute_force', 8)}
            className="px-3 py-1.5 rounded bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/60 text-xs text-rose-300 font-medium transition-colors"
          >
            Brute Force (PRD Sec 12)
          </button>
          <button
            disabled={simulating}
            onClick={() => handleSimulate('dos', 6)}
            className="px-3 py-1.5 rounded bg-orange-950/40 hover:bg-orange-900/60 border border-orange-800/60 text-xs text-orange-300 font-medium transition-colors"
          >
            DoS Volumetric Burst
          </button>
          <button
            disabled={simulating}
            onClick={() => handleSimulate('port_scan', 10)}
            className="px-3 py-1.5 rounded bg-amber-950/40 hover:bg-amber-900/60 border border-amber-800/60 text-xs text-amber-300 font-medium transition-colors"
          >
            Port Recon Scan
          </button>
          <button
            disabled={simulating}
            onClick={() => handleSimulate('benign', 10)}
            className="px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 font-medium transition-colors"
          >
            Benign Traffic
          </button>
          <button
            disabled={simulating}
            onClick={() => handleIngestBenchmark('unsw')}
            className="px-3 py-1.5 rounded bg-sky-950/50 hover:bg-sky-900/60 border border-sky-800/60 text-xs text-sky-300 font-medium inline-flex items-center gap-1.5 transition-colors"
            title="Load authentic UNSW-NB15 flow benchmark dataset sample"
          >
            <Database className="w-3.5 h-3.5 text-sky-400" />
            Load UNSW-NB15
          </button>
          <button
            disabled={simulating}
            onClick={() => handleIngestBenchmark('cic')}
            className="px-3 py-1.5 rounded bg-indigo-950/50 hover:bg-indigo-900/60 border border-indigo-800/60 text-xs text-indigo-300 font-medium inline-flex items-center gap-1.5 transition-colors"
            title="Load authentic CIC-IDS2017 bidirectional flow benchmark dataset sample"
          >
            <Database className="w-3.5 h-3.5 text-indigo-400" />
            Load CIC-IDS2017
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".csv"
            className="hidden"
          />
          <button
            disabled={simulating}
            onClick={() => fileInputRef.current?.click()}
            className="px-3 py-1.5 rounded bg-emerald-950/50 hover:bg-emerald-900/60 border border-emerald-800/60 text-xs text-emerald-300 font-medium inline-flex items-center gap-1.5 transition-colors shadow-sm"
            title="Manually browse and upload a custom CSV dataset file from your machine"
          >
            <Upload className="w-3.5 h-3.5 text-emerald-400" />
            Upload Dataset CSV
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-4 flex flex-wrap items-center gap-3 text-xs">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 min-w-[220px]">
          <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search IP, username, keyword, message..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-md pl-9 pr-3 py-1.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-xs"
          />
        </form>

        {/* Severity Filter */}
        <select
          value={severityFilter}
          onChange={(e) => {
            setSeverityFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-700 text-slate-300 rounded px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
        >
          <option value="">All Severities</option>
          <option value="Critical">Critical</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>

        {/* Attack Type Filter */}
        <select
          value={attackTypeFilter}
          onChange={(e) => {
            setAttackTypeFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-700 text-slate-300 rounded px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
        >
          <option value="">All Attack Types</option>
          <option value="Normal">Normal (Benign)</option>
          <option value="Brute Force">Brute Force</option>
          <option value="DoS">DoS / Flood</option>
          <option value="Port Scan">Port Scan</option>
          <option value="Exploitation">Exploitation</option>
          <option value="Web Attack">Web Attack</option>
        </select>

        {/* Source Filter */}
        <select
          value={sourceFilter}
          onChange={(e) => {
            setSourceFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-700 text-slate-300 rounded px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
        >
          <option value="">All Sources</option>
          <option value="auth_service">auth_service</option>
          <option value="perimeter_firewall">perimeter_firewall</option>
          <option value="ids_sensor">ids_sensor</option>
          <option value="endpoint_audit">endpoint_audit</option>
          <option value="web_server">web_server</option>
          <option value="unsw_nb15_network_tap">unsw_nb15_network_tap</option>
        </select>

        {/* Origin Filter */}
        <select
          value={simulatedFilter}
          onChange={(e) => {
            setSimulatedFilter(e.target.value);
            setPage(1);
          }}
          className="bg-slate-900 border border-slate-700 text-slate-300 rounded px-2.5 py-1.5 focus:outline-none focus:border-sky-500"
        >
          <option value="">All Origins</option>
          <option value="false">Authentic Benchmark</option>
          <option value="true">Simulated Demo</option>
        </select>

        {(searchTerm || severityFilter || attackTypeFilter || sourceFilter || simulatedFilter) && (
          <button
            onClick={() => {
              setSearchTerm('');
              setSeverityFilter('');
              setAttackTypeFilter('');
              setSourceFilter('');
              setSimulatedFilter('');
              setPage(1);
            }}
            className="text-sky-400 hover:text-sky-300 font-medium"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Security Logs Table */}
      <div className="bg-soc-card border border-soc-border rounded-lg overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/70 text-slate-400 uppercase tracking-wider font-semibold border-b border-soc-border">
              <tr>
                <th className="py-3 px-3.5">Timestamp (IST)</th>
                <th className="py-3 px-3.5">Origin</th>
                <th className="py-3 px-3.5">Severity</th>
                <th className="py-3 px-3.5">Attack Category</th>
                <th className="py-3 px-3.5">Event Source & Type</th>
                <th className="py-3 px-3.5">Source → Destination</th>
                <th className="py-3 px-3.5">Security Message</th>
                <th className="py-3 px-3.5 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {events.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500 font-sans">
                    No security events match the selected filters.
                  </td>
                </tr>
              ) : (
                events.map((ev) => (
                  <tr
                    key={ev.id}
                    onClick={() => setSelectedEvent(ev)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-3.5 text-slate-400 whitespace-nowrap text-[11px] font-mono">
                      {formatDateTimeIST(ev.timestamp)}
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap font-sans">
                      {ev.is_simulated ? (
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          SIMULATED
                        </span>
                      ) : (
                        <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-sky-950/70 text-sky-400 border border-sky-800/60">
                          BENCHMARK
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap font-sans">
                      <SeverityBadge severity={ev.severity} size="sm" />
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap text-slate-200 font-medium">
                      {ev.attack_type}
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap text-slate-400">
                      <span className="text-slate-300 font-sans">{ev.source}</span>
                      <span className="text-slate-600 block text-[10px]">{ev.event_type}</span>
                    </td>
                    <td className="py-3 px-3.5 whitespace-nowrap text-slate-300 text-[11px]">
                      <span>{ev.source_ip}</span>
                      <span className="text-slate-600 mx-1">→</span>
                      <span className="text-slate-400">{ev.destination_ip}:{ev.destination_port || '—'}</span>
                    </td>
                    <td className="py-3 px-3.5 max-w-sm font-sans text-slate-300 text-xs truncate">
                      {ev.message}
                    </td>
                    <td className="py-3 px-3.5 text-right font-sans">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedEvent(ev);
                        }}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 text-xs"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="bg-slate-900/60 border-t border-soc-border px-4 py-3 flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>
            Showing <strong className="text-white">{events.length}</strong> of{' '}
            <strong className="text-white">{totalCount}</strong> events
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1 rounded bg-soc-card border border-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              Previous
            </button>
            <span className="px-2">
              Page <strong className="text-white">{page}</strong> of <strong className="text-white">{totalPages}</strong>
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="px-3 py-1 rounded bg-soc-card border border-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Event Inspection Slide-Over Drawer */}
      {selectedEvent && (
        <div className="fixed inset-0 z-50 bg-black/75 flex justify-end">
          <div className="bg-soc-card border-l border-soc-border w-full max-w-xl h-full p-6 space-y-6 overflow-y-auto shadow-2xl flex flex-col justify-between">
            <div className="space-y-6">
              {/* Drawer Header */}
              <div className="flex items-start justify-between border-b border-soc-border pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <SeverityBadge severity={selectedEvent.severity} />
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {selectedEvent.is_simulated ? 'SIMULATED DATA' : 'UNSW-NB15 BENCHMARK'}
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-white tracking-tight">{selectedEvent.event_type}</h2>
                  <p className="text-xs text-slate-500 font-mono mt-0.5">{selectedEvent.id}</p>
                </div>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Message Banner */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3.5 text-xs text-slate-200 font-sans leading-relaxed">
                {selectedEvent.message}
              </div>

              {/* Flow Details Grid */}
              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="bg-slate-900/60 p-3 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px] uppercase">Attack Category</span>
                  <span className="text-rose-400 font-bold text-sm mt-0.5 block">{selectedEvent.attack_type}</span>
                </div>
                <div className="bg-slate-900/60 p-3 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px] uppercase">Protocol & Port</span>
                  <span className="text-slate-200 font-semibold text-sm mt-0.5 block">
                    {selectedEvent.protocol} : {selectedEvent.destination_port || '—'}
                  </span>
                </div>
                <div className="bg-slate-900/60 p-3 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px] uppercase">Source Endpoint</span>
                  <span className="text-sky-400 font-semibold mt-0.5 block truncate">{selectedEvent.source_ip}</span>
                </div>
                <div className="bg-slate-900/60 p-3 rounded border border-slate-800">
                  <span className="text-slate-500 block text-[10px] uppercase">Destination Target</span>
                  <span className="text-slate-300 font-semibold mt-0.5 block truncate">{selectedEvent.destination_ip}</span>
                </div>
                {selectedEvent.user_identity && (
                  <div className="col-span-2 bg-slate-900/60 p-3 rounded border border-slate-800">
                    <span className="text-slate-500 block text-[10px] uppercase">User Identity Subject</span>
                    <span className="text-amber-400 font-semibold mt-0.5 block">{selectedEvent.user_identity}</span>
                  </div>
                )}
              </div>

              {/* Raw Benchmark Features JSON Viewer */}
              {selectedEvent.raw_features && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                      Raw Feature Vectors (JSON):
                    </span>
                    <button
                      onClick={() => copyJson(selectedEvent.raw_features)}
                      className="text-xs text-sky-400 hover:text-sky-300 inline-flex items-center gap-1 font-mono"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
                    </button>
                  </div>
                  <pre className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-[11px] font-mono text-emerald-400 overflow-x-auto max-h-64 leading-relaxed">
                    {JSON.stringify(selectedEvent.raw_features, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            {/* Footer Actions */}
            <div className="pt-4 border-t border-soc-border flex gap-3">
              <button
                onClick={() => setExplainEventId(selectedEvent.id)}
                className="flex-1 py-2 px-4 rounded-md bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors shadow-lg shadow-sky-900/20 font-mono"
              >
                <BrainCircuit className="w-4 h-4" />
                <span>Explain with SHAP (XAI)</span>
              </button>
              <button
                onClick={() => setSelectedEvent(null)}
                className="py-2 px-4 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Deep Explainability Slide-Over Drawer */}
      <ExplainabilityDrawer
        eventId={explainEventId || undefined}
        isOpen={!!explainEventId}
        onClose={() => setExplainEventId(null)}
      />
    </div>
  );
};
