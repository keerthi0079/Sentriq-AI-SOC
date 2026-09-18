import React, { useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  Clock,
  Terminal,
  Copy,
  Check,
} from 'lucide-react';
import { ResponseAction } from '../../types';
import { socApi } from '../../services/api';
import { formatDateTimeIST } from '../../utils/date';

interface ContainmentActionsCardProps {
  actions: ResponseAction[];
  onActionUpdated: (updatedAction: ResponseAction) => void;
}

export const ContainmentActionsCard: React.FC<ContainmentActionsCardProps> = ({
  actions,
  onActionUpdated,
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [submittingId, setSubmittingId] = useState<string | null>(null);
  const [comments, setComments] = useState<Record<string, string>>({});
  const analystName = 'Tier-2 Senior SOC Analyst';

  const copyCommand = (id: string, cmd: string) => {
    navigator.clipboard.writeText(cmd);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleReview = async (actionId: string, decision: 'Approved' | 'Rejected') => {
    setSubmittingId(actionId);
    try {
      const res = await socApi.reviewAction({
        action_id: actionId,
        decision,
        analyst_name: analystName,
        comment: comments[actionId] || undefined,
      });
      if (res.success) {
        onActionUpdated(res.action);
      }
    } catch (err) {
      console.error('Failed to submit containment action review:', err);
    } finally {
      setSubmittingId(null);
    }
  };

  const pendingCount = actions.filter((a) => a.status === 'Pending').length;
  const approvedCount = actions.filter((a) => a.status === 'Approved').length;

  return (
    <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-soc-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <Terminal className="w-4 h-4 text-rose-400" />
              Containment & Remediation Playbooks (PRD FR-10)
            </h2>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950/80 text-amber-400 border border-amber-800/60 font-semibold">
              Human-in-the-Loop Required
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated defensive proposals strictly held in Pending state until validated and authorized by an analyst.
          </p>
        </div>

        {/* Counter Badges */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="px-2.5 py-1 rounded bg-amber-950/70 border border-amber-800 text-amber-300">
            {pendingCount} Pending
          </span>
          <span className="px-2.5 py-1 rounded bg-emerald-950/70 border border-emerald-800 text-emerald-300">
            {approvedCount} Approved
          </span>
        </div>
      </div>

      {/* Action Cards List */}
      {actions.length === 0 ? (
        <div className="py-8 text-center text-slate-500 text-xs font-mono">
          No containment actions formulated for this incident yet.
        </div>
      ) : (
        <div className="space-y-4">
          {actions.map((act) => {
            const isPending = act.status === 'Pending';
            const isApproved = act.status === 'Approved';
            const isRejected = act.status === 'Rejected';
            const isSubmitting = submittingId === act.id;

            const riskColor =
              act.risk_level === 'High'
                ? 'text-rose-400 bg-rose-950/60 border-rose-800'
                : act.risk_level === 'Medium'
                ? 'text-amber-400 bg-amber-950/60 border-amber-800'
                : 'text-sky-400 bg-sky-950/60 border-sky-800';

            return (
              <div
                key={act.id}
                className={`border rounded-lg p-4 space-y-3 transition-all ${
                  isPending
                    ? 'bg-slate-900/90 border-slate-700/80 shadow-md'
                    : isApproved
                    ? 'bg-emerald-950/20 border-emerald-800/60'
                    : 'bg-rose-950/10 border-rose-900/40 opacity-70'
                }`}
              >
                {/* Top Row: Title, Action Type, Risk Level, Status */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold text-white font-sans">{act.title}</span>
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${riskColor}`}>
                      Risk: {act.risk_level}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                      Target: {act.target_entity}
                    </span>
                  </div>

                  {/* Status Badge */}
                  <div>
                    {isPending && (
                      <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700 flex items-center gap-1.5 animate-pulse">
                        <Clock className="w-3 h-3" /> PENDING ANALYST REVIEW
                      </span>
                    )}
                    {isApproved && (
                      <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" /> APPROVED & ENFORCED
                      </span>
                    )}
                    {isRejected && (
                      <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-700 flex items-center gap-1.5">
                        <XCircle className="w-3 h-3 text-rose-400" /> REJECTED
                      </span>
                    )}
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs text-slate-300 font-sans leading-relaxed">
                  {act.description}
                </p>

                {/* Command Snippet */}
                {act.command && (
                  <div className="bg-slate-950 border border-slate-800 rounded p-2.5 flex items-center justify-between gap-2 font-mono text-xs">
                    <div className="flex items-center gap-2 overflow-x-auto text-sky-300">
                      <span className="text-slate-600 select-none">$</span>
                      <code>{act.command}</code>
                    </div>
                    <button
                      onClick={() => copyCommand(act.id, act.command!)}
                      className="text-slate-400 hover:text-white p-1 rounded transition-colors flex-shrink-0"
                      title="Copy containment command"
                    >
                      {copiedId === act.id ? (
                        <Check className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                )}

                {/* Approval Metadata (If approved or rejected) */}
                {!isPending && (
                  <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>
                      Reviewed by: <strong className="text-slate-300">{act.approved_by || 'SOC Analyst'}</strong>
                      {act.approved_at && (
                        <> at {formatDateTimeIST(act.approved_at)}</>
                      )}
                    </span>
                    {act.analyst_comment && (
                      <span className="italic text-slate-300">Note: "{act.analyst_comment}"</span>
                    )}
                  </div>
                )}

                {/* Human-in-the-Loop Review Buttons (Only for Pending) */}
                {isPending && (
                  <div className="pt-2 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex-1">
                      <input
                        type="text"
                        placeholder="Optional justification note for SOC audit log..."
                        value={comments[act.id] || ''}
                        onChange={(e) =>
                          setComments({ ...comments, [act.id]: e.target.value })
                        }
                        className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
                      />
                    </div>
                    <div className="flex items-center gap-2 self-end sm:self-auto">
                      <button
                        disabled={isSubmitting}
                        onClick={() => handleReview(act.id, 'Approved')}
                        className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>Approve & Apply</span>
                      </button>
                      <button
                        disabled={isSubmitting}
                        onClick={() => handleReview(act.id, 'Rejected')}
                        className="px-3 py-1.5 bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>Reject</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
