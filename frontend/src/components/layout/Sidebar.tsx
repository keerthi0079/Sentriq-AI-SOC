import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  AlertOctagon,
  ScrollText,
  BrainCircuit,
  Settings,
  Server,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/', label: 'Overview Dashboard', icon: LayoutDashboard },
    { to: '/incidents', label: 'Incident Management', icon: AlertOctagon },
    { to: '/logs', label: 'Security Logs Explorer', icon: ScrollText },
    { to: '/analysis', label: 'ML Threat Analysis', icon: BrainCircuit },
    { to: '/settings', label: 'System & Database', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-soc-card border-r border-soc-border flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-1">
        <p className="px-3 py-2 text-[10px] uppercase font-semibold tracking-wider text-slate-500">
          SOC Operations
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-soc-border text-xs text-slate-500 space-y-1">
        <div className="flex items-center gap-1.5 text-slate-400 font-medium">
          <Server className="w-3.5 h-3.5 text-sky-400" />
          <span>Local Docker Pod</span>
        </div>
        <p className="text-[11px] text-slate-500">PostgreSQL 16 @ localhost:5432</p>
        <p className="text-[10px] text-slate-600 pt-2 border-t border-slate-800">
          Final Year Major Project
        </p>
      </div>
    </aside>
  );
};

