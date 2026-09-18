import React from 'react';
import { Severity } from '../../types';

interface SeverityBadgeProps {
  severity: Severity;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity, size = 'md' }) => {
  const styles: Record<Severity, { bg: string; text: string; dot: string; border: string }> = {
    Low: {
      bg: 'bg-emerald-950/40',
      text: 'text-emerald-400',
      dot: 'bg-emerald-400',
      border: 'border-emerald-800/50',
    },
    Medium: {
      bg: 'bg-amber-950/40',
      text: 'text-amber-400',
      dot: 'bg-amber-400',
      border: 'border-amber-800/50',
    },
    High: {
      bg: 'bg-orange-950/40',
      text: 'text-orange-400',
      dot: 'bg-orange-400',
      border: 'border-orange-800/50',
    },
    Critical: {
      bg: 'bg-rose-950/40',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
      border: 'border-rose-800/60',
    },
  };

  const current = styles[severity] || styles.Medium;
  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-md border ${current.bg} ${current.text} ${current.border} ${padding}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${current.dot}`} />
      {severity}
    </span>
  );
};

