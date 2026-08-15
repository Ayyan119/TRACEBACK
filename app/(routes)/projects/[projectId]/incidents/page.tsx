'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Project, Incident } from '@/types';
import { IncidentTable } from '@/components/incidents/IncidentTable';
import { Button } from '@/components/ui/Button';
import { Plus, Search, Filter, AlertTriangle } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectIncidentsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.projectId as string) || 'shopflow';

  const [project, setProject] = useState<Project | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [search, setSearch] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);

  const fetchIncidents = async () => {
    setIsLoading(true);
    const [proj, data] = await Promise.all([
      api.getProject(projectId).catch(() => null),
      api.getIncidents({
        projectId,
        severity: filterSeverity !== 'ALL' ? filterSeverity : undefined,
        status: filterStatus !== 'ALL' ? filterStatus : undefined,
      }).catch(() => []),
    ]);
    setProject(proj);
    setIncidents(data);
    setIsLoading(false);
  };

  useEffect(() => {
    fetchIncidents();
  }, [projectId, filterSeverity, filterStatus]);

  const filteredIncidents = incidents.filter((inc) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      inc.title.toLowerCase().includes(q) ||
      inc.code.toLowerCase().includes(q) ||
      inc.affectedService.toLowerCase().includes(q)
    );
  });

  const projectName = project ? project.name : projectId;

  return (
    <div className="space-y-5 max-w-7xl mx-auto text-xs pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-borderColor pb-3">
        <div>
          <h1 className="text-lg font-bold text-textPrimary font-mono">
            {projectName} — Incident Directory
          </h1>
          <p className="text-xs text-textSecondary mt-0.5">
            Production incidents strictly isolated to workspace project <span className="font-mono text-accentPrimary">{projectName}</span>.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={() => router.push(`/projects/${projectId}/incidents/new`)}
          className="gap-1.5 text-xs font-semibold shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Report New Incident</span>
        </Button>
      </div>

      {/* Control Filters Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-bgSurface border border-borderColor p-3 rounded-lg">
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-textMuted" />
          <input
            type="text"
            placeholder="Search incident title, code, service..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-bgApp border border-borderColor rounded pl-8 pr-3 py-1.5 text-xs text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentPrimary"
          />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 text-xs text-textMuted">
            <Filter className="w-3.5 h-3.5" />
            <span>Severity:</span>
          </div>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-bgApp border border-borderColor text-textPrimary text-xs rounded px-2.5 py-1.5 focus:outline-none focus:border-accentPrimary"
          >
            <option value="ALL">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          <div className="flex items-center gap-1.5 text-xs text-textMuted ml-2">
            <span>Status:</span>
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-bgApp border border-borderColor text-textPrimary text-xs rounded px-2.5 py-1.5 focus:outline-none focus:border-accentPrimary"
          >
            <option value="ALL">All Statuses</option>
            <option value="Investigating">Investigating</option>
            <option value="Identified">Identified</option>
            <option value="Monitoring">Monitoring</option>
            <option value="Resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Incident Table */}
      {isLoading ? (
        <Skeleton className="h-64" />
      ) : (
        <IncidentTable incidents={filteredIncidents} isLoading={false} projectName={projectName} onRefresh={fetchIncidents} />
      )}
    </div>
  );
}
