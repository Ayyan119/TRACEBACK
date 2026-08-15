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
