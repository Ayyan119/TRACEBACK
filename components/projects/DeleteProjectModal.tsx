'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Project, ProjectExportReport } from '@/types';
import { Button } from '@/components/ui/Button';
import { AlertTriangle, Download, Trash2, X, FileText, CheckCircle2 } from 'lucide-react';

interface DeleteProjectModalProps {
  isOpen: boolean;
  project: Project;
  onClose: () => void;
  onSuccess?: () => void;
}

export const DeleteProjectModal: React.FC<DeleteProjectModalProps> = ({
  isOpen,
  project,
  onClose,
  onSuccess,
}) => {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2>(1);
  const [confirmName, setConfirmName] = useState('');
  const [exportReport, setExportReport] = useState<ProjectExportReport | null>(null);
  const [isExported, setIsExported] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoadingReport, setIsLoadingReport] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setStep(1);
      setConfirmName('');
      setIsExported(false);
      setExportReport(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const isNameMatched = confirmName.trim() === project.name.trim();

  const handleStep1Proceed = async () => {
    if (!isNameMatched) return;
    setIsLoadingReport(true);
    setErrorMsg(null);
    try {
      const report = await api.exportProject(project.id);
      setExportReport(report);
    } catch (err) {
      console.warn('Export report pre-fetch error (continuing to delete step):', err);
    } finally {
      setIsLoadingReport(false);
      setStep(2);
    }
  };

  const projectExportName = (project.slug || project.name || project.id).toLowerCase().replace(/[\s_]+/g, '-').replace(/[^a-z0-9-]/g, '');

  const handleDownloadReport = () => {
    if (!exportReport) return;
    const jsonStr = JSON.stringify(exportReport, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectExportName}-project-export.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setIsExported(true);
  };

  const handleFinalDelete = async () => {
    setIsDeleting(true);
    setErrorMsg(null);
    try {
      await api.deleteProject(project.id);

      // Find fallback project
      const remaining = await api.getProjects();
      const fallbackTarget = remaining.length > 0 ? (remaining[0].slug || remaining[0].id) : '';

      onClose();
      if (onSuccess) {
        onSuccess();
      }
      if (fallbackTarget) {
        router.push(`/projects/${fallbackTarget}`);
      } else {
        router.push('/projects');
      }
      router.refresh();
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to delete project workspace');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-bgSurface border border-statusDanger/40 rounded-lg w-full max-w-md p-5 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-borderColor pb-3">
          <div className="flex items-center gap-2 text-statusDanger">
            <AlertTriangle className="w-4 h-4" />
            <h3 className="text-sm font-bold font-mono uppercase">Delete Project Workspace</h3>
          </div>
          <button onClick={onClose} className="text-textMuted hover:text-textPrimary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        {step === 1 ? (
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-statusDanger/10 border border-statusDanger/30 rounded text-statusDanger space-y-1">
              <p className="font-bold font-mono text-[11px] uppercase">Warning: Destructive Action</p>
              <p className="text-textPrimary text-[11px] leading-relaxed">
                This will permanently remove the <strong className="font-mono text-statusDanger">{project.name}</strong> project and all its associated isolated resources.
              </p>
            </div>

            <div className="p-3 bg-bgApp border border-borderColor rounded space-y-1.5 font-mono text-[11px]">
              <p className="text-textMuted uppercase font-semibold text-[10px]">Associated Resources to be deleted:</p>
              <ul className="text-textSecondary space-y-1 pl-2">
                <li>• {project.serviceCount} Monitored Microservices</li>
                <li>• {project.activeIncidentCount} Incident Reports & Investigations</li>
                <li>• Indexed Knowledge Runbooks & Vector Embeddings</li>
                <li>• Log Stream References & Deployment Records</li>
              </ul>
            </div>

            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1.5">
                Type the project name <strong className="text-textPrimary select-all">{project.name}</strong> to confirm:
              </label>
              <input
                type="text"
                value={confirmName}
                onChange={(e) => setConfirmName(e.target.value)}
                placeholder={project.name}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-statusDanger font-mono"
              />
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-borderColor">
              <Button variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button
                variant="danger"
                disabled={!isNameMatched}
                isLoading={isLoadingReport}
                onClick={handleStep1Proceed}
              >
                Continue Deletion
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4 text-xs">
            <div className="p-3 bg-accentSubtle/20 border border-accentPrimary/40 rounded space-y-1 text-textPrimary">
              <p className="font-bold font-mono text-[11px] uppercase text-accentPrimary">
                Save Project Export Report
              </p>
              <p className="text-textSecondary text-[11px] leading-relaxed">
                Before permanently deleting <strong className="font-mono text-textPrimary">{project.name}</strong>, you can download a complete JSON report of all project services, incidents, investigations, and knowledge metadata.
              </p>
            </div>

            <div className="flex items-center justify-between p-3 bg-bgApp border border-borderColor rounded font-mono text-[11px]">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-accentPrimary" />
                <span>{projectExportName}-project-export.json</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownloadReport}
                className="gap-1 text-[11px] h-7 px-2"
              >
                {isExported ? <CheckCircle2 className="w-3.5 h-3.5 text-statusSuccess" /> : <Download className="w-3.5 h-3.5" />}
                <span>{isExported ? 'Downloaded' : 'Download Report'}</span>
              </Button>
            </div>

            {errorMsg && (
              <div className="p-2.5 bg-rose-950/30 border border-rose-800/40 rounded text-statusDanger text-xs">
                {errorMsg}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-3 border-t border-borderColor">
              <Button variant="ghost" onClick={onClose}>
                Cancel
              </Button>
              <Button
                variant="danger"
                isLoading={isDeleting}
                onClick={handleFinalDelete}
                className="gap-1.5 font-mono"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Permanently Delete Project</span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
