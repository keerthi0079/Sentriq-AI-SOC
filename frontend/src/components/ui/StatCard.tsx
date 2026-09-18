import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'default' | 'danger' | 'warning' | 'accent';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'default',
}) => {
  const iconVariants = {
    default: 'text-slate-400 bg-slate-800/60 border-slate-700/50',
    danger: 'text-rose-400 bg-rose-950/30 border-rose-800/40',
    warning: 'text-amber-400 bg-amber-950/30 border-amber-800/40',
    accent: 'text-sky-400 bg-sky-950/30 border-sky-800/40',
  };

  return (
    <div className="bg-soc-card border border-soc-border rounded-lg p-5 shadow-sm hover:border-slate-600 transition-colors">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
          <h3 className="text-2xl font-bold text-white mt-1.5 font-mono">{value}</h3>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg border ${iconVariants[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
};

