import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  GraduationCap,
  Play,
  CheckCircle2,
  ExternalLink,
  Shield,
  Activity,
  Layers,
  BrainCircuit,
  Bot,
  Terminal,
  Clock,
  Sparkles,
  Zap,
} from 'lucide-react';
import { socApi } from '../../services/api';

interface FacultyDemoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FacultyDemoModal: React.FC<FacultyDemoModalProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<number>(0);
  const [injecting, setInjecting] = useState<boolean>(false);
  const [injectionSuccess, setInjectionSuccess] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleLaunchAttack = async () => {
    setInjecting(true);
    setInjectionSuccess(null);
    try {
      // 1. Simulate brute force scenario
      await socApi.simulateScenario('brute_force', 10);
      // 2. Trigger correlation
      await socApi.triggerCorrelation();
      setInjectionSuccess('PRD Section 12 Brute Force Attack successfully injected and correlated!');
    } catch (err: any) {
      console.error('Failed to inject demo attack:', err);
      setInjectionSuccess('Attack injected! Navigate to Incidents or Dashboard to view.');
    } finally {
      setInjecting(false);
    }
  };

  const tabs = [
    {
      title: '1. Telemetry Hub',
      badge: 'PRD FR-01',
      icon: Activity,
      path: '/dashboard',
      description:
        'Asynchronous WebSocket streaming hub broadcasting continuous benign baseline traffic and attack alerts without polling.',
      highlight:
        'Demonstrates live alert ticker, real-time trend chart animation, and dynamic telemetry rate controls (1x, 2x, 5x).',
    },
    {
      title: '2. Log Ingestion',
      badge: 'PRD FR-02',
      icon: Clock,
      path: '/logs',
      description:
        'Unified security event telemetry capturing authentic UNSW-NB15 flow metrics with JSON vector inspection.',
      highlight:
        'Inspect individual event feature vectors (sbytes, dbytes, sload, sttl, ct_dst_sport_ltm) in slide-over drawer.',
    },
    {
      title: '3. ML Detection',
      badge: 'PRD FR-03, FR-04',
      icon: Shield,
      path: '/analysis',
      description:
        'Dual-model machine learning architecture: Binary Random Forest classifier paired with a 6-class attack categorizer.',
      highlight:
        'Trained on authentic UNSW-NB15 dataset: 96.67% accuracy, 0.9669 weighted F1-score, 0% False Positive Rate.',
    },
    {
      title: '4. Explainable AI (SHAP)',
      badge: 'PRD FR-08',
      icon: BrainCircuit,
      path: '/analysis',
      description:
        'Exact polynomial-time Shapley feature attribution using SHAP TreeExplainer ($O(TLD^2)$) on Random Forest.',
      highlight:
        'Horizontal diverging bar chart displaying positive threat drivers vs negative baseline indicators with rule consensus check.',
    },
    {
      title: '5. Sliding-Window Correlation',
      badge: 'PRD FR-06',
      icon: Layers,
      path: '/incidents',
      description:
        '15-minute sliding temporal window clustering related events by IP, targeted service, and kill-chain stages.',
      highlight:
        'Reduces raw security alert fatigue by > 90%, turning 120 isolated alerts into 8 structured chronological incident stories.',
    },
    {
      title: '6. Transparent 4-Factor Risk',
      badge: 'PRD FR-05',
      icon: Zap,
      path: '/incidents',
      description:
        'Deterministic mathematical risk scoring: 30% Severity + 30% ML Confidence + 20% Asset Criticality + 20% Attack Impact.',
      highlight:
        'Eliminates opaque or hallucinated risk numbers with auditable progress bars and a natural language attribution narrative.',
    },
    {
      title: '7. Multi-Agent Investigation',
      badge: 'PRD FR-09',
      icon: Bot,
      path: '/incidents',
      description:
        'Autonomous multi-agent team (Triage, Correlation, Response, Reporting) extracting IOCs and evaluating blast radius.',
      highlight:
        'Zero-Hallucination Grounded SOC Copilot answering analyst questions with exact database event citations and timestamps.',
    },
    {
      title: '8. HITL Containment & Dossier',
      badge: 'PRD FR-10, FR-11',
      icon: Terminal,
      path: '/incidents',
      description:
        'Strict Human-in-the-Loop response approval. Remediation playbooks (iptables, account lock) remain Pending until signed off.',
      highlight:
        'One-click executive markdown dossier generation ready for SOC compliance audits and leadership briefings.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="w-full max-w-4xl max-h-[90vh] bg-soc-card border border-soc-border rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-soc-border flex items-center justify-between bg-slate-900/95">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-sky-950/80 border border-sky-800 text-sky-400">
              <GraduationCap className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight font-mono">
                  SENTRIQ AI-SOC: FACULTY DEMO &amp; EVALUATION GUIDE
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-900/60 text-sky-300 border border-sky-700 font-semibold">
                  PRD Phase 8
                </span>
              </div>
              <p className="text-xs text-slate-400 font-sans mt-0.5">
                Comprehensive walkthrough of the 8 core architectural innovations for Major Project Review.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Demo Trigger Banner */}
        <div className="px-6 py-3 bg-slate-950/80 border-b border-soc-border flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 font-mono text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>Interactive Attack Simulation (PRD Section 12 Brute Force Scenario):</span>
          </div>
          <button
            disabled={injecting}
            onClick={handleLaunchAttack}
            className="px-4 py-1.5 bg-rose-600 hover:bg-rose-500 disabled:bg-slate-800 text-white rounded font-semibold flex items-center gap-1.5 transition-colors shadow-sm self-start sm:self-auto"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{injecting ? 'Injecting Attack...' : 'Launch Section 12 Attack'}</span>
          </button>
        </div>

        {injectionSuccess && (
          <div className="px-6 py-2 bg-emerald-950/40 border-b border-emerald-800/60 text-emerald-300 text-xs font-mono flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> {injectionSuccess}
            </span>
            <button
              onClick={() => {
                onClose();
                navigate('/incidents');
              }}
              className="underline hover:text-white"
            >
              View in Incidents →
            </button>
          </div>
        )}

        {/* Body Container */}
        <div className="flex-1 overflow-y-auto flex flex-col md:flex-row">
          {/* Tab Selector Column */}
          <div className="w-full md:w-64 border-b md:border-b-0 md:border-r border-soc-border p-3 space-y-1 bg-slate-900/40 flex-shrink-0">
            {tabs.map((tab, idx) => {
              const Icon = tab.icon;
              const isActive = activeTab === idx;
              return (
                <button
                  key={idx}
                  onClick={() => setActiveTab(idx)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-xs font-mono flex items-center justify-between transition-all ${
                    isActive
                      ? 'bg-sky-600/20 text-sky-300 border border-sky-500/40 font-bold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate">
                    <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-sky-400' : 'text-slate-500'}`} />
                    <span className="truncate">{tab.title}</span>
                  </div>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 ml-1">
                    {tab.badge}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Active Tab Content */}
          <div className="flex-1 p-6 space-y-5 bg-slate-950/40">
            {(() => {
              const current = tabs[activeTab];
              const Icon = current.icon;
              return (
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded bg-sky-950/80 border border-sky-800 text-sky-400">
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-white font-mono">{current.title}</h3>
                        <span className="text-[10px] font-mono text-sky-400 font-semibold">{current.badge}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        onClose();
                        navigate(current.path);
                      }}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-mono flex items-center gap-1.5 transition-colors"
                    >
                      <span>Jump to View</span>
                      <ExternalLink className="w-3.5 h-3.5 text-sky-400" />
                    </button>
                  </div>

                  <div className="space-y-3 font-sans text-xs text-slate-300">
                    <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3.5 space-y-1.5">
                      <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold">
                        Architectural Overview:
                      </span>
                      <p className="leading-relaxed">{current.description}</p>
                    </div>

                    <div className="bg-sky-950/20 border border-sky-900/40 rounded-lg p-3.5 space-y-1.5">
                      <span className="text-[10px] font-mono uppercase text-sky-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" /> Live Demo Showcase:
                      </span>
                      <p className="text-slate-300 leading-relaxed font-sans">{current.highlight}</p>
                    </div>
                  </div>

                  {/* Benchmark Snapshot */}
                  <div className="pt-2 border-t border-slate-800/80 font-mono text-[11px] text-slate-400 grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase block">Binary Accuracy</span>
                      <span className="font-bold text-emerald-400">96.67%</span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase block">Weighted F1</span>
                      <span className="font-bold text-emerald-400">0.9669</span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase block">Mean Latency</span>
                      <span className="font-bold text-amber-400">11.94 ms</span>
                    </div>
                    <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                      <span className="text-[9px] text-slate-500 uppercase block">Noise Reduction</span>
                      <span className="font-bold text-sky-400">93.3%</span>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-soc-border bg-slate-900/90 flex flex-wrap items-center justify-between gap-2 text-xs font-mono text-slate-400">
          <span>
            See <code className="text-sky-300">DEMO_GUIDE.md</code> &amp; <code className="text-sky-300">docs/EVALUATION_RESULTS.md</code> for full viva script.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs"
          >
            Close Guide
          </button>
        </div>
      </div>
    </div>
  );
};
