import React, { useState } from 'react';
import {
  X,
  FileText,
  Download,
  Copy,
  Check,
  CheckCircle2,
} from 'lucide-react';

interface ExecutiveReportModalProps {
  incidentCode: string;
  markdownContent: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ExecutiveReportModal: React.FC<ExecutiveReportModalProps> = ({
  incidentCode,
  markdownContent,
  isOpen,
  onClose,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(markdownContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Sentriq-Dossier-${incidentCode}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="w-full max-w-4xl max-h-[90vh] bg-soc-card border border-soc-border rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="px-6 py-4 border-b border-soc-border flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-950/80 border border-emerald-800 text-emerald-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                Executive Incident Dossier (PRD FR-11)
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                Autonomously compiled by Sentriq AI Reporting Agent for <span className="text-sky-400 font-bold">{incidentCode}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Markdown'}</span>
            </button>
            <button
              onClick={handleDownload}
              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .md</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition-colors ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Markdown Content Viewer */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-950 font-mono text-xs text-slate-300 leading-relaxed space-y-4">
          <pre className="whitespace-pre-wrap select-text font-mono text-xs bg-slate-900/60 p-4 rounded-lg border border-slate-800/80">
            {markdownContent}
          </pre>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-soc-border bg-slate-900/90 flex items-center justify-between text-xs font-mono text-slate-400">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <CheckCircle2 className="w-4 h-4" /> Ready for SOC Executive Briefing & Audits
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

