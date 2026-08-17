'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Project } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { CreateProjectModal } from '@/components/projects/CreateProjectModal';
import { FolderGit2, Plus, ArrowRight } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectsDirectoryPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const data = await api.getProjects();
      setProjects(data || []);
    } catch (e) {
      console.error('Failed to fetch projects in directory:', e);
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreated = (newProjectId: string) => {
    fetchProjects();
    router.push(`/projects/${newProjectId}`);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-xs pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-borderColor pb-3">
        <div>
          <h1 className="text-lg font-bold text-textPrimary font-mono">Workspace Projects Directory</h1>
          <p className="text-xs text-textSecondary mt-0.5">
            Select an isolated production environment workspace or create a new project.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={() => window.dispatchEvent(new Event('tb_open_create_project_modal'))}
          className="gap-1.5 font-semibold text-xs shrink-0 font-mono"
        >
          <Plus className="w-4 h-4" />
          <span>New Project</span>
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-64" />
      ) : projects.length === 0 ? (
        <div className="p-8 border border-dashed border-borderColor rounded-xl bg-bgSurface/40 text-center space-y-4 max-w-lg mx-auto my-12 shadow-sm">
          <div className="w-12 h-12 rounded-2xl bg-accentSubtle border border-accentPrimary/30 flex items-center justify-center text-accentPrimary mx-auto">
            <FolderGit2 className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-textPrimary font-mono">No Workspace Projects Yet</h3>
            <p className="text-xs text-textSecondary leading-relaxed font-sans">
              Your workspace is currently clean and empty. Create your first isolated microservice project to start tracking telemetry, deployments, and incidents.
            </p>
          </div>
          <Button
            variant="primary"
            size="md"
            onClick={() => window.dispatchEvent(new Event('tb_open_create_project_modal'))}
            className="gap-2 font-mono font-semibold mx-auto shadow-md"
          >
            <Plus className="w-4 h-4" />
            <span>Create Your First Project</span>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {projects.map((p) => (
            <Card key={p.id} hoverable className="p-4 space-y-3 flex flex-col justify-between">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FolderGit2 className="w-4 h-4 text-accentPrimary" />
                    <span className="font-bold text-sm text-textPrimary font-mono">{p.name}</span>
                  </div>
                  <Badge variant="outline">{p.environment}</Badge>
                </div>
                <p className="text-xs text-textSecondary leading-relaxed">{p.description}</p>
              </div>

              <div className="pt-3 border-t border-borderColor space-y-2">
                <div className="flex justify-between font-mono text-[11px] text-textMuted">
                  <span>Services: {p.serviceCount}</span>
                  <span className="text-statusWarning font-bold">Incidents: {p.activeIncidentCount}</span>
                </div>

                <Link
                  href={`/projects/${p.slug || p.id}`}
                  className="w-full py-2 px-3 bg-bgApp hover:bg-bgSurfaceHover border border-borderColor rounded text-xs font-semibold text-accentPrimary flex items-center justify-center gap-1.5 transition-colors font-mono"
                >
                  <span>Open {p.name} Workspace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
