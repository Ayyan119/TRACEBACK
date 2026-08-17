'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Project, Service, Incident, KnowledgeDocument, Investigation } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { IncidentTable } from '@/components/incidents/IncidentTable';
import { SeverityBadge } from '@/components/incidents/SeverityBadge';
import { StatusBadge } from '@/components/incidents/StatusBadge';
import {
  FolderGit2,
  Server,
  AlertTriangle,
  FileText,
  Activity,
  Plus,
  ArrowRight,
  Sparkles,
  BookOpen,
  UploadCloud,
} from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.projectId as string) || '';

  const [project, setProject] = useState<Project | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [docs, setDocs] = useState<KnowledgeDocument[]>([]);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadProjectData = async () => {
    setIsLoading(true);
    const [proj, srvList, incList, docList] = await Promise.all([
      api.getProject(projectId).catch(() => null),
      api.getServices({ projectId }).catch(() => []),
      api.getIncidents({ projectId }).catch(() => []),
      api.getKnowledge({ projectId }).catch(() => []),
    ]);

    setProject(proj);
    setServices(srvList || []);
    setIncidents(incList || []);
    setDocs(docList || []);
    setIsLoading(false);

    if (incList && incList.length > 0) {
      api.getInvestigation(incList[0].id, projectId)
        .then((inv) => setInvestigation(inv))
        .catch(() => setInvestigation(null));
    } else {
      setInvestigation(null);
    }
  };

  useEffect(() => {
    if (['incidents', 'services', 'knowledge', 'settings', 'new'].includes(projectId)) {
      router.replace('/projects');
      return;
    }
    loadProjectData();
  }, [projectId]);

  if (isLoading) return <Skeleton className="h-96" />;

  if (!project) {
    return (
      <div className="p-8 text-center space-y-4 max-w-md mx-auto my-12 bg-bgSurface border border-borderColor rounded-lg">
        <div className="w-12 h-12 rounded-full bg-accentSubtle text-accentPrimary flex items-center justify-center mx-auto">
          <FolderGit2 className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-textPrimary font-mono">Workspace Project Not Found</h2>
          <p className="text-xs text-textMuted mt-1">The requested project '{projectId}' does not exist or has been removed.</p>
        </div>
        <Button variant="primary" size="sm" onClick={() => router.push('/projects')} className="font-mono text-xs">
          Go to Projects Directory
        </Button>
      </div>
    );
  }

  const p = project;

  const activeIncidents = incidents.filter((i) => i.status !== 'Resolved');
  const criticalServices = services.filter((s) => s.health !== 'Healthy');

  return (
    <div className="space-y-3.5 max-w-7xl mx-auto text-xs pb-6">
      {/* Top Header Banner */}
      <div className="bg-bgSurface border border-borderColor p-3.5 rounded-lg space-y-2">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded bg-accentSubtle text-accentPrimary border border-accentPrimary/40">
              <FolderGit2 className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-semibold text-textPrimary font-mono">{p.name} Workspace</h1>
                <Badge variant="outline" className="text-[10px] py-0.5">{p.environment}</Badge>
              </div>
              <p className="text-xs text-textSecondary mt-0.5">{p.description}</p>
            </div>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={() => router.push(`/projects/${projectId}/incidents/new`)}
            className="gap-1.5 text-xs font-semibold shrink-0 h-8"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Report Incident</span>
          </Button>
        </div>
      </div>

      {/* KPI Stats Bar (Project-Isolated) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2.5">
        <Card className="p-3 space-y-1">
          <span className="text-[10px] text-textMuted uppercase font-mono tracking-wider font-semibold">Active Incidents</span>
          <div className="flex items-baseline justify-between">
            <span className="text-lg font-bold font-mono text-statusDanger">{activeIncidents.length}</span>
            <AlertTriangle className="w-3.5 h-3.5 text-statusDanger" />
          </div>
          <p className="text-[10px] text-textMuted">Isolated to {p.name}</p>
        </Card>

        <Card className="p-3 space-y-1">
          <span className="text-[10px] text-textMuted uppercase font-mono tracking-wider font-semibold">Monitored Services</span>
          <div className="flex items-baseline justify-between">
            <span className="text-lg font-bold font-mono text-textPrimary">{services.length}</span>
            <Server className="w-3.5 h-3.5 text-accentPrimary" />
          </div>
          <p className="text-[10px] text-textMuted">
            {services.length === 0
              ? 'No services configured'
              : criticalServices.length > 0
              ? `${criticalServices.length} degraded/critical`
              : '100% Healthy'}
          </p>
        </Card>

        <Card className="p-3 space-y-1">
          <span className="text-[10px] text-textMuted uppercase font-mono tracking-wider font-semibold">Knowledge Chunks</span>
          <div className="flex items-baseline justify-between">
            <span className="text-lg font-bold font-mono text-textPrimary">
              {docs.reduce((acc, d) => acc + (d.chunks || 0), 0)}
            </span>
            <FileText className="w-3.5 h-3.5 text-accentPrimary" />
          </div>
          <p className="text-[10px] text-textMuted">{docs.length} indexed runbooks</p>
        </Card>

        <Card className="p-3 space-y-1">
          <span className="text-[10px] text-textMuted uppercase font-mono tracking-wider font-semibold">Telemetry Stream</span>
          <div className="flex items-baseline justify-between">
            <span className="text-lg font-bold font-mono text-statusSuccess">
              {services.length > 0 ? 'Active' : 'Standby'}
            </span>
            <Activity className="w-3.5 h-3.5 text-statusSuccess" />
          </div>
          <p className="text-[10px] text-textMuted">Real-time stream channel</p>
        </Card>
      </div>

      {/* Primary Active Investigation Workbench Banner */}
      {investigation && (
        <Card className="p-3 border-accentPrimary/40 bg-accentSubtle/10 space-y-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-borderColor/60 pb-1.5">
            <div className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-accentPrimary" />
              <span className="font-mono text-xs font-semibold text-textPrimary uppercase">Active AI Investigation Workbench</span>
              <Badge variant="confidence" className="text-[9px]">
                {investigation.confidence}% CONFIDENCE
              </Badge>
            </div>
            <Link
              href={`/projects/${projectId}/incidents/${investigation.incidentId}/investigation`}
              className="text-xs font-semibold text-accentPrimary hover:underline flex items-center gap-1"
            >
              <span>Open Investigation Workbench</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-0.5">
            <h3 className="text-xs font-bold text-textPrimary">{investigation.title}</h3>
            <p className="text-[11px] text-textSecondary leading-relaxed">{investigation.summary}</p>
          </div>
        </Card>
      )}

      {/* Services Topology Section */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-xs text-textPrimary flex items-center gap-2">
            <Server className="w-3.5 h-3.5 text-accentPrimary" />
            <span>{p.name} Microservices Topology</span>
          </h3>
          {services.length > 0 && (
            <Link href={`/projects/${projectId}/services`} className="text-xs text-accentPrimary hover:underline font-mono">
              View All Services →
            </Link>
          )}
        </div>

        {services.length === 0 ? (
          <Card className="p-4 text-center space-y-2 border-dashed border-borderColor">
            <div className="w-8 h-8 rounded-full bg-bgApp border border-borderColor flex items-center justify-center mx-auto text-textMuted">
              <Server className="w-4 h-4" />
            </div>
            <div>
              <p className="font-bold text-textPrimary text-xs font-mono">No services configured yet for {p.name}</p>
              <p className="text-textMuted text-[11px] mt-0.5">
                Register microservices or connect telemetry sources to monitor health and P95 latency.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push(`/projects/${projectId}/services`)}
              className="gap-1.5 text-xs font-mono"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Configure Services</span>
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
            {services.map((srv) => (
              <Card
                key={srv.id}
                onClick={() => router.push(`/projects/${projectId}/services`)}
                hoverable
                className="p-3 space-y-1.5 cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold font-mono text-textPrimary text-xs">{srv.name}</span>
                  <Badge
                    variant={srv.health === 'Healthy' ? 'success' : srv.health === 'Degraded' ? 'warning' : 'danger'}
                    size="sm"
                  >
                    {srv.health}
                  </Badge>
                </div>

                <div className="space-y-0.5 font-mono text-[10px] text-textMuted pt-1 border-t border-borderColor">
                  <div className="flex justify-between">
                    <span>Environment:</span>
                    <span className="text-textSecondary">{srv.environment || 'Production'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Error Rate:</span>
                    <span className={srv.errorRatePercent > 1 ? 'text-statusDanger font-bold' : 'text-textSecondary'}>
                      {srv.errorRatePercent}%
                    </span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Incident History Table */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-xs text-textPrimary flex items-center gap-2">
            <AlertTriangle className="w-3.5 h-3.5 text-statusDanger" />
            <span>{p.name} Incident Directory</span>
          </h3>
          {incidents.length > 0 && (
            <Link href={`/projects/${projectId}/incidents`} className="text-xs text-accentPrimary hover:underline font-mono">
              View Incident Directory →
            </Link>
          )}
        </div>

        {incidents.length === 0 ? (
          <Card className="p-6 text-center space-y-3 border-dashed border-borderColor">
            <div className="w-10 h-10 rounded-full bg-bgApp border border-borderColor flex items-center justify-center mx-auto text-statusSuccess">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <p className="font-bold text-textPrimary text-xs font-mono">No incidents recorded yet for {p.name}</p>
              <p className="text-textMuted text-[11px] mt-0.5">
                Report observed symptoms or upload logs to launch an automated AI root cause investigation.
              </p>
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={() => router.push(`/projects/${projectId}/incidents/new`)}
              className="gap-1.5 text-xs font-mono"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Report Incident</span>
            </Button>
          </Card>
        ) : (
          <IncidentTable incidents={incidents} isLoading={false} projectName={p.name} onRefresh={loadProjectData} />
        )}
      </div>
    </div>
  );
}
