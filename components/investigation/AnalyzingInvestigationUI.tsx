'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Sparkles, Cpu, CheckCircle2, Loader2, Database, ShieldCheck, FileText, Search, Activity, Terminal } from 'lucide-react';

interface AnalyzingInvestigationUIProps {
  incidentCode: string;
  projectName?: string;
  onCancel?: () => void;
}

const PIPELINE_STAGES = [
  { id: 1, name: 'Evidence & Document Ingestion', icon: FileText, desc: 'Processing raw logs, attachments, and diagnostic screenshots...' },
  { id: 2, name: 'Multi-Source Telemetry Tool Execution', icon: Activity, desc: 'Querying system metrics, error logs, and service traces...' },
  { id: 3, name: 'Self-RAG Vector Search', icon: Database, desc: 'Searching Qdrant knowledge base runbooks & historical incidents...' },
  { id: 4, name: 'Cross-Attention Reranking', icon: Search, desc: 'Reranking retrieved evidence for relevance to target incident...' },
  { id: 5, name: 'Anomaly & Evidence Analysis', icon: Cpu, desc: 'Extracting technical symptoms, errors, and failure mechanisms...' },
  { id: 6, name: 'Hypothesis Generation', icon: Sparkles, desc: 'Generating structured candidate root cause hypotheses...' },
  { id: 7, name: 'Hypothesis Evaluation & Scoring', icon: Activity, desc: 'Scoring supporting vs. contradicting evidence for each hypothesis...' },
  { id: 8, name: 'Adversarial Grounding Validation', icon: ShieldCheck, desc: 'Verifying claim-level grounding against raw evidence...' },
  { id: 9, name: 'Executive RCA Report Synthesis', icon: FileText, desc: 'Synthesizing canonical root cause, verification steps, and remediation...' },
  { id: 10, name: 'PostgreSQL Persistence & Qdrant Indexing', icon: Database, desc: 'Saving investigation run and indexing vector history...' },
];

