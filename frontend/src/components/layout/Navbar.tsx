import React, { useEffect, useState } from 'react';
import { Shield, Database, Radio, CheckCircle2, AlertTriangle, GraduationCap } from 'lucide-react';
import { socApi } from '../../services/api';
import { HealthResponse } from '../../types';
import { FacultyDemoModal } from '../demo';
import { formatClockIST } from '../../utils/date';

export const Navbar: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [time, setTime] = useState<string>('');
  const [isDemoModalOpen, setIsDemoModalOpen] = useState<boolean>(false);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await socApi.getHealth();
        setHealth(data);
      } catch {
        setHealth(null);
      }
    };

    fetchHealth();
    const healthInterval = setInterval(fetchHealth, 15000);

    const updateClock = () => {
      setTime(formatClockIST());
    };
    updateClock();
    const clockInterval = setInterval(updateClock, 1000);

    return () => {
      clearInterval(healthInterval);
      clearInterval(clockInterval);
    };
  }, []);

  return (
    <header className="h-16 bg-soc-card border-b border-soc-border px-6 flex items-center justify-between sticky top-0 z-40">
      {/* Brand & Shield */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold tracking-wider text-white text-base font-mono">SENTRIQ</span>
            <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-slate-800 text-sky-400 border border-slate-700">
              AI-SOC
            </span>
          </div>
          <p className="text-[11px] text-slate-400 leading-tight">Autonomous Security Operations Center</p>
        </div>
      </div>

      {/* Center/Right Status Telemetry */}
      <div className="flex items-center gap-3 text-xs font-mono">
        {/* Faculty Demo Mode Trigger Button */}
        <button
          onClick={() => setIsDemoModalOpen(true)}
          className="px-3 py-1.5 bg-gradient-to-r from-sky-600/20 to-emerald-600/20 hover:from-sky-600/30 hover:to-emerald-600/30 text-sky-300 border border-sky-500/40 rounded-md font-semibold flex items-center gap-1.5 transition-all shadow-sm"
          title="Open Faculty Presentation & Architecture Walkthrough"
        >
          <GraduationCap className="w-4 h-4 text-emerald-400" />
          <span className="hidden sm:inline">Faculty Demo Mode</span>
        </button>

        {/* Live Clock */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900/60 border border-slate-800 text-slate-300">
          <Radio className="w-3.5 h-3.5 text-sky-400 animate-pulse" />
          <span>{time || 'Syncing...'}</span>
        </div>

        {/* Database Connection Pill (Docker Desktop PostgreSQL) */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900/80 border border-slate-800">
          <Database className="w-3.5 h-3.5 text-slate-400" />
          {health?.database === 'connected' ? (
            <div className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-medium">PostgreSQL 16 (Docker)</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Connecting to DB...</span>
            </div>
          )}
        </div>

        {/* System Health */}
        <div className="hidden sm:flex items-center gap-1.5 text-slate-400 px-2 py-1">
          <CheckCircle2 className="w-3.5 h-3.5 text-sky-400" />
          <span>v{health?.version || '1.0.0'}</span>
        </div>
      </div>

      {/* Interactive Faculty Demo Walkthrough Modal */}
      <FacultyDemoModal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
      />
    </header>
  );
};
