import React, { useEffect, useState } from 'react';
import { Database, Server } from 'lucide-react';
import { socApi } from '../services/api';
import { HealthResponse } from '../types';
import { formatDateTimeIST } from '../utils/date';

export const Settings: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await socApi.getHealth();
        setHealth(data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchHealth();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System & Database Infrastructure</h1>
        <p className="text-sm text-slate-400 mt-1">
          Infrastructure telemetry, Docker Desktop service topology, and database health.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Database Topology Card */}
        <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Relational Data Store</h3>
              <p className="text-xs text-slate-400">Docker Desktop Container</p>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">Container Image:</span>
              <span className="text-slate-200">postgres:16-alpine</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">Connection Status:</span>
              <span className={health?.database === 'connected' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'}>
                {health?.database || 'Checking...'}
              </span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">Host & Port:</span>
              <span className="text-slate-200">localhost:5432</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">Database Name:</span>
              <span className="text-slate-200">sentriq_soc</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">Driver:</span>
              <span className="text-slate-200">SQLAlchemy 2.0 (asyncpg / psycopg2)</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Storage Volume:</span>
              <span className="text-slate-200">sentriq_pgdata (persistent)</span>
            </div>
          </div>
        </div>

        {/* Backend Application Engine Card */}
        <div className="bg-soc-card border border-soc-border rounded-lg p-5 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-sky-500/10 border border-sky-500/30 text-sky-400">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Backend Application Engine</h3>
              <p className="text-xs text-slate-400">FastAPI Async Core</p>
            </div>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">Platform:</span>
              <span className="text-slate-200">{health?.project || 'Sentriq'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">API Version:</span>
              <span className="text-slate-200">{health?.version || '1.0.0'}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">API Base Prefix:</span>
              <span className="text-slate-200">/api/v1</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">FastAPI Interactive Docs:</span>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="text-sky-400 hover:underline"
              >
                /docs (Swagger UI)
              </a>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-800">
              <span className="text-slate-500">Environment:</span>
              <span className="text-slate-200">development</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Server Time (IST):</span>
              <span className="text-slate-300 text-[11px]">{health?.timestamp ? formatDateTimeIST(health.timestamp) : '—'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
