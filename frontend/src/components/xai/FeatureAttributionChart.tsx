import React, { useState } from 'react';
import { FeatureAttribution } from '../../types';
import { ArrowRight, ArrowLeft } from 'lucide-react';

interface FeatureAttributionChartProps {
  features: FeatureAttribution[];
  baseValue?: number;
  attackProbability?: number;
  compact?: boolean;
}

export const FeatureAttributionChart: React.FC<FeatureAttributionChartProps> = ({
  features,
  baseValue,
  attackProbability,
  compact = false,
}) => {
  const [showAll, setShowAll] = useState<boolean>(false);

  // Filter top features if not showing all
  const displayFeatures = showAll ? features : features.slice(0, 8);

  // Determine max absolute SHAP value for scaling
  const maxAbsShap = Math.max(
    ...features.map((f) => Math.abs(f.shap_value)),
    0.001
  );

  return (
    <div className="space-y-4 font-sans">
      {/* Probability Gauge & Baseline Info */}
      {baseValue !== undefined && attackProbability !== undefined && !compact && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-xs flex flex-wrap items-center justify-between gap-3 font-mono">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Baseline Prior (E[f(x)]):</span>
            <span className="text-slate-200 font-bold">{(baseValue * 100).toFixed(1)}%</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-500">
            <ArrowRight className="w-3.5 h-3.5" />
            <span className="text-slate-400">SHAP Sum Shift:</span>
            <span
              className={`font-bold ${
                attackProbability >= baseValue ? 'text-rose-400' : 'text-emerald-400'
              }`}
            >
              {attackProbability >= baseValue ? '+' : ''}
              {((attackProbability - baseValue) * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Predicted Threat Likelihood:</span>
            <span
              className={`font-bold px-2 py-0.5 rounded text-xs ${
                attackProbability >= 0.5
                  ? 'bg-rose-950 text-rose-300 border border-rose-800'
                  : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
              }`}
            >
              {(attackProbability * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      )}

      {/* Diverging Legend */}
      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 border-b border-slate-800 pb-2">
        <span className="flex items-center gap-1 text-emerald-400">
          <ArrowLeft className="w-3 h-3" />
          <span>Mitigating / Normal Baseline Traffic</span>
        </span>
        <span className="text-slate-500 text-[10px] uppercase tracking-wider">
          SHAP Feature Impact (φ)
        </span>
        <span className="flex items-center gap-1 text-rose-400">
          <span>Malicious Threat Driver</span>
          <ArrowRight className="w-3 h-3" />
        </span>
      </div>

      {/* Diverging Bars Container */}
      <div className="space-y-2 font-mono text-xs">
        {displayFeatures.map((feat) => {
          const isPositive = feat.direction === 'positive';
          const normalizedWidth = Math.min(
            100,
            Math.max(4, (Math.abs(feat.shap_value) / maxAbsShap) * 100)
          );

          return (
            <div
              key={feat.feature_name}
              className="grid grid-cols-12 items-center gap-2 py-1 px-2 rounded hover:bg-slate-800/40 transition-colors"
            >
              {/* Feature Name & Value */}
              <div className="col-span-5 truncate text-[11px]">
                <span className="text-slate-300 font-medium">{feat.display_name}</span>
                <span className="text-[10px] text-slate-500 ml-1.5">
                  ({String(feat.feature_value)})
                </span>
              </div>

              {/* Diverging Center-Aligned Bar (col-span-5) */}
              <div className="col-span-5 flex items-center h-4 relative">
                {/* Center Divider Line */}
                <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-slate-700 z-10" />

                {/* Left side (Negative / Benign) */}
                <div className="w-1/2 flex justify-end pr-0.5">
                  {!isPositive && (
                    <div
                      className="h-2.5 rounded-l bg-emerald-500 transition-all duration-300 hover:brightness-125"
                      style={{ width: `${normalizedWidth}%` }}
                      title={`SHAP φ: ${feat.shap_value} (-${feat.contribution_percent}%)`}
                    />
                  )}
                </div>

                {/* Right side (Positive / Threat) */}
                <div className="w-1/2 flex justify-start pl-0.5">
                  {isPositive && (
                    <div
                      className="h-2.5 rounded-r bg-rose-500 transition-all duration-300 hover:brightness-125"
                      style={{ width: `${normalizedWidth}%` }}
                      title={`SHAP φ: +${feat.shap_value} (+${feat.contribution_percent}%)`}
                    />
                  )}
                </div>
              </div>

              {/* Attribution Impact Label */}
              <div className="col-span-2 text-right font-bold text-[11px]">
                <span
                  className={
                    isPositive ? 'text-rose-400' : 'text-emerald-400'
                  }
                >
                  {isPositive ? '+' : '-'}
                  {feat.contribution_percent.toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Show All / Show Less Toggle */}
      {features.length > 8 && (
        <div className="pt-2 text-center border-t border-slate-800/60">
          <button
            onClick={() => setShowAll(!showAll)}
            className="text-xs text-sky-400 hover:text-sky-300 font-mono font-semibold transition-colors"
          >
            {showAll ? 'Show Top 8 Contributors' : `View All ${features.length} Features`}
          </button>
        </div>
      )}
    </div>
  );
};
