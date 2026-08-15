'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Project, Incident, EvidenceItem, LogEvent } from '@/types';
import { SeverityBadge } from '@/components/incidents/SeverityBadge';
import { StatusBadge } from '@/components/incidents/StatusBadge';
import { EvidenceUploader } from '@/components/evidence/EvidenceUploader';
import { EvidenceViewer } from '@/components/evidence/EvidenceViewer';
import { LogViewer } from '@/components/logs/LogViewer';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { DeleteIncidentModal } from '@/components/incidents/DeleteIncidentModal';
import { ArrowLeft, Sparkles, Clock, Server, FileText, Terminal, Trash2 } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectIncidentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.projectId as string) || 'shopflow';
  const incidentId = (params?.incidentId as string) || 'inc-1042';

  const [project, setProject] = useState<Project | null>(null);
  const [incident, setIncident] = useState<Incident | null>(null);
  const [evidenceList, setEvidenceList] = useState<EvidenceItem[]>([]);
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [activeTab, setActiveTab] = useState<'evidence' | 'logs'>('evidence');
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [proj, inc, evList, logList] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        api.getIncident(incidentId, projectId).catch(() => null),
        api.getEvidence(incidentId, projectId).catch(() => []),
        api.getLogs(incidentId, { projectId }).catch(() => []),
      ]);
      setProject(proj);
      setIncident(inc);
      setEvidenceList(evList || []);
      setLogs(logList || []);
    } catch (err) {
      console.error('Failed to load incident details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [incidentId, projectId]);

  if (isLoading) return <Skeleton className="h-96" />;

  const projectName = project ? project.name : projectId;

  const inc = incident || {
    id: incidentId,
    code: 'INC-1042',
    projectId,
    title: 'Incident Telemetry Hub',
    description: 'Ingested logs and metrics repository for incident triage.',
    severity: 'High' as const,
    status: 'Investigating' as const,
    affectedService: 'order-service',
    detectedAt: '14:03 UTC',
    duration: '22m',
    confidence: 91,
    updatedAt: 'Just now',
    reporter: 'Datadog Alert Manager',
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-xs pb-12">
      {/* Top Bar */}
      <div className="flex items-center justify-between border-b border-borderColor pb-3">
        <Link
          href={`/projects/${projectId}/incidents`}
          className="inline-flex items-center gap-1.5 text-textSecondary hover:text-textPrimary transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to {projectName} Incident Directory</span>
        </Link>
        <span className="font-mono text-[10px] text-textMuted uppercase">Workspace: {projectName}</span>
      </div>

      {/* Incident Header */}
      <div className="bg-bgSurface border border-borderColor p-5 rounded-lg space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-accentPrimary text-sm">{inc.code}</span>
              <SeverityBadge severity={inc.severity} />
              <StatusBadge status={inc.status} />
            </div>
            <h1 className="text-lg font-bold text-textPrimary">{inc.title}</h1>
            <p className="text-xs text-textSecondary">{inc.description}</p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Button
              variant="primary"
              size="sm"
              onClick={() => router.push(`/projects/${projectId}/incidents/${inc.id}/investigation`)}
              className="gap-2 font-semibold font-mono"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch AI Report</span>
            </Button>
            <Button
              variant="danger"
              size="sm"
              onClick={() => setIsDeleteModalOpen(true)}
              className="gap-1.5 font-mono"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete Incident</span>
            </Button>
          </div>
        </div>

        <div className="pt-3 border-t border-borderColor flex flex-wrap gap-6 text-xs text-textMuted font-mono">
          <div className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-accentPrimary" />
            <span>Detected: {inc.detectedAt}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Server className="w-3.5 h-3.5 text-accentPrimary" />
            <span>Service: {inc.affectedService}</span>
          </div>
        </div>
      </div>

      {/* Evidence & Logs Tabs */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 border-b border-borderColor pb-2">
          <button
            onClick={() => setActiveTab('evidence')}
            className={`px-3 py-1.5 rounded font-medium text-xs transition-colors flex items-center gap-1.5 ${
              activeTab === 'evidence'
                ? 'bg-accentPrimary text-white font-semibold'
                : 'bg-bgSurface text-textSecondary hover:bg-bgSurfaceHover border border-borderColor'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Evidence Artifacts ({evidenceList.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`px-3 py-1.5 rounded font-medium text-xs transition-colors flex items-center gap-1.5 ${
              activeTab === 'logs'
                ? 'bg-accentPrimary text-white font-semibold'
                : 'bg-bgSurface text-textSecondary hover:bg-bgSurfaceHover border border-borderColor'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Telemetry Log Console ({logs.length})</span>
          </button>
        </div>

        {activeTab === 'evidence' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <EvidenceUploader incidentId={inc.id} onUploadComplete={fetchData} />
            <EvidenceViewer evidence={evidenceList} />
          </div>
        ) : (
          <LogViewer logs={logs} isLoading={false} />
        )}
      </div>

      {inc && (
        <DeleteIncidentModal
          isOpen={isDeleteModalOpen}
          incident={inc}
          projectId={projectId}
          onClose={() => setIsDeleteModalOpen(false)}
        />
      )}
    </div>
  );
}
