'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Project, Incident, Investigation } from '@/types';
import { ExecutiveSummary } from '@/components/investigation/ExecutiveSummary';
import { ImpactPanel } from '@/components/investigation/ImpactPanel';
import { DetectedChangesPanel } from '@/components/investigation/DetectedChangesPanel';
import { HypothesisCard } from '@/components/investigation/HypothesisCard';
import { EvidenceGroupedList } from '@/components/investigation/EvidenceGroupedList';
import { RecommendationList } from '@/components/investigation/RecommendationList';
import { EvidenceGapPanel } from '@/components/investigation/EvidenceGapPanel';
import { InvestigationActivityTrace } from '@/components/investigation/InvestigationActivityTrace';
import { AskInvestigationPanel } from '@/components/investigation/AskInvestigationPanel';
import { AnalyzingInvestigationUI } from '@/components/investigation/AnalyzingInvestigationUI';
import { SeverityBadge } from '@/components/incidents/SeverityBadge';
import { StatusBadge } from '@/components/incidents/StatusBadge';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ArrowLeft, RefreshCw, HelpCircle, Clock, Sparkles, CheckCircle2 } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectInvestigationReportPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.projectId as string) || 'shopflow';
  const incidentId = (params?.incidentId as string) || 'inc-1001';

  const [project, setProject] = useState<Project | null>(null);
  const [incident, setIncident] = useState<Incident | null>(null);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [investigationRuns, setInvestigationRuns] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isTriggering, setIsTriggering] = useState(false);
  const [isResolving, setIsResolving] = useState(false);
  const [isResolvedSuccess, setIsResolvedSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const startFreshInvestigation = async () => {
    setIsAnalyzing(true);
    setErrorMessage(null);
    try {
      const updated = await api.startInvestigation(incidentId, { forceRestart: true, projectId });
      setInvestigation(updated);
      const runs = await (api as any).getInvestigationRuns?.(incidentId).catch(() => []) || [];
      setInvestigationRuns(runs || []);
    } catch (err: any) {
      console.error('Failed to run AI investigation:', err);
      setErrorMessage(err?.message || 'AI investigation workflow failed. Please check log references.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const fetchInvestigation = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [proj, inc, data, runs] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        api.getIncident(incidentId, projectId).catch(() => null),
        api.getInvestigation(incidentId, projectId).catch(() => null),
        (api as any).getInvestigationRuns?.(incidentId).catch(() => []) || [],
      ]);
      setProject(proj);
      setIncident(inc);
      setInvestigationRuns(runs || []);

      if (data) {
        setInvestigation(data);
      } else {
        // Auto-start AI investigation workflow if no report exists yet
        await startFreshInvestigation();
      }
    } catch (err: any) {
      console.error('Failed to load AI investigation report:', err);
      setErrorMessage(err?.message || 'Failed to load investigation report from backend API.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInvestigation();
  }, [incidentId, projectId]);

  const handleReanalyze = async () => {
    if (isTriggering || isAnalyzing) return;
    setIsTriggering(true);
    try {
      await startFreshInvestigation();
      const updatedInc = await api.getIncident(incidentId, projectId).catch(() => null);
      if (updatedInc) setIncident(updatedInc);
    } finally {
      setIsTriggering(false);
    }
  };

  const handleResolveIncident = async () => {
    if (isResolving) return;
    setIsResolving(true);
    try {
      await api.resolveIncident(incidentId, projectId);
      const updatedInc = await api.getIncident(incidentId, projectId).catch(() => null);
      if (updatedInc) setIncident(updatedInc);
      setIsResolvedSuccess(true);
    } catch (err: any) {
      console.error('Failed to resolve incident:', err);
      setErrorMessage(err?.message || 'Failed to mark incident as resolved.');
    } finally {
      setIsResolving(false);
    }
  };

  const projectName = project ? project.name : projectId;
  const displayIncidentCode = incident?.code || (investigation as any)?.incidentCode || 'INC-1001';

  if (isLoading || isAnalyzing) {
    return <AnalyzingInvestigationUI incidentCode={displayIncidentCode} projectName={projectName} />;
  }

  if (!investigation) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center space-y-4">
        <Card className="p-8 border-borderColor bg-bgSurface space-y-4">
          <div className="w-12 h-12 rounded-full bg-accentPrimary/20 text-accentPrimary flex items-center justify-center mx-auto">
            <Sparkles className="w-6 h-6" />
          </div>
          <h2 className="text-base font-bold text-textPrimary font-sans">
            Ready to Analyze Incident <span className="font-mono text-accentPrimary">{displayIncidentCode}</span>
          </h2>
          <p className="text-xs text-textMuted font-mono leading-relaxed">
            No report available yet for project <span className="text-textSecondary">{projectName}</span>. Click below to launch the 10-node autonomous LangGraph AI investigation workflow.
          </p>
          {errorMessage && <p className="text-statusDanger text-xs font-mono">{errorMessage}</p>}
          <Button variant="primary" onClick={startFreshInvestigation} isLoading={isAnalyzing} className="gap-2 font-mono text-xs">
            <Sparkles className="w-4 h-4" />
            <span>Launch AI Investigation Workflow</span>
          </Button>
        </Card>
      </div>
    );
  }

  const inv = investigation;
  const rootCauseTitle = inv.primaryHypothesis?.title;

  const isIncidentResolved = incident?.status === 'Resolved' || isResolvedSuccess;

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-xs pb-12">
      {/* Navigation Header */}
      <div className="flex items-center justify-between border-b border-borderColor pb-3">
        <Link
          href={`/projects/${projectId}/incidents/${incidentId}`}
          className="inline-flex items-center gap-1.5 text-textSecondary hover:text-textPrimary transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Evidence Hub ({projectName})</span>
        </Link>
        <span className="font-mono text-[10px] text-textMuted uppercase tracking-wider">
          TRACEBACK AI Engine • Project: {projectName}
        </span>
      </div>

      {isResolvedSuccess && (
        <div className="bg-statusSuccess/15 border border-statusSuccess/40 p-4 rounded-lg text-xs text-statusSuccess flex items-center justify-between font-mono">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5" />
            <span>INCIDENT RESOLVED • Monitored services restored to Healthy state and archived to Qdrant vector memory.</span>
          </div>
          <button onClick={() => setIsResolvedSuccess(false)} className="underline hover:no-underline text-[11px]">Dismiss</button>
        </div>
      )}

      {errorMessage && (
        <div className="bg-statusError/10 border border-statusError/30 p-4 rounded-lg text-xs text-statusError flex items-center justify-between">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="underline hover:no-underline font-mono">Dismiss</button>
        </div>
      )}

      {/* Main Report Title Banner */}
      <div className="bg-bgSurface border border-borderColor p-5 rounded-lg space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-accentPrimary text-xs">{displayIncidentCode}:</span>
              {(inv as any).investigationNumber && (
                <span className="px-2 py-0.5 rounded bg-accentPrimary/20 text-accentPrimary font-mono text-[10px]">
                  Run #{(inv as any).investigationNumber}
                </span>
              )}
              <SeverityBadge severity={inv.severity} />
              <StatusBadge status={isIncidentResolved ? 'Resolved' : inv.status === 'analyzing' ? 'Investigating' : 'Identified'} />
            </div>
            <h1 className="text-lg font-bold text-textPrimary">{inv.title}</h1>
          </div>

          <div className="flex items-center gap-3 border-l border-borderColor pl-4">
            <div className="text-right">
              <p className="text-[10px] text-textMuted uppercase font-mono tracking-wider mb-1">Investigation Confidence</p>
              <Badge variant="confidence" className="font-mono text-xs px-2.5 py-1">
                {inv.confidence}% CONFIDENCE
              </Badge>
            </div>

            <Button size="sm" variant="outline" onClick={handleReanalyze} isLoading={isTriggering} className="gap-1.5 text-xs font-mono">
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Re-analyze</span>
            </Button>

            {isIncidentResolved ? (
              <Badge variant="success" className="font-mono text-xs px-3 py-1.5 gap-1.5 bg-statusSuccess/20 text-statusSuccess border-statusSuccess/40">
                <CheckCircle2 className="w-4 h-4" />
                <span>RESOLVED & HEALTHY</span>
              </Badge>
            ) : (
              <Button
                size="sm"
                variant="primary"
                onClick={handleResolveIncident}
                isLoading={isResolving}
                className="gap-1.5 text-xs bg-statusSuccess hover:bg-statusSuccess/90 text-white font-mono"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Mark as Resolved</span>
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* 1. EXECUTIVE SUMMARY & DIAGNOSIS */}
      <ExecutiveSummary summary={inv.summary} rootCause={rootCauseTitle} />

      {/* 2. SYSTEM & CUSTOMER IMPACT */}
      <ImpactPanel impact={inv.impact} />

      {/* 3. ACTIONABLE REMEDIATION RECOMMENDATIONS */}
      <RecommendationList recommendations={inv.recommendations} />

      {/* 4. DETECTED CHANGES */}
      <DetectedChangesPanel metrics={inv.detectedChanges} />

      {/* 5. ROOT CAUSE HYPOTHESES */}
      <Card className="p-4 space-y-3">
        <CardHeader className="p-0 pb-2">
          <CardTitle className="text-xs uppercase font-mono tracking-wider text-textMuted flex items-center gap-2 font-bold">
            <HelpCircle className="w-4 h-4 text-accentPrimary" />
            <span>Root Cause Hypotheses & Confidence Scoring ({projectName})</span>
          </CardTitle>
        </CardHeader>

        <div className="space-y-3">
          <div>
            <span className="text-[10px] uppercase font-mono font-semibold text-statusSuccess tracking-wider block mb-1.5">
              Primary Hypothesis
            </span>
            <HypothesisCard hypothesis={inv.primaryHypothesis} />
          </div>

          {inv.alternativeHypotheses && inv.alternativeHypotheses.length > 0 && (
            <div>
              <span className="text-[10px] uppercase font-mono font-semibold text-textMuted tracking-wider block mb-1.5">
                Alternative Hypotheses Evaluated
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {inv.alternativeHypotheses.map((alt) => (
                  <HypothesisCard key={alt.id} hypothesis={alt} />
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* 8. EVIDENCE GROUPED LIST */}
      <EvidenceGroupedList />

      {/* 9. MISSING EVIDENCE GAPS */}
      <EvidenceGapPanel
        gaps={inv.evidenceGaps}
        onUploadClick={() => router.push(`/projects/${projectId}/incidents/new`)}
      />

      {/* 10. ACTIVITY TRACE */}
      <InvestigationActivityTrace trace={inv.activityTrace} />

      {/* HISTORICAL INVESTIGATION RUNS */}
      {investigationRuns && investigationRuns.length > 0 && (
        <Card className="p-4 space-y-3">
          <CardHeader className="p-0 pb-2">
            <CardTitle className="text-xs uppercase font-mono tracking-wider text-textMuted flex items-center gap-2">
              <Clock className="w-4 h-4 text-accentPrimary" />
              <span>Historical Investigation Runs ({investigationRuns.length})</span>
            </CardTitle>
          </CardHeader>
          <div className="space-y-2 font-mono text-xs">
            {investigationRuns.map((run: any) => (
              <div
                key={run.id}
                className="bg-bgSurface border border-borderColor p-3 rounded-md flex items-center justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-accentPrimary">Run #{run.investigation_number}</span>
                    <Badge variant={run.status === 'COMPLETED' ? 'success' : run.status === 'FAILED' ? 'danger' : 'outline'} className="text-[10px] px-2 py-0.5">
                      {run.status}
                    </Badge>
                    {run.confidence && (
                      <span className="text-textSecondary text-[10px]">{run.confidence}% Confidence</span>
                    )}
                  </div>
                  <p className="text-[11px] text-textMuted font-sans">{run.final_summary || run.error_message || 'Execution completed.'}</p>
                </div>
                <div className="text-right text-[10px] text-textMuted">
                  <div>{run.completed_at ? new Date(run.completed_at).toLocaleTimeString() : 'Running...'}</div>
                  {run.duration_ms && <div>{(run.duration_ms / 1000).toFixed(2)}s duration</div>}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* 12. CHAT / FOLLOW-UP */}
      <AskInvestigationPanel />
    </div>
  );
}
