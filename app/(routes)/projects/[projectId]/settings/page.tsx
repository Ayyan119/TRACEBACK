'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Project } from '@/types';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { DeleteProjectModal } from '@/components/projects/DeleteProjectModal';
import { Settings, Sliders, Bell, Database, Monitor, Moon, Sun, FolderGit2, AlertTriangle, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectSettingsPage() {
  const params = useParams();
  const projectId = (params?.projectId as string) || '';

  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [themeMode, setThemeMode] = useState<'dark' | 'light' | 'system'>('dark');
  const [activeTab, setActiveTab] = useState<'Appearance' | 'Workspace' | 'Project' | 'AI settings' | 'Data sources'>('Appearance');
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  useEffect(() => {
    if (!projectId) return;
    setIsLoading(true);
    api.getProject(projectId).then((p) => {
      setProject(p);
      setIsLoading(false);
    }).catch(() => setIsLoading(false));
  }, [projectId]);

  const handleThemeChange = (mode: 'dark' | 'light' | 'system') => {
    setThemeMode(mode);
    localStorage.setItem('tb_theme', mode);
    let active = mode;
    if (mode === 'system') {
      active = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', active);
  };

  const tabs: ('Appearance' | 'Workspace' | 'Project' | 'AI settings' | 'Data sources')[] = [
    'Appearance',
    'Workspace',
    'Project',
    'AI settings',
    'Data sources',
  ];

  if (isLoading) return <Skeleton className="h-64" />;

  const currentProj = project || {
    id: projectId || 'workspace',
    name: (projectId || 'Workspace').toUpperCase().replace('-', ' '),
    slug: projectId,
    environment: 'production' as const,
    description: 'Workspace environment',
    serviceCount: 0,
    activeIncidentCount: 0,
    createdAt: '',
    updatedAt: '',
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto text-xs pb-10">
      <div className="border-b border-borderColor pb-3">
        <h1 className="text-lg font-bold text-textPrimary font-mono">
          {currentProj.name} — Project & Workspace Settings
        </h1>
        <p className="text-xs text-textSecondary mt-0.5">
          Configure appearance theme, project telemetry, AI threshold parameters, and environment settings.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-borderColor pb-2 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-1.5 rounded font-medium text-xs transition-colors whitespace-nowrap ${
              activeTab === tab
                ? 'bg-accentPrimary text-white font-semibold'
                : 'bg-bgSurface text-textSecondary hover:bg-bgSurfaceHover border border-borderColor'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Appearance Settings */}
      {activeTab === 'Appearance' && (
        <Card className="p-5 space-y-4">
          <CardHeader className="p-0 border-b border-borderColor pb-2">
            <CardTitle className="text-xs font-semibold text-textPrimary flex items-center gap-2">
              <Monitor className="w-4 h-4 text-accentPrimary" />
              <span>Theme Appearance Preference</span>
            </CardTitle>
          </CardHeader>

          <p className="text-textSecondary text-xs">
            Select your visual theme. Dark theme provides optimized low-light contrast. Light theme provides crisp daytime clarity.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <button
              onClick={() => handleThemeChange('dark')}
              className={`p-4 rounded-lg border text-left space-y-2 transition-all ${
                themeMode === 'dark' ? 'border-accentPrimary bg-accentSubtle/10' : 'border-borderColor bg-bgApp hover:border-borderColor/80'
              }`}
            >
              <Moon className="w-5 h-5 text-accentPrimary" />
              <p className="font-bold text-textPrimary text-xs font-mono">Dark Theme</p>
              <p className="text-[10px] text-textMuted font-mono">Graphite dark theme</p>
            </button>

            <button
              onClick={() => handleThemeChange('light')}
              className={`p-4 rounded-lg border text-left space-y-2 transition-all ${
                themeMode === 'light' ? 'border-accentPrimary bg-accentSubtle/10' : 'border-borderColor bg-bgApp hover:border-borderColor/80'
              }`}
            >
              <Sun className="w-5 h-5 text-amber-500" />
              <p className="font-bold text-textPrimary text-xs font-mono">Light Theme</p>
              <p className="text-[10px] text-textMuted font-mono">Subtle light theme</p>
            </button>

            <button
              onClick={() => handleThemeChange('system')}
              className={`p-4 rounded-lg border text-left space-y-2 transition-all ${
                themeMode === 'system' ? 'border-accentPrimary bg-accentSubtle/10' : 'border-borderColor bg-bgApp hover:border-borderColor/80'
              }`}
            >
              <Monitor className="w-5 h-5 text-textSecondary" />
              <p className="font-bold text-textPrimary text-xs font-mono">System Default</p>
              <p className="text-[10px] text-textMuted font-mono">Syncs with OS theme</p>
            </button>
          </div>
        </Card>
      )}

      {/* Project Settings */}
      {activeTab === 'Project' && (
        <Card className="p-5 space-y-3">
          <CardHeader className="p-0 border-b border-borderColor pb-2">
            <CardTitle className="text-xs font-semibold text-textPrimary flex items-center gap-2">
              <FolderGit2 className="w-4 h-4 text-accentPrimary" />
              <span>Project Configuration ({currentProj.name})</span>
            </CardTitle>
          </CardHeader>
          <div className="space-y-2 font-mono text-xs">
            <div className="flex justify-between py-1.5 border-b border-borderColor">
              <span className="text-textMuted">Project Identifier:</span>
              <span className="text-accentPrimary font-bold">{currentProj.id}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-borderColor">
              <span className="text-textMuted">Environment Tier:</span>
              <span className="text-textPrimary font-bold">{currentProj.environment}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-borderColor">
              <span className="text-textMuted">Monitored Microservices:</span>
              <span className="text-textPrimary font-bold">{currentProj.serviceCount} services</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-borderColor">
              <span className="text-textMuted">Active Incident Reports:</span>
              <span className="text-statusWarning font-bold">{currentProj.activeIncidentCount} active</span>
            </div>
          </div>
        </Card>
      )}

      {/* AI Settings */}
      {activeTab === 'AI settings' && (
        <Card className="p-5 space-y-4">
          <CardHeader className="p-0 border-b border-borderColor pb-2">
            <CardTitle className="text-xs font-semibold text-textPrimary flex items-center gap-2">
              <Sliders className="w-4 h-4 text-accentPrimary" />
              <span>AI Investigation Parameters</span>
            </CardTitle>
          </CardHeader>

          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 bg-bgApp border border-borderColor rounded flex items-center justify-between">
              <div>
                <p className="font-bold text-textPrimary">LangGraph Execution Mode</p>
                <p className="text-[10px] text-textMuted font-sans">Single investigation workflow with telemetry tools</p>
              </div>
              <Badge variant="success">Active</Badge>
            </div>

            <div className="p-3 bg-bgApp border border-borderColor rounded flex items-center justify-between">
              <div>
                <p className="font-bold text-textPrimary">Confidence Threshold</p>
                <p className="text-[10px] text-textMuted font-sans">Minimum hypothesis confidence required for automated triage</p>
              </div>
              <span className="font-bold text-accentPrimary">85% Confidence</span>
            </div>
          </div>
        </Card>
      )}

      {/* Other tabs */}
      {activeTab !== 'Appearance' && activeTab !== 'Project' && activeTab !== 'AI settings' && (
        <Card className="p-5">
          <h3 className="text-xs font-semibold text-textPrimary">{activeTab} Configuration</h3>
          <p className="text-[11px] text-textMuted mt-1">
            Configure {activeTab.toLowerCase()} properties and integrations for project {currentProj.name}.
          </p>
        </Card>
      )}

      {/* Workspace Deletion Section */}
      <div className="border border-statusDanger/40 rounded-lg p-5 bg-statusDanger/5 space-y-3 mt-8">
        <div className="flex items-center gap-2 text-statusDanger">
          <AlertTriangle className="w-4 h-4" />
          <h3 className="text-xs font-bold font-mono uppercase tracking-wider">Workspace Deletion</h3>
        </div>
        <p className="text-xs text-textSecondary leading-relaxed">
          Permanently delete the <strong className="font-mono text-textPrimary">{currentProj.name}</strong> workspace and all associated services, incidents, investigations, knowledge runbooks, and telemetry log references.
        </p>
        <div className="pt-2">
          <Button
            variant="danger"
            size="sm"
            onClick={() => setIsDeleteModalOpen(true)}
            className="gap-1.5 font-mono text-xs"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Delete {currentProj.name} Workspace</span>
          </Button>
        </div>
      </div>

      {/* Delete Project Modal */}
      {currentProj && (
        <DeleteProjectModal
          isOpen={isDeleteModalOpen}
          project={currentProj}
          onClose={() => setIsDeleteModalOpen(false)}
        />
      )}
    </div>
  );
}
