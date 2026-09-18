import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  Flame,
  AlertTriangle,
  Activity,
  RefreshCw,
  ExternalLink,
  Play,
  Pause,
  Zap,
  BellRing,
  X,
  ArrowUpRight,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { Link, useNavigate } from 'react-router-dom';
import { socApi } from '../services/api';
import { Incident, IncidentSummary, SimulationStatus } from '../types';
import { StatCard } from '../components/ui/StatCard';
import { SeverityBadge } from '../components/ui/SeverityBadge';
import { StatusBadge } from '../components/ui/StatusBadge';
import { useSocWebSocket } from '../hooks/useSocWebSocket';
import { formatTimeIST } from '../utils/date';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // WebSocket Live Telemetry Hook
  const {
    status: wsStatus,
    latestAlert,
    latestEvent,
    liveMetrics,
    latestIncident,
    streamStatus: wsStreamStatus,
  } = useSocWebSocket();

  // Primary State
  const [summary, setSummary] = useState<IncidentSummary>({
    total_incidents: 0,
    open_incidents: 0,
    critical_incidents: 0,
    high_risk_incidents: 0,
  });
  const [recentIncidents, setRecentIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Simulation Controls State
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [speed, setSpeed] = useState<number>(1);
  const [streamStats, setStreamStats] = useState<SimulationStatus | null>(null);
  const [injecting, setInjecting] = useState<boolean>(false);
  const [injectionNotice, setInjectionNotice] = useState<string | null>(null);
  const [dismissedAlertId, setDismissedAlertId] = useState<string | null>(null);

  // Telemetry Chart Trend Points
  const [trendData, setTrendData] = useState([
    { time: '00:00', normal: 120, threats: 4 },
    { time: '04:00', normal: 80, threats: 2 },
    { time: '08:00', normal: 260, threats: 12 },
    { time: '12:00', normal: 420, threats: 28 },
    { time: '16:00', normal: 380, threats: 19 },
    { time: '20:00', normal: 290, threats: 14 },
    { time: 'Live', normal: 310, threats: 22 },
  ]);

  const [categoryDistribution, setCategoryDistribution] = useState([
    { name: 'Brute Force', count: 18, color: '#EF4444' },
    { name: 'DoS / Flood', count: 12, color: '#F97316' },
    { name: 'Port Scan', count: 9, color: '#F59E0B' },
    { name: 'Web Attack', count: 5, color: '#38BDF8' },
    { name: 'Exploit Attempt', count: 3, color: '#14B8A6' },
  ]);

  // Initial Data Fetch
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumData, incData, simData] = await Promise.all([
        socApi.getIncidentSummary(),
        socApi.getIncidents({ page: 1, page_size: 5 }),
        socApi.getSimulationStatus(),
      ]);
      setSummary(sumData);
      setRecentIncidents(incData.items);
      setIsStreaming(simData.is_running);
      setSpeed(simData.speed);
      setStreamStats(simData);
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError('Unable to load security data. Check backend connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Sync stream status from WebSocket updates
  useEffect(() => {
    if (wsStreamStatus) {
      setIsStreaming(wsStreamStatus.is_running);
      setSpeed(wsStreamStatus.speed);
      setStreamStats(wsStreamStatus);
    }
  }, [wsStreamStatus]);

  // Sync real-time metrics from WebSocket
  useEffect(() => {
    if (liveMetrics) {
      setStreamStats((prev) =>
        prev
          ? {
              ...prev,
              events_generated: liveMetrics.total_events,
              threats_detected: liveMetrics.threats_detected,
              incidents_triggered: liveMetrics.incidents_triggered,
              is_running: liveMetrics.is_running,
              speed: liveMetrics.stream_speed,
            }
          : null
      );
    }
  }, [liveMetrics]);

  // Handle incoming live event updates for trend chart
  useEffect(() => {
    if (latestEvent) {
      setTrendData((prev) => {
        const next = [...prev];
        const lastIdx = next.length - 1;
        if (latestEvent.is_attack) {
          next[lastIdx] = { ...next[lastIdx], threats: next[lastIdx].threats + 1 };
          setCategoryDistribution((cats) =>
            cats.map((c) =>
              c.name.toLowerCase().includes(latestEvent.attack_type.toLowerCase())
                ? { ...c, count: c.count + 1 }
                : c
            )
          );
        } else {
          next[lastIdx] = { ...next[lastIdx], normal: next[lastIdx].normal + 1 };
        }
        return next;
      });
    }
  }, [latestEvent]);

  // Handle incoming live incidents dynamically
  useEffect(() => {
    if (latestIncident) {
      setRecentIncidents((prev) => {
        const existsIndex = prev.findIndex((item) => item.id === latestIncident.id);
        if (existsIndex >= 0) {
          const updated = [...prev];
          updated[existsIndex] = { ...updated[existsIndex], ...latestIncident };
          return updated;
        } else {
          return [latestIncident as Incident, ...prev.slice(0, 4)];
        }
      });

      setSummary((prev) => ({
        ...prev,
        total_incidents: prev.total_incidents + 1,
        open_incidents: prev.open_incidents + 1,
        critical_incidents:
          latestIncident.severity === 'Critical'
            ? prev.critical_incidents + 1
            : prev.critical_incidents,
        high_risk_incidents:
          latestIncident.risk_score >= 60
            ? prev.high_risk_incidents + 1
            : prev.high_risk_incidents,
      }));
    }
  }, [latestIncident]);

  // Simulation Controls Handlers
  const handleToggleStream = async () => {
    try {
      if (isStreaming) {
        const res = await socApi.stopSimulation();
        setIsStreaming(res.is_running);
      } else {
        const res = await socApi.startSimulation();
        setIsStreaming(res.is_running);
      }
    } catch (err) {
      console.error('Failed to toggle stream:', err);
    }
  };

  const handleChangeSpeed = async (newSpeed: number) => {
    try {
      const res = await socApi.setSimulationSpeed(newSpeed);
      setSpeed(res.speed);
    } catch (err) {
      console.error('Failed to change stream speed:', err);
    }
  };

  const handleInjectScenario = async (scenario: string, label: string) => {
    setInjecting(true);
    try {
      const res = await socApi.injectSimulationScenario(scenario);
      setInjectionNotice(`Injected ${res.events_queued} events: ${label}`);
      setTimeout(() => setInjectionNotice(null), 4000);
    } catch (err) {
      console.error('Failed to inject scenario:', err);
    } finally {
      setInjecting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls Bar */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-white tracking-tight">Security Operations Dashboard</h1>
              {/* WebSocket Telemetry Status Badge */}
              <div
                className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono font-bold tracking-wider border ${
                  wsStatus === 'connected'
                    ? 'bg-emerald-950/60 border-emerald-800/80 text-emerald-400'
                    : wsStatus === 'connecting'
                    ? 'bg-amber-950/60 border-amber-800/80 text-amber-400'
                    : 'bg-rose-950/60 border-rose-800/80 text-rose-400'
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    wsStatus === 'connected'
                      ? 'bg-emerald-400 animate-pulse'
                      : wsStatus === 'connecting'
                      ? 'bg-amber-400 animate-ping'
                      : 'bg-rose-500'
                  }`}
                />
                <span>
                  {wsStatus === 'connected'
                    ? 'TELEMETRY: LIVE'
                    : wsStatus === 'connecting'
                    ? 'CONNECTING...'
                    : 'OFFLINE'}
                </span>
              </div>
            </div>
            <p className="text-sm text-slate-400 mt-1">
              Real-time threat telemetry, on-the-fly ML detection, and sliding-window attack correlation.
            </p>
          </div>

          <button
            onClick={loadData}
            disabled={loading}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-md bg-soc-card border border-soc-border hover:border-slate-600 text-sm font-medium text-slate-300 transition-colors self-start"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-sky-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Phase 5: Interactive Telemetry Simulation Control Bar */}
        <div className="bg-soc-card border border-soc-border rounded-lg p-3.5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
          <div className="flex flex-wrap items-center gap-3">
            {/* Stream Play/Pause Toggle */}
            <button
              onClick={handleToggleStream}
              className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded text-xs font-bold transition-all ${
                isStreaming
                  ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-900/30'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-900/30'
              }`}
            >
              {isStreaming ? (
                <>
                  <Pause className="w-3.5 h-3.5 fill-current" />
                  <span>Pause Stream</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>Start Live Stream</span>
                </>
              )}
            </button>

            {/* Speed Selector */}
            <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded p-0.5 text-xs font-mono">
              <span className="text-[10px] text-slate-500 px-2 uppercase font-sans">Rate:</span>
              {[1, 2, 5].map((s) => (
                <button
                  key={s}
                  onClick={() => handleChangeSpeed(s)}
                  className={`px-2 py-0.5 rounded text-xs font-bold transition-colors ${
                    speed === s
                      ? 'bg-sky-500 text-white'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {s}x
                </button>
              ))}
            </div>

            {/* Scenario Injection Quick Buttons */}
            <div className="flex items-center gap-1.5 pl-2 border-l border-slate-800">
              <span className="text-[11px] text-slate-400 font-semibold flex items-center gap-1">
                <Zap className="w-3 h-3 text-amber-400" />
                <span>Inject Scenario:</span>
              </span>

              <button
                disabled={injecting}
                onClick={() => handleInjectScenario('brute_force', 'Brute Force (PRD Sec 12)')}
                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 border border-slate-700 rounded text-xs font-medium transition-colors"
              >
                Brute Force
              </button>
              <button
                disabled={injecting}
                onClick={() => handleInjectScenario('dos', 'Volumetric DoS Flood')}
                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 border border-slate-700 rounded text-xs font-medium transition-colors"
              >
                DoS Flood
              </button>
              <button
                disabled={injecting}
                onClick={() => handleInjectScenario('port_scan', 'Recon Port Probe')}
                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 border border-slate-700 rounded text-xs font-medium transition-colors"
              >
                Port Recon
              </button>
            </div>
          </div>

          {/* Telemetry Stream KPI Counters */}
          <div className="flex items-center gap-3 text-xs font-mono text-slate-400 self-end sm:self-auto">
            {streamStats && (
              <div className="flex items-center gap-3 bg-slate-900/80 px-3 py-1.5 rounded border border-slate-800">
                <span>
                  Events: <strong className="text-white">{streamStats.events_generated}</strong>
                </span>
                <span className="text-slate-600">|</span>
                <span>
                  Threats: <strong className="text-rose-400">{streamStats.threats_detected}</strong>
                </span>
                <span className="text-slate-600">|</span>
                <span>
                  Queue: <strong className="text-amber-400">{streamStats.queue_size}</strong>
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Injection Toast Notification */}
        {injectionNotice && (
          <div className="bg-sky-950/60 border border-sky-800 text-sky-200 text-xs px-4 py-2 rounded-lg flex items-center justify-between animate-fadeIn">
            <span className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400 animate-bounce" />
              <span>{injectionNotice}</span>
            </span>
            <span className="text-[10px] font-mono text-sky-400">Pushed to ingestion stream</span>
          </div>
        )}

        {/* Phase 5: Live Detection Alert Ticker Banner */}
        {latestAlert && latestAlert.event_id !== dismissedAlertId && (
          <div className="bg-rose-950/40 border border-rose-800/80 rounded-lg p-3.5 flex items-center justify-between gap-3 animate-pulse">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 shrink-0">
                <BellRing className="w-4 h-4" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-rose-400 uppercase tracking-wider">
                    Live Threat Detected:
                  </span>
                  <span className="font-bold text-white text-xs">{latestAlert.attack_category}</span>
                  <SeverityBadge severity={latestAlert.severity} size="sm" />
                  <span className="text-[10px] font-mono text-slate-400">
                    Conf: {(latestAlert.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5 font-sans">
                  Origin <span className="font-mono text-rose-300 font-semibold">{latestAlert.source_ip}</span> targeting{' '}
                  <span className="font-mono text-slate-200">{latestAlert.target_asset}</span>: {latestAlert.message}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Link
                to="/incidents"
                className="px-2.5 py-1 bg-rose-900/60 hover:bg-rose-800 border border-rose-700 text-white rounded text-xs font-semibold inline-flex items-center gap-1"
              >
                <span>Investigate</span>
                <ArrowUpRight className="w-3 h-3" />
              </Link>
              <button
                onClick={() => setDismissedAlertId(latestAlert.event_id)}
                className="p-1 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Error State Banner */}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800/60 rounded-lg p-4 text-rose-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={loadData}
            className="px-3 py-1 bg-rose-900/60 hover:bg-rose-800/80 rounded border border-rose-700 text-xs font-semibold text-white"
          >
            Retry
          </button>
        </div>
      )}

      {/* KPI Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Incidents"
          value={summary.total_incidents}
          subtitle="All recorded incidents"
          icon={Activity}
          variant="accent"
        />
        <StatCard
          title="Active Investigations"
          value={summary.open_incidents}
          subtitle="Open or investigating"
          icon={AlertTriangle}
          variant="warning"
        />
        <StatCard
          title="Critical Threats"
          value={summary.critical_incidents}
          subtitle="High priority response"
          icon={Flame}
          variant="danger"
        />
        <StatCard
          title="High Risk Level"
          value={summary.high_risk_incidents}
          subtitle="Risk score ≥ 60.0"
          icon={ShieldAlert}
          variant="danger"
        />
      </div>

      {/* Visual Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Trend Area Chart */}
        <div className="lg:col-span-2 bg-soc-card border border-soc-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <span>Event Telemetry Trend</span>
                {isStreaming && (
                  <span className="flex h-2 w-2 relative">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
                  </span>
                )}
              </h3>
              <p className="text-xs text-slate-400">Normal vs Suspicious network events over rolling window</p>
            </div>
            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-slate-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-slate-600" /> Benign
              </span>
              <span className="flex items-center gap-1.5 text-rose-400">
                <span className="w-2.5 h-2.5 rounded-sm bg-rose-500" /> Threats
              </span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="threatGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="normalGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#475569" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#475569" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" fontSize={11} />
                <YAxis stroke="#475569" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1E293B',
                    borderColor: '#334155',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: '#F8FAFC',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="normal"
                  stroke="#64748B"
                  fillOpacity={1}
                  fill="url(#normalGrad)"
                />
                <Area
                  type="monotone"
                  dataKey="threats"
                  stroke="#EF4444"
                  fillOpacity={1}
                  fill="url(#threatGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Attack Category Breakdown Bar Chart */}
        <div className="bg-soc-card border border-soc-border rounded-lg p-5">
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-white">Threat Category Distribution</h3>
            <p className="text-xs text-slate-400">Observed attack patterns</p>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={categoryDistribution}
                layout="vertical"
                margin={{ top: 10, right: 20, left: 15, bottom: 0 }}
              >
                <XAxis type="number" stroke="#475569" fontSize={10} />
                <YAxis dataKey="name" type="category" stroke="#94A3B8" fontSize={10} width={85} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1E293B',
                    borderColor: '#334155',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: '#F8FAFC',
                  }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {categoryDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Incidents Table */}
      <div className="bg-soc-card border border-soc-border rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <span>Recent Security Incidents</span>
              <span className="text-xs font-mono font-normal text-slate-400">
                (Live correlation feed)
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Correlated security incidents stored in PostgreSQL
            </p>
          </div>
          <Link
            to="/incidents"
            className="text-xs text-sky-400 hover:text-sky-300 inline-flex items-center gap-1 font-medium"
          >
            <span>View All Incidents</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </Link>
        </div>

        {recentIncidents.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">
            No incidents found in the database. Run or start telemetry to generate live data.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-soc-border">
                <tr>
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Incident Title</th>
                  <th className="py-3 px-4">Attack Category</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Risk Score</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Source IP</th>
                  <th className="py-3 px-4 text-right">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {recentIncidents.map((inc) => (
                  <tr
                    key={inc.id}
                    onClick={() => navigate(`/incidents/${inc.id}`)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                  >
                    <td className="py-3 px-4 font-semibold text-sky-400 group-hover:text-sky-300">{inc.incident_code}</td>
                    <td className="py-3 px-4 font-sans text-slate-200 max-w-xs truncate">
                      {inc.title}
                    </td>
                    <td className="py-3 px-4 text-slate-300">{inc.attack_category}</td>
                    <td className="py-3 px-4">
                      <SeverityBadge severity={inc.severity} size="sm" />
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="w-8 font-bold">{inc.risk_score.toFixed(0)}</span>
                        <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-full ${
                              inc.risk_score >= 80
                                ? 'bg-rose-500'
                                : inc.risk_score >= 60
                                ? 'bg-orange-500'
                                : inc.risk_score >= 30
                                ? 'bg-amber-500'
                                : 'bg-emerald-500'
                            }`}
                            style={{ width: `${inc.risk_score}%` }}
                          />
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-sans">
                      <StatusBadge status={inc.status} />
                    </td>
                    <td className="py-3 px-4 text-slate-400">{inc.source_ip || 'Internal'}</td>
                    <td className="py-3 px-4 text-right text-slate-400 font-mono text-[11px]">
                      {formatTimeIST(inc.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
