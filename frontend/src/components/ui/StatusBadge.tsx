import React from 'react';
import { IncidentStatus } from '../../types';

interface StatusBadgeProps {
  status: IncidentStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const styles: Record<IncidentStatus, { bg: string; text: string; border: string }> = {
    Open: {
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      border: 'border-rose-500/20',
    },
    Investigating: {
      bg: 'bg-sky-500/10',
      text: 'text-sky-400',
      border: 'border-sky-500/20',
    },
    Resolved: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/20',
    },
    Closed: {
      bg: 'bg-slate-500/10',
      text: 'text-slate-400',
      border: 'border-slate-500/20',
    },
  };

  const current = styles[status] || styles.Open;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${current.bg} ${current.text} ${current.border}`}
    >
      {status}
    </span>
  );
};