export const AnalyzingInvestigationUI: React.FC<AnalyzingInvestigationUIProps> = ({
  incidentCode,
  projectName = 'Default Project',
}) => {
  const [currentStageIdx, setCurrentStageIdx] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    // Stage transition timer simulation while waiting for backend API response
    const interval = setInterval(() => {
      setCurrentStageIdx((prev) => {
        if (prev < PIPELINE_STAGES.length - 1) {
          const next = prev + 1;
          const stage = PIPELINE_STAGES[next];
          setLogs((l) => [
            `[${new Date().toLocaleTimeString()}] Node [${stage.name}]: ${stage.desc}`,
            ...l.slice(0, 15),
          ]);
          return next;
        }
        return prev;
      });
    }, 1800);

    setLogs([
      `[${new Date().toLocaleTimeString()}] Initializing Autonomous AI Agent for incident ${incidentCode}...`,
      `[${new Date().toLocaleTimeString()}] Target Project: ${projectName}`,
      `[${new Date().toLocaleTimeString()}] Node [${PIPELINE_STAGES[0].name}]: ${PIPELINE_STAGES[0].desc}`,
    ]);

    return () => clearInterval(interval);
  }, [incidentCode, projectName]);

  const progressPercent = Math.min(100, Math.round(((currentStageIdx + 1) / PIPELINE_STAGES.length) * 100));

  return (
    <div className="max-w-4xl mx-auto space-y-6 py-8 px-4 animate-in fade-in duration-300">
      {/* Top Banner */}
      <Card className="p-6 border-accentPrimary/40 bg-gradient-to-r from-bgSurface via-bgApp to-bgSurface relative overflow-hidden shadow-2xl">
        <div className="absolute -top-12 -right-12 w-48 h-48 bg-accentPrimary/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 relative z-10">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accentPrimary opacity-75" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-accentPrimary" />
              </span>
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-accentPrimary">
                Autonomous AI Investigation Running
              </span>
            </div>

            <h2 className="text-xl font-bold text-textPrimary font-sans">
              Investigating Incident <span className="font-mono text-accentPrimary">{incidentCode}</span>
            </h2>
            <p className="text-xs text-textMuted font-mono">
              Project: <span className="text-textSecondary font-semibold">{projectName}</span> — Analyzing logs, runbooks & telemetry evidence
            </p>
          </div>

          <div className="text-right shrink-0">
            <div className="text-2xl font-bold font-mono text-accentPrimary">{progressPercent}%</div>
            <p className="text-[10px] text-textMuted font-mono uppercase tracking-wider">Analysis Progress</p>
          </div>
        </div>

        {/* Dynamic Progress Bar */}
        <div className="mt-5 w-full bg-bgApp rounded-full h-2 overflow-hidden border border-borderColor">
          <div
            className="bg-gradient-to-r from-accentPrimary via-cyan-400 to-accentPrimary h-full transition-all duration-500 rounded-full"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </Card>

      {/* Grid: Active Stages & Terminal Activity Trace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Pipeline Stages (2 cols) */}
        <div className="lg:col-span-2 space-y-3">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-textMuted flex items-center gap-2">
            <Cpu className="w-4 h-4 text-accentPrimary" />
            <span>LangGraph Agent 10-Node Workflow</span>
          </h3>

          <div className="space-y-2">
            {PIPELINE_STAGES.map((stage, idx) => {
              const Icon = stage.icon;
              const isDone = idx < currentStageIdx;
              const isActive = idx === currentStageIdx;

              return (
                <div
                  key={stage.id}
                  className={`p-3 rounded-lg border transition-all flex items-center justify-between text-xs ${
                    isActive
                      ? 'bg-accentPrimary/10 border-accentPrimary text-textPrimary shadow-md scale-[1.01]'
                      : isDone
                      ? 'bg-bgSurface/60 border-borderColor/60 text-textSecondary opacity-80'
                      : 'bg-bgApp/40 border-borderColor/40 text-textMuted opacity-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-7 h-7 rounded-md flex items-center justify-center font-mono text-xs ${
                        isActive
                          ? 'bg-accentPrimary/20 text-accentPrimary border border-accentPrimary/50'
                          : isDone
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-bgApp text-textMuted border border-borderColor'
                      }`}
                    >
                      {isDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : isActive ? (
                        <Loader2 className="w-4 h-4 animate-spin text-accentPrimary" />
                      ) : (
                        <Icon className="w-3.5 h-3.5" />
                      )}
                    </div>

                    <div>
                      <p className={`font-semibold ${isActive ? 'text-accentPrimary' : isDone ? 'text-textPrimary' : 'text-textMuted'}`}>
                        {stage.id}. {stage.name}
                      </p>
                      <p className="text-[10px] text-textMuted font-mono truncate">{stage.desc}</p>
                    </div>
                  </div>

                  {isActive && (
                    <span className="text-[10px] font-mono font-bold uppercase text-accentPrimary px-2 py-0.5 rounded bg-accentPrimary/20 border border-accentPrimary/40 animate-pulse">
                      Active
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Terminal Activity Stream (1 col) */}
        <div className="space-y-3">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-textMuted flex items-center gap-2">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span>Agent Terminal Stream</span>
          </h3>

          <Card className="p-3 bg-black/90 border-borderColor font-mono text-[11px] leading-relaxed h-[420px] overflow-y-auto space-y-2 flex flex-col justify-start">
            <div className="text-emerald-400/80 text-[10px] border-b border-emerald-900/50 pb-1.5 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              <span>LIVE DIAGNOSTIC LOG STREAM</span>
            </div>

            <div className="space-y-1.5 flex-1 overflow-y-auto">
              {logs.map((log, i) => (
                <div key={i} className="text-emerald-300/90 break-words font-mono text-[10.5px]">
                  {log}
                </div>
              ))}
            </div>

            <div className="pt-2 border-t border-emerald-900/40 text-[10px] text-emerald-500/60 flex items-center gap-1">
              <Loader2 className="w-3 h-3 animate-spin text-emerald-400" />
              <span>Awaiting LangGraph node state updates...</span>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
