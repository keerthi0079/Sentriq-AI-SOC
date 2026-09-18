import React, { useState } from 'react';
import {
  Bot,
  ShieldAlert,
  GitCommit,
  Network,
  Copy,
  Check,
  FileText,
  Terminal,
  Target,
  Sparkles,
} from 'lucide-react';
import { InvestigationDossier, IOCDetail } from '../../types';

interface MultiAgentDossierCardProps {
  dossier: InvestigationDossier;
  onOpenReport: () => void;
  onOpenCopilot: () => void;
}

export const MultiAgentDossierCard: React.FC<MultiAgentDossierCardProps> = ({
  dossier,
  onOpenReport,
  onOpenCopilot,
}) => {
  const [copiedValue, setCopiedValue] = useState<string | null>(null);

  const copyToClipboard = (val: string) => {
    navigator.clipboard.writeText(val);
    setCopiedValue(val);
    setTimeout(() => setCopiedValue(null), 2000);
  };

  const triageAgent = dossier.agent_findings?.triage_agent;
  const correlationAgent = dossier.agent_findings?.correlation_agent;

  return (
    <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-soc-border pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-sky-950/80 border border-sky-800 text-sky-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white tracking-tight">
                Autonomous Multi-Agent Investigation Dossier
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-900/60 text-sky-300 border border-sky-700/50 flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-sky-400" /> 4 Agents Active
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Coordinated AI triage, kill-chain correlation, playbook formulation, and reporting (PRD Section 1.3 & FR-09)
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={onOpenCopilot}
            className="px-3 py-1.5 bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 border border-sky-500/40 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Consult Copilot</span>
          </button>
          <button
            onClick={onOpenReport}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-emerald-400" />
            <span>Executive Dossier</span>
          </button>
        </div>
      </div>

      {/* 4 Agent Contributions Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Agent 1: Triage */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-3 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold text-sky-400 flex items-center gap-1">
              <ShieldAlert className="w-3 h-3 text-sky-400" /> Triage Agent
            </span>
            <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/40">
              94% Conf
            </span>
          </div>
          <p className="text-[11px] text-slate-300 font-sans line-clamp-2">
            {triageAgent?.summary || 'Triaged incoming raw security telemetry and extracted forensic IOCs.'}
          </p>
        </div>

        {/* Agent 2: Correlation */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-3 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold text-amber-400 flex items-center gap-1">
              <GitCommit className="w-3 h-3 text-amber-400" /> Correlation Agent
            </span>
            <span className="text-[9px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/40">
              91% Conf
            </span>
          </div>
          <p className="text-[11px] text-slate-300 font-sans line-clamp-2">
            {correlationAgent?.summary || 'Mapped attack progression to MITRE ATT&CK stages and evaluated blast radius.'}
          </p>
        </div>

        {/* Agent 3: Response Playbook */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-3 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold text-rose-400 flex items-center gap-1">
              <Terminal className="w-3 h-3 text-rose-400" /> Response Agent
            </span>
            <span className="text-[9px] font-mono text-amber-400 bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-800/40">
              HITL Enforced
            </span>
          </div>
          <p className="text-[11px] text-slate-300 font-sans line-clamp-2">
            Synthesized {dossier.recommended_actions?.length || 0} containment action(s) awaiting explicit analyst sign-off.
          </p>
        </div>

        {/* Agent 4: Executive Reporting */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-lg p-3 space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold text-emerald-400 flex items-center gap-1">
              <FileText className="w-3 h-3 text-emerald-400" /> Reporting Agent
            </span>
            <span className="text-[9px] font-mono text-sky-400 bg-sky-950/60 px-1.5 py-0.5 rounded border border-sky-800/40">
              Markdown
            </span>
          </div>
          <p className="text-[11px] text-slate-300 font-sans line-clamp-2">
            Compiled complete executive briefing adhering to PRD FR-11 compliance standards.
          </p>
        </div>
      </div>

      {/* Attack Entry Vector & MITRE ATT&CK Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Entry Vector Card */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Target className="w-3.5 h-3.5 text-rose-400" /> Initial Attack Entry Vector
          </span>
          <p className="text-xs font-mono font-semibold text-white leading-relaxed">
            {dossier.attack_entry_vector}
          </p>
          <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-400 font-mono">
            <span>Kill-Chain Stage:</span>
            <span className="text-amber-400 font-bold bg-amber-950/50 px-2 py-0.5 rounded border border-amber-800/50">
              {dossier.kill_chain_stage}
            </span>
          </div>
        </div>

        {/* Blast Radius & MITRE Card */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-4 space-y-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Network className="w-3.5 h-3.5 text-sky-400" /> MITRE ATT&CK & Blast Radius
          </span>
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <span className="text-sky-300 bg-sky-950/80 px-2 py-0.5 rounded border border-sky-800">
              {correlationAgent?.mitre_technique_id || 'T1059'} - {correlationAgent?.mitre_technique_name || 'Execution'}
            </span>
            <span className="text-slate-400">
              ({correlationAgent?.mitre_tactic || 'Execution'})
            </span>
          </div>
          <p className="text-xs text-slate-300 font-sans leading-relaxed pt-1">
            {dossier.blast_radius_summary}
          </p>
        </div>
      </div>

      {/* Indicators of Compromise (IOC) Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-sky-400" />
            Extracted Indicators of Compromise ({dossier.indicators_of_compromise?.length || 0})
          </h3>
          <span className="text-[11px] font-mono text-slate-400">
            Grounded Forensic Evidence
          </span>
        </div>

        <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900/60">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900 text-[10px] uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Indicator Value</th>
                  <th className="py-2.5 px-3">Classification</th>
                  <th className="py-2.5 px-3">Contextual Significance</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {dossier.indicators_of_compromise?.map((ioc: IOCDetail, i: number) => {
                  const repBadge =
                    ioc.reputation === 'Malicious'
                      ? 'bg-rose-950 text-rose-400 border-rose-800'
                      : ioc.reputation === 'Suspicious'
                      ? 'bg-orange-950 text-orange-400 border-orange-800'
                      : ioc.reputation === 'Compromised Account'
                      ? 'bg-amber-950 text-amber-400 border-amber-800'
                      : 'bg-slate-800 text-slate-300 border-slate-700';

                  return (
                    <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-2.5 px-3 text-slate-400 font-semibold">{ioc.type}</td>
                      <td className="py-2.5 px-3 font-bold text-sky-300">{ioc.value}</td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded border ${repBadge}`}
                        >
                          {ioc.reputation}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-300 font-sans max-w-xs truncate">
                        {ioc.description}
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => copyToClipboard(ioc.value)}
                          className="p-1 rounded text-slate-400 hover:text-white transition-colors"
                          title="Copy indicator value"
                        >
                          {copiedValue === ioc.value ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
