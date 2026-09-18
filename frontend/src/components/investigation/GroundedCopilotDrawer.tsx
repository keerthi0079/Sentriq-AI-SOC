import React, { useState, useRef, useEffect } from 'react';
import {
  X,
  Bot,
  Send,
  ShieldCheck,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Link as LinkIcon,
  HelpCircle,
  RefreshCw,
} from 'lucide-react';
import { socApi } from '../../services/api';
import { CopilotChatMessage, CopilotChatResponse } from '../../types';

interface GroundedCopilotDrawerProps {
  incidentId: string;
  incidentCode: string;
  isOpen: boolean;
  onClose: () => void;
}

export const GroundedCopilotDrawer: React.FC<GroundedCopilotDrawerProps> = ({
  incidentId,
  incidentCode,
  isOpen,
  onClose,
}) => {
  const [messages, setMessages] = useState<CopilotChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello Analyst. I am the **Sentriq AI-SOC Copilot**. My responses are strictly grounded in PostgreSQL event logs, correlation timelines, and MITRE kill-chain telemetry for **${incidentCode}** (Zero-Hallucination Guarantee). What would you like to investigate?`,
      timestamp: new Date().toISOString(),
      suggested_follow_ups: [
        'How did the attacker enter the system?',
        'What containment actions are recommended?',
        'What are the extracted IOCs?',
        'Why was this risk score assigned?',
      ],
    },
  ]);
  const [input, setInput] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [expandedFacts, setExpandedFacts] = useState<Record<string, boolean>>({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [isOpen, messages]);

  if (!isOpen) return null;

  const handleSend = async (queryText?: string) => {
    const text = queryText || input;
    if (!text.trim() || loading) return;

    const userMsg: CopilotChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInput('');
    setLoading(true);

    try {
      // Build brief history for context
      const historyPayload = messages.slice(-4).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res: CopilotChatResponse = await socApi.chatCopilot({
        incident_id: incidentId,
        question: text,
        history: historyPayload,
      });

      const assistantMsg: CopilotChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: res.answer,
        grounded_facts: res.grounded_facts,
        citations: res.citations,
        suggested_follow_ups: res.suggested_follow_ups,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Failed to query copilot:', err);
      const errorMsg: CopilotChatMessage = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: `Error querying SOC copilot: ${err.response?.data?.detail || 'Grounded telemetry query failed.'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleFacts = (id: string) => {
    setExpandedFacts((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm transition-opacity">
      <div className="w-full max-w-xl bg-soc-card border-l border-soc-border h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="px-5 py-4 border-b border-soc-border flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-950/80 border border-sky-800 text-sky-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold text-white tracking-tight">
                  Sentriq AI-SOC Copilot
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 flex items-center gap-1 font-semibold">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" /> Grounded Telemetry
                </span>
              </div>
              <p className="text-[11px] font-mono text-slate-400">
                Grounded context: <span className="text-sky-300 font-bold">{incidentCode}</span> (PRD FR-09)
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Transcript */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-xs">
          {messages.map((m) => {
            const isUser = m.role === 'user';
            const isExpanded = !!expandedFacts[m.id];

            return (
              <div
                key={m.id}
                className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                {!isUser && (
                  <div className="w-7 h-7 rounded-full bg-sky-950 border border-sky-800 flex items-center justify-center flex-shrink-0 text-sky-400 mt-1">
                    <Bot className="w-4 h-4" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-lg p-3.5 space-y-2.5 ${
                    isUser
                      ? 'bg-sky-600 text-white rounded-br-none'
                      : 'bg-slate-900/95 border border-slate-800 text-slate-200 rounded-bl-none shadow-sm'
                  }`}
                >
                  {/* Message Content */}
                  <div className="prose prose-invert prose-xs leading-relaxed space-y-2">
                    {m.content.split('\n\n').map((para, idx) => (
                      <p key={idx} className="whitespace-pre-wrap">
                        {para}
                      </p>
                    ))}
                  </div>

                  {/* Grounded Facts Accordion (Assistant Only) */}
                  {!isUser && m.grounded_facts && m.grounded_facts.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/80">
                      <button
                        onClick={() => toggleFacts(m.id)}
                        className="flex items-center justify-between w-full text-[11px] font-mono text-sky-400 hover:text-sky-300 transition-colors"
                      >
                        <span className="flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          Grounded Database Facts ({m.grounded_facts.length})
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="w-3.5 h-3.5" />
                        ) : (
                          <ChevronDown className="w-3.5 h-3.5" />
                        )}
                      </button>

                      {isExpanded && (
                        <ul className="mt-2 space-y-1 text-[10px] font-mono text-slate-300 bg-slate-950/80 p-2.5 rounded border border-slate-800">
                          {m.grounded_facts.map((fact, idx) => (
                            <li key={idx} className="flex items-start gap-1.5">
                              <span className="text-emerald-400 select-none">•</span>
                              <span>{fact}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}

                  {/* Telemetry Citations (Assistant Only) */}
                  {!isUser && m.citations && m.citations.length > 0 && (
                    <div className="pt-1 flex flex-wrap items-center gap-1.5 text-[10px] font-mono text-slate-400">
                      <span className="flex items-center gap-1 text-slate-500">
                        <LinkIcon className="w-3 h-3" /> Evidence:
                      </span>
                      {m.citations.slice(0, 3).map((cit, idx) => (
                        <span
                          key={idx}
                          className="bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-slate-300"
                        >
                          {cit}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Clickable Suggested Follow-up Prompts */}
                  {!isUser && m.suggested_follow_ups && m.suggested_follow_ups.length > 0 && (
                    <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                      <span className="text-[10px] font-mono text-slate-400 flex items-center gap-1">
                        <HelpCircle className="w-3 h-3 text-sky-400" /> Suggested Inquiries:
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {m.suggested_follow_ups.map((q, idx) => (
                          <button
                            key={idx}
                            disabled={loading}
                            onClick={() => handleSend(q)}
                            className="text-[11px] font-mono bg-slate-950 hover:bg-slate-800 text-sky-300 hover:text-white border border-slate-800 px-2 py-1 rounded text-left transition-colors"
                          >
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-7 h-7 rounded-full bg-sky-950 border border-sky-800 flex items-center justify-center flex-shrink-0 text-sky-400 mt-1">
                <Bot className="w-4 h-4 animate-spin" />
              </div>
              <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-3 text-xs text-slate-400 font-mono flex items-center gap-2">
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-sky-400" />
                <span>Grounding query against PostgreSQL incident events...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-soc-border bg-slate-900/90 space-y-2">
          {/* Quick Query Shortcuts */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] font-mono text-slate-400">
            <span className="text-slate-500 flex-shrink-0">Quick:</span>
            <button
              onClick={() => handleSend('How did the attacker enter the system?')}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded border border-slate-700 whitespace-nowrap"
            >
              Entry Vector
            </button>
            <button
              onClick={() => handleSend('What containment actions are recommended?')}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded border border-slate-700 whitespace-nowrap"
            >
              Containment Playbook
            </button>
            <button
              onClick={() => handleSend('What are the extracted IOCs?')}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded border border-slate-700 whitespace-nowrap"
            >
              Extracted IOCs
            </button>
            <button
              onClick={() => handleSend('Why was this risk score assigned?')}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-0.5 rounded border border-slate-700 whitespace-nowrap"
            >
              Risk Formula
            </button>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ask copilot about attacker IP, kill-chain, or containment..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSend();
              }}
              disabled={loading}
              className="flex-1 bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
            <button
              disabled={loading || !input.trim()}
              onClick={() => handleSend()}
              className="px-3.5 py-2 bg-sky-600 hover:bg-sky-500 disabled:bg-slate-800 text-white rounded text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
