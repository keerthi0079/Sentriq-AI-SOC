import React, { useEffect, useState } from 'react';
import {
  X,
  BrainCircuit,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  Sparkles,
} from 'lucide-react';
import { socApi } from '../../services/api';
import { XAIExplanationResponse } from '../../types';
import { FeatureAttributionChart } from './FeatureAttributionChart';

interface ExplainabilityDrawerProps {
  eventId?: string;
  features?: Record<string, any>;
  isOpen: boolean;
  onClose: () => void;
}

export const ExplainabilityDrawer: React.FC<ExplainabilityDrawerProps> = ({
  eventId,
  features,
  isOpen,
  onClose,
}) => {
  const [explanation, setExplanation] = useState<XAIExplanationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    const fetchExplanation = async () => {
      setLoading(true);
      setError(null);
      try {
        let data: XAIExplanationResponse;
        if (eventId) {
          data = await socApi.getEventExplanation(eventId);
        } else if (features) {
          data = await socApi.explainFeatures({ features });
        } else {
          return;
        }
        setExplanation(data);
      } catch (err: any) {
        console.error('Failed to load SHAP explanation:', err);
        setError(err.response?.data?.detail || 'Unable to compute SHAP feature attribution.');
      } finally {
        setLoading(false);
      }
    };

    fetchExplanation();
  }, [isOpen, eventId, features]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/70 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-2xl bg-soc-card border-l border-soc-border h-full flex flex-col shadow-2xl animate-fadeIn">
        {/* Drawer Header */}
        <div className="p-5 border-b border-soc-border flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold text-white tracking-tight">
                  Explainable AI (SHAP) Threat Attribution
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">
                  PRD FR-08
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Mathematical feature attribution using TreeExplainer on Random Forest model
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-24 text-center space-y-3">
              <Sparkles className="w-8 h-8 animate-spin text-sky-400 mx-auto" />
              <p className="text-xs text-slate-400 font-mono">
                Calculating Shapley feature attribution vectors...
              </p>
            </div>
          ) : error ? (
            <div className="bg-rose-950/40 border border-rose-800/80 rounded-lg p-5 text-center space-y-3">
              <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto" />
              <h3 className="text-sm font-bold text-white">Explanation Unavailable</h3>
              <p className="text-xs text-slate-300 font-sans">{error}</p>
            </div>
          ) : explanation ? (
            <div className="space-y-6">
              {/* Telemetry Metric Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                <div className="bg-slate-900/90 border border-slate-800 rounded p-3 space-y-0.5">
                  <span className="text-[10px] uppercase text-slate-500 font-sans">Predicted Class</span>
                  <p className="text-sm font-bold text-rose-400 truncate">
                    {explanation.predicted_category}
                  </p>
                </div>
                <div className="bg-slate-900/90 border border-slate-800 rounded p-3 space-y-0.5">
                  <span className="text-[10px] uppercase text-slate-500 font-sans">Attack Probability</span>
                  <p className="text-sm font-bold text-sky-400">
                    {(explanation.attack_probability * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-slate-900/90 border border-slate-800 rounded p-3 space-y-0.5">
                  <span className="text-[10px] uppercase text-slate-500 font-sans">SHAP Base Value</span>
                  <p className="text-sm font-bold text-slate-300">
                    {(explanation.base_value * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="bg-slate-900/90 border border-slate-800 rounded p-3 space-y-0.5">
                  <span className="text-[10px] uppercase text-slate-500 font-sans flex items-center gap-1">
                    <Clock className="w-3 h-3 text-emerald-400" /> Latency
                  </span>
                  <p className="text-sm font-bold text-emerald-400">
                    {explanation.inference_latency_ms} ms
                  </p>
                </div>
              </div>

              {/* Natural Language Synthesis Banner */}
              <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950/40 border border-sky-900/40 rounded-lg p-4 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-sky-300 uppercase tracking-wider font-mono">
                  <BrainCircuit className="w-4 h-4 text-sky-400" />
                  <span>Synthesized Detection Evidence</span>
                </div>
                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  {explanation.narrative}
                </p>
              </div>

              {/* Horizontal Diverging Bar Chart */}
              <div className="bg-soc-panel border border-soc-border rounded-lg p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-soc-border pb-3">
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                    <Layers className="w-3.5 h-3.5 text-sky-400" />
                    <span>Diverging Feature Attribution Waterfall</span>
                  </h3>
                  <span className="text-[11px] font-mono text-slate-500">
                    {explanation.all_features.length} Features Evaluated
                  </span>
                </div>

                <FeatureAttributionChart
                  features={explanation.all_features}
                  baseValue={explanation.base_value}
                  attackProbability={explanation.attack_probability}
                />
              </div>

              {/* Rule-to-XAI Bridge Consensus Card (PRD FR-08) */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                      Rule-to-XAI Bridge Consensus
                    </h3>
                  </div>
                  <span
                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                      explanation.rule_agreement
                        ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                        : 'bg-amber-950 text-amber-400 border-amber-800'
                    }`}
                  >
                    {explanation.rule_agreement ? 'Consensus Verified' : 'Divergent Signal'}
                  </span>
                </div>
                <p className="text-xs text-slate-400 font-sans leading-relaxed">
                  {explanation.rule_agreement
                    ? 'The mathematical SHAP feature attribution directly corroborates the rule-assisted heuristic detection evidence.'
                    : 'The ML model and heuristic rule engine evaluated different signal distributions.'}
                </p>

                {explanation.rule_reasons && explanation.rule_reasons.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/80 space-y-1">
                    <span className="text-[10px] font-mono text-slate-500 uppercase">
                      Heuristic Evidence Checked:
                    </span>
                    <ul className="text-xs text-slate-300 space-y-1 font-mono list-disc list-inside">
                      {explanation.rule_reasons.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
};
