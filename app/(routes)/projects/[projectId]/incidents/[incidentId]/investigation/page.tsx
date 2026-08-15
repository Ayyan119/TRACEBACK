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
import { Timeline } from '@/components/investigation/Timeline';
import { EvidenceChain } from '@/components/investigation/EvidenceChain';
import { EvidenceGroupedList } from '@/components/investigation/EvidenceGroupedList';
import { RecommendationList } from '@/components/investigation/RecommendationList';
import { EvidenceGapPanel } from '@/components/investigation/EvidenceGapPanel';
import { InvestigationActivityTrace } from '@/components/investigation/InvestigationActivityTrace';
import { AskInvestigationPanel } from '@/components/investigation/AskInvestigationPanel';
import { SeverityBadge } from '@/components/incidents/SeverityBadge';
import { StatusBadge } from '@/components/incidents/StatusBadge';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ArrowLeft, RefreshCw, HelpCircle, Clock } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectInvestigationReportPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.projectId as string) || 'shopflow';
  const incidentId = (params?.incidentId as string) || 'inc-1042';

  const [project, setProject] = useState<Project | null>(null);
  const [incident, setIncident] = useState<Incident | null>(null);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [investigationRuns, setInvestigationRuns] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isTriggering, setIsTriggering] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

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
      setInvestigation(data);
      setInvestigationRuns(runs || []);
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
    if (isTriggering) return;
    setIsTriggering(true);
    setErrorMessage(null);
    try {
      const updated = await api.startInvestigation(incidentId, { forceRestart: true, projectId });
      setInvestigation(updated);
    } catch (err: any) {
      console.error('Failed to trigger AI investigation:', err);
      setErrorMessage(err?.message || 'Investigation execution failed. Please check backend log references.');
    } finally {
      setIsTriggering(false);
    }
  };

  if (isLoading) return <Skeleton className="h-96" />;

  const projectName = project ? project.name : projectId;
  const displayIncidentCode = incident?.code || (investigation as any)?.incidentCode || 'INC-1001';

  if (!investigation) {
    return (
      <div className="p-8 text-center text-textMuted font-mono">
        No investigation report available for incident {displayIncidentCode} in project {projectName}.
      </div>
    );
  }

  const inv = investigation;
  const rootCauseTitle = inv.primaryHypothesis
    ? (inv.primaryHypothesis.title?.includes('Suspected Root Cause for') && inv.primaryHypothesis.description
        ? inv.primaryHypothesis.description
        : inv.primaryHypothesis.title)
    : undefined;

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
              <SeverityBadge severity={inv.severity} />
              <StatusBadge status={inv.status === 'analyzing' ? 'Investigating' : 'Identified'} />
            </div>
            <h1 className="text-lg font-bold text-textPrimary">{inv.title}</h1>
          </div>

          <div className="flex items-center gap-4 border-l border-borderColor pl-4">
            <div className="text-right">
              <p className="text-[10px] text-textMuted uppercase font-mono tracking-wider mb-1">Investigation Confidence</p>
              <Badge variant="confidence" className="font-mono text-xs px-2.5 py-1">
                {inv.confidence}% CONFIDENCE
              </Badge>
            </div>

            <Button size="sm" variant="outline" onClick={handleReanalyze} isLoading={isTriggering} className="gap-1.5 text-xs">
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Re-analyze</span>
            </Button>
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

      {/* 6. TIMELINE */}
      <Timeline events={inv.timeline} />

      {/* 7. EVIDENCE CHAIN */}
      <EvidenceChain chain={inv.evidenceChain} />

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
