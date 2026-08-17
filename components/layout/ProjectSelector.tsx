'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname, useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Project } from '@/types';
import { CreateProjectModal } from '@/components/projects/CreateProjectModal';
import { FolderGit2, ChevronDown, Check, Plus } from 'lucide-react';

export const ProjectSelector: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const params = useParams();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  let currentProjectId = (params?.projectId as string) || '';
  if (!currentProjectId && pathname) {
    const match = pathname.match(/\/projects\/([^\/]+)/);
    if (match) currentProjectId = match[1];
  }

  const fetchProjects = async () => {
    try {
      const data = await api.getProjects();
      setProjects(data || []);
    } catch {
      setProjects([]);
    }
  };

  useEffect(() => {
    setMounted(true);
    fetchProjects();

    const handleUpdate = () => fetchProjects();
    window.addEventListener('tb_user_profile_updated', handleUpdate);
    return () => window.removeEventListener('tb_user_profile_updated', handleUpdate);
  }, []);

  const activeProject = projects.find((p) => p.id === currentProjectId || p.slug === currentProjectId) || projects[0] || null;

  const handleSelectProject = (projectId: string) => {
    setIsOpen(false);
    if (projectId === currentProjectId) return;

    if (currentProjectId && pathname.includes(`/projects/${currentProjectId}`)) {
      const newPath = pathname.replace(`/projects/${currentProjectId}`, `/projects/${projectId}`);
      router.push(newPath);
    } else {
      router.push(`/projects/${projectId}`);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-bgApp hover:bg-bgSurfaceHover border border-borderColor text-xs font-semibold text-textPrimary transition-colors shadow-xs"
      >
        <FolderGit2 className="w-3.5 h-3.5 text-accentPrimary" />
        <span className="font-mono">{activeProject ? activeProject.name : 'No Active Workspace'}</span>
        <ChevronDown className="w-3 h-3 text-textMuted" />
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-1 w-60 bg-bgSurface border border-borderColor rounded-md shadow-2xl z-50 py-1 space-y-0.5">
          <div className="px-3 py-1 text-[10px] uppercase font-mono font-semibold text-textMuted border-b border-borderColor">
            Switch Workspace Project
          </div>

          <div className="max-h-56 overflow-y-auto space-y-0.5">
            {projects.map((p) => {
              const isSelected = p.id === activeProject.id;
              return (
                <button
                  key={p.id}
                  onClick={() => handleSelectProject(p.slug || p.id)}
                  className={`w-full text-left px-3 py-2 flex items-center justify-between text-xs transition-colors ${
                    isSelected ? 'bg-accentSubtle text-accentPrimary font-semibold' : 'text-textPrimary hover:bg-bgSurfaceHover'
                  }`}
                >
                  <div>
                    <p className="font-mono">{p.name}</p>
                    <p className="text-[10px] text-textMuted font-sans">{p.environment}</p>
                  </div>
                  {isSelected && <Check className="w-3.5 h-3.5 text-accentPrimary" />}
                </button>
              );
            })}
          </div>

          <div className="border-t border-borderColor pt-1 px-1">
            <button
              onClick={() => {
                setIsOpen(false);
                window.dispatchEvent(new Event('tb_open_create_project_modal'));
              }}
              className="w-full text-left px-2.5 py-1.5 rounded text-xs text-accentPrimary hover:bg-accentSubtle/20 flex items-center gap-1.5 font-semibold font-mono"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>+ New Project</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
