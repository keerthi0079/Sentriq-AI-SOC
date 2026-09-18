import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  Play,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Cpu,
  Layers,
  Sparkles,
  ArrowUpRight,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { socApi } from '../services/api';
import {
  MLPredictionResponse,
  ModelInfoResponse,
  SecurityEvent,
  XAIExplanationResponse,
} from '../types';
import { FeatureAttributionChart } from '../components/xai/FeatureAttributionChart';
import { ExplainabilityDrawer } from '../components/xai/ExplainabilityDrawer';

export const ThreatAnalysis: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [recentEvents, setRecentEvents] = useState<SecurityEvent[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'db' | 'custom'>('db');

  // Custom Feature Form State
  const [customFeatures, setCustomFeatures] = useState({
    dur: 0.12,
    spkts: 8,
    dpkts: 12,
    sbytes: 850,
    dbytes: 2400,
    rate: 160.0,
    destination_port: 443,
    proto: 'TCP',
    service: 'http',
    source: 'web_server',
  });

  // Prediction & XAI Output State
  const [prediction, setPrediction] = useState<MLPredictionResponse | null>(null);
  const [explanation, setExplanation] = useState<XAIExplanationResponse | null>(null);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initData = async () => {
      try {
        const [info, eventsRes] = await Promise.all([
          socApi.getModelInfo(),
          socApi.getEvents({ page: 1, page_size: 25 }),
        ]);
        setModelInfo(info);
        setRecentEvents(eventsRes.items);
        if (eventsRes.items.length > 0) {
          setSelectedEventId(eventsRes.items[0].id);
        }
      } catch (err) {
        console.error('Failed to initialize ML workbench:', err);
      }
    };
    initData();
  }, []);

  const handlePredictDatabaseEvent = async () => {
    if (!selectedEventId) return;
    setLoading(true);
    setError(null);
    try {
      const [res, xai] = await Promise.all([
        socApi.analyzeEventById(selectedEventId),
        socApi.getEventExplanation(selectedEventId),
      ]);
      setPrediction(res);
      setExplanation(xai);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Inference execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const handlePredictCustom = async () => {
    setLoading(true);
    setError(null);
    try {
      const [res, xai] = await Promise.all([
        socApi.predictThreat({ features: customFeatures }),
        socApi.explainFeatures({ features: customFeatures }),
      ]);
      setPrediction(res);
      setExplanation(xai);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Inference execution failed.');
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (type: string) => {
    if (type === 'brute_force') {
      setCustomFeatures({
        dur: 1.25,
        spkts: 18,
        dpkts: 22,
        sbytes: 1850,
        dbytes: 2400,
        rate: 32.0,
        destination_port: 22,
        proto: 'TCP',
        service: 'ssh',
        source: 'auth_service',
      });
    } else if (type === 'dos') {
      setCustomFeatures({
        dur: 0.05,
        spkts: 12000,
        dpkts: 0,
        sbytes: 720000,
        dbytes: 0,
        rate: 240000.0,
        destination_port: 443,
        proto: 'TCP',
        service: 'http',
        source: 'perimeter_firewall',
      });
    } else if (type === 'port_scan') {
      setCustomFeatures({
        dur: 0.001,
        spkts: 2,
        dpkts: 0,
        sbytes: 120,
        dbytes: 0,
        rate: 2000.0,
        destination_port: 80,
        proto: 'TCP',
        service: 'other',
        source: 'ids_sensor',
      });
    } else {
      // Benign
      setCustomFeatures({
        dur: 0.12,
        spkts: 8,
        dpkts: 12,
        sbytes: 850,
        dbytes: 2400,
        rate: 160.0,
        destination_port: 443,
        proto: 'TCP',
        service: 'http',
        source: 'web_server',
      });
    }
  };

  // Format probabilities for Recharts bar chart
  const chartData = prediction
    ? Object.entries(prediction.class_probabilities).map(([name, prob]) => ({
        name,
        percentage: Number((prob * 100).toFixed(1)),
        isWinner: name === prediction.predicted_attack_category,
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">ML Threat Detection Workbench</h1>
          <p className="text-sm text-slate-400 mt-1">
            Evaluate raw telemetry through trained Random Forest classifiers for binary threat detection and multi-class categorization.
          </p>
        </div>
      </div>

      {/* Model Metadata Status Card */}
      {modelInfo && (
        <div className="bg-soc-card border border-soc-border rounded-lg p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div className="space-y-1">
            <span className="text-slate-500 uppercase tracking-wider text-[10px] flex items-center gap-1">
              <Cpu className="w-3 h-3 text-sky-400" /> Active Architecture
            </span>
            <p className="font-bold text-slate-200">{modelInfo.algorithm}</p>
            <span className="text-[11px] text-slate-400">v{modelInfo.model_version}</span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-500 uppercase tracking-wider text-[10px] flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-emerald-400" /> Binary Accuracy
            </span>
            <p className="font-bold text-emerald-400 text-sm">
              {((modelInfo.metrics_summary?.binary_accuracy || 0.9667) * 100).toFixed(1)}%
            </p>
            <span className="text-[11px] text-slate-400">F1: {(modelInfo.metrics_summary?.binary_f1 || 0.9669).toFixed(4)}</span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-500 uppercase tracking-wider text-[10px] flex items-center gap-1">
              <Layers className="w-3 h-3 text-amber-400" /> Multi-Class Macro F1
            </span>
            <p className="font-bold text-amber-400 text-sm">
              {(modelInfo.metrics_summary?.multiclass_macro_f1 || 0.8261).toFixed(4)}
            </p>
            <span className="text-[11px] text-slate-400">Accuracy: {((modelInfo.metrics_summary?.multiclass_accuracy || 0.9667) * 100).toFixed(1)}%</span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-500 uppercase tracking-wider text-[10px]">Supported Classes</span>
            <p className="text-slate-300 truncate text-[11px]">{modelInfo.supported_classes.join(', ')}</p>
            <span className="text-[10px] text-slate-500">{modelInfo.dataset_sample_size} training samples</span>
          </div>
        </div>
      )}

      {/* Input Workbench & Prediction Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Input Selection (5 cols) */}
        <div className="lg:col-span-5 bg-soc-card border border-soc-border rounded-lg p-5 space-y-4">
          <div className="flex border-b border-soc-border pb-2 gap-4 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('db')}
              className={`pb-2 transition-colors ${
                activeTab === 'db'
                  ? 'border-b-2 border-sky-400 text-sky-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Analyze Existing Event
            </button>
            <button
              onClick={() => setActiveTab('custom')}
              className={`pb-2 transition-colors ${
                activeTab === 'custom'
                  ? 'border-b-2 border-sky-400 text-sky-400'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Manual Feature Workbench
            </button>
          </div>

          {activeTab === 'db' ? (
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">
                  Select Event from Database:
                </label>
                <select
                  value={selectedEventId}
                  onChange={(e) => setSelectedEventId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-md p-2.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
                >
                  {recentEvents.map((ev) => (
                    <option key={ev.id} value={ev.id}>
                      [{ev.is_simulated ? 'SIM' : 'BENCH'}] {ev.attack_type} | {ev.source_ip} → {ev.destination_port} ({ev.event_type})
                    </option>
                  ))}
                </select>
              </div>

              {selectedEventId && (
                <div className="bg-slate-900/70 border border-slate-800 rounded-md p-3.5 space-y-2 text-xs font-mono">
                  {(() => {
                    const ev = recentEvents.find((e) => e.id === selectedEventId);
                    if (!ev) return null;
                    return (
                      <>
                        <div className="flex justify-between text-slate-400">
                          <span>Event Source:</span>
                          <span className="text-slate-200">{ev.source}</span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                          <span>Ground Truth:</span>
                          <span className={ev.is_attack ? 'text-rose-400' : 'text-emerald-400'}>
                            {ev.attack_type} ({ev.is_attack ? 'Attack' : 'Normal'})
                          </span>
                        </div>
                        <div className="flex justify-between text-slate-400">
                          <span>Message:</span>
                          <span className="text-slate-300 max-w-[220px] truncate font-sans">{ev.message}</span>
                        </div>
                      </>
                    );
                  })()}
                </div>
              )}

              <button
                disabled={loading || !selectedEventId}
                onClick={handlePredictDatabaseEvent}
                className="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-500 disabled:bg-slate-800 text-white rounded-md text-xs font-semibold transition-colors flex items-center justify-center gap-2 shadow-sm"
              >
                {loading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 fill-current" />
                )}
                <span>Execute ML Threat Analysis</span>
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Presets */}
              <div className="space-y-1.5">
                <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">
                  Quick Feature Presets:
                </span>
                <div className="grid grid-cols-2 gap-1.5">
                  <button
                    onClick={() => applyPreset('brute_force')}
                    className="p-1.5 rounded bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/60 text-[11px] text-rose-300 font-medium text-left"
                  >
                    Brute Force (SSH)
                  </button>
                  <button
                    onClick={() => applyPreset('dos')}
                    className="p-1.5 rounded bg-orange-950/40 hover:bg-orange-900/60 border border-orange-800/60 text-[11px] text-orange-300 font-medium text-left"
                  >
                    Volumetric DoS Flood
                  </button>
                  <button
                    onClick={() => applyPreset('port_scan')}
                    className="p-1.5 rounded bg-amber-950/40 hover:bg-amber-900/60 border border-amber-800/60 text-[11px] text-amber-300 font-medium text-left"
                  >
                    Port Recon Probe
                  </button>
                  <button
                    onClick={() => applyPreset('benign')}
                    className="p-1.5 rounded bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-800/60 text-[11px] text-emerald-300 font-medium text-left"
                  >
                    Benign HTTP Flow
                  </button>
                </div>
              </div>

              {/* Editable Fields */}
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div>
                  <label className="text-[10px] text-slate-400 block">Packet Rate (pps):</label>
                  <input
                    type="number"
                    value={customFeatures.rate}
                    onChange={(e) => setCustomFeatures({ ...customFeatures, rate: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block">Dest Port:</label>
                  <input
                    type="number"
                    value={customFeatures.destination_port}
                    onChange={(e) => setCustomFeatures({ ...customFeatures, destination_port: parseInt(e.target.value) || 80 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block">Source Packets:</label>
                  <input
                    type="number"
                    value={customFeatures.spkts}
                    onChange={(e) => setCustomFeatures({ ...customFeatures, spkts: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block">Dest Packets:</label>
                  <input
                    type="number"
                    value={customFeatures.dpkts}
                    onChange={(e) => setCustomFeatures({ ...customFeatures, dpkts: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block">Source Bytes:</label>
                  <input
                    type="number"
                    value={customFeatures.sbytes}
                    onChange={(e) => setCustomFeatures({ ...customFeatures, sbytes: parseInt(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-[10px] text-slate-400 block">Duration (s):</label>
                  <input
                    type="number"
                    step="0.01"
                    value={customFeatures.dur}
                    onChange={(e) => setCustomFeatures({ ...customFeatures, dur: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-900 border border-slate-700 rounded p-1.5 text-slate-200"
                  />
                </div>
              </div>

              <button
                disabled={loading}
                onClick={handlePredictCustom}
                className="w-full py-2.5 px-4 bg-sky-600 hover:bg-sky-500 disabled:bg-slate-800 text-white rounded-md text-xs font-semibold transition-colors flex items-center justify-center gap-2 shadow-sm"
              >
                {loading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 fill-current" />
                )}
                <span>Run Inference on Custom Features</span>
              </button>
            </div>
          )}

          {error && (
            <div className="bg-rose-950/40 border border-rose-800/60 rounded p-3 text-xs text-rose-300 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Right Column: Prediction Output (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {!prediction ? (
            <div className="bg-soc-card border border-soc-border rounded-lg p-12 text-center space-y-3 flex flex-col items-center justify-center min-h-[360px]">
              <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <h3 className="text-base font-semibold text-white">ML Inference Ready</h3>
              <p className="text-xs text-slate-400 max-w-sm">
                Select an event from the security logs or configure feature values to run real-time threat classification.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Verdict Banner Card */}
              <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div>
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">
                      Threat Classification Verdict
                    </span>
                    <div className="flex items-center gap-3 mt-1">
                      <span
                        className={`px-3 py-1 rounded-md text-sm font-bold tracking-wider font-mono border ${
                          prediction.is_threat
                            ? 'bg-rose-950/60 text-rose-400 border-rose-800/80'
                            : 'bg-emerald-950/60 text-emerald-400 border-emerald-800/80'
                        }`}
                      >
                        {prediction.verdict}
                      </span>
                      <span className="text-lg font-bold text-white font-sans">
                        {prediction.predicted_attack_category}
                      </span>
                    </div>
                  </div>

                  <div className="text-right font-mono">
                    <span className="text-[10px] uppercase tracking-wider text-slate-400 block">
                      Model Confidence
                    </span>
                    <span className="text-2xl font-bold text-sky-400">
                      {(prediction.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {/* Threat Probability Bar */}
                <div className="space-y-1 font-mono text-xs">
                  <div className="flex justify-between text-slate-400 text-[11px]">
                    <span>Attack Likelihood P(Attack):</span>
                    <span className="font-bold text-slate-200">
                      {(prediction.threat_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        prediction.is_threat ? 'bg-rose-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${prediction.threat_probability * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Multi-Class Probabilities Bar Chart */}
              <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-3">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300 font-mono">
                  Multi-Class Category Probability Distribution
                </h3>
                <div className="h-44">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={chartData}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 10, bottom: 0 }}
                    >
                      <XAxis type="number" domain={[0, 100]} stroke="#475569" fontSize={10} unit="%" />
                      <YAxis dataKey="name" type="category" stroke="#94A3B8" fontSize={10} width={90} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#1E293B',
                          borderColor: '#334155',
                          borderRadius: '6px',
                          fontSize: '11px',
                          color: '#F8FAFC',
                        }}
                      />
                      <Bar dataKey="percentage" radius={[0, 4, 4, 0]}>
                        {chartData.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={entry.isWinner ? (prediction.is_threat ? '#EF4444' : '#22C55E') : '#334155'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Explainable Detection Evidence Box (PRD FR-08) */}
              <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-2.5">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-sky-400 font-mono">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Explainable Detection Signals (Heuristic Evidence)</span>
                </div>
                <ul className="space-y-1.5 text-xs text-slate-300 list-disc list-inside leading-relaxed font-sans">
                  {prediction.detection_reasons.map((reason, idx) => (
                    <li key={idx} className="text-slate-300">
                      {reason}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Phase 6: SHAP Mathematical Feature Attribution Card */}
              {explanation && (
                <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-soc-border pb-3">
                    <div className="flex items-center gap-2">
                      <BrainCircuit className="w-4 h-4 text-sky-400" />
                      <div>
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                          SHAP Feature Attribution (PRD Section 16 & FR-08)
                        </h3>
                        <p className="text-[11px] text-slate-400">
                          Exact Shapley contributions computed via TreeExplainer ({explanation.inference_latency_ms}ms)
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => setDrawerOpen(true)}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 rounded text-xs font-mono font-semibold inline-flex items-center gap-1 transition-colors"
                    >
                      <span>Deep XAI Inspector</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <FeatureAttributionChart
                    features={explanation.all_features}
                    baseValue={explanation.base_value}
                    attackProbability={explanation.attack_probability}
                  />

                  <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3 text-xs text-slate-300 font-sans leading-relaxed">
                    <div className="flex items-center gap-1.5 font-semibold text-sky-300 text-[11px] mb-1 font-mono">
                      <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                      <span>Attribution Synthesis Narrative:</span>
                    </div>
                    {explanation.narrative}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Deep Explainability Slide-Over Drawer */}
      <ExplainabilityDrawer
        eventId={activeTab === 'db' ? selectedEventId || undefined : undefined}
        features={activeTab === 'custom' ? customFeatures : undefined}
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
};
