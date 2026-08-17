'use client';

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { EnvironmentTier, CreateServiceInput, ServiceType } from '@/types';
import { Button } from '@/components/ui/Button';
import { FolderPlus, Plus, Trash2, X, Server } from 'lucide-react';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (projectId: string) => void;
}

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [name, setName] = useState('');
  const [environment, setEnvironment] = useState<EnvironmentTier>('production');
  const [description, setDescription] = useState('');
  const [ownerTeam, setOwnerTeam] = useState('');
  const [repositoryUrl, setRepositoryUrl] = useState('');

  // Initial Services state
  const [initialServices, setInitialServices] = useState<CreateServiceInput[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [internalIsOpen, setInternalIsOpen] = useState(false);
  const showModal = isOpen || internalIsOpen;

  useEffect(() => {
    setMounted(true);
    const handleOpen = () => setInternalIsOpen(true);
    window.addEventListener('tb_open_create_project_modal', handleOpen);
    return () => window.removeEventListener('tb_open_create_project_modal', handleOpen);
  }, []);

  const handleCloseModal = () => {
    setInternalIsOpen(false);
    onClose();
  };

  if (!showModal || !mounted) return null;

  const handleAddServiceRow = () => {
    setInitialServices((prev) => [
      ...prev,
      {
        name: '',
        type: 'API',
        description: '',
        ownerTeam: '',
      },
    ]);
  };

  const handleRemoveServiceRow = (index: number) => {
    setInitialServices((prev) => prev.filter((_, i) => i !== index));
  };

  const handleServiceChange = (index: number, field: keyof CreateServiceInput, value: string) => {
    setInitialServices((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    setErrorMessage(null);
    try {
      const validInitialServices = initialServices.filter((s) => s.name && s.name.trim() !== '');

      const created = await api.createProject({
        name: name.trim(),
        environment,
        description: description.trim() || undefined,
        ownerTeam: ownerTeam.trim() || undefined,
        repositoryUrl: repositoryUrl.trim() || undefined,
        initialServices: validInitialServices.length > 0 ? validInitialServices : undefined,
      });

      handleCloseModal();
      window.dispatchEvent(new Event('tb_user_profile_updated'));
      if (onSuccess) {
        onSuccess(created.id);
      } else {
        router.push(`/projects/${created.id}`);
      }
    } catch (err: any) {
      console.error('Failed to create project:', err);
      setErrorMessage(err?.message || 'Failed to create project. Please check backend log references.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const modalContent = (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-[9999] flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-bgSurface border border-borderColor rounded-xl w-full max-w-xl p-5 space-y-4 shadow-2xl max-h-[85vh] overflow-y-auto font-mono text-xs z-[10000]">
        <div className="flex items-center justify-between border-b border-borderColor pb-3">
          <div className="flex items-center gap-2">
            <FolderPlus className="w-4 h-4 text-accentPrimary" />
            <h3 className="text-sm font-bold text-textPrimary font-mono">Create New Workspace Project</h3>
          </div>
          <button onClick={handleCloseModal} className="text-textMuted hover:text-textPrimary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Section 1: Project Metadata */}
          <div className="space-y-3">
            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Project Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Calculator"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-sans"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-mono text-textSecondary mb-1">
                  Environment Tier *
                </label>
                <select
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value as EnvironmentTier)}
                  className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-sans"
                >
                  <option value="production">Production</option>
                  <option value="staging">Staging</option>
                  <option value="development">Development</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-textSecondary mb-1">
                  Owner / Team (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Core Engineering"
                  value={ownerTeam}
                  onChange={(e) => setOwnerTeam(e.target.value)}
                  className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-sans"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Description (Optional)
              </label>
              <textarea
                rows={2}
                placeholder="Brief summary of project services and architecture..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary resize-none font-sans"
              />
            </div>

            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Repository URL (Optional)
              </label>
              <input
                type="url"
                placeholder="e.g. https://github.com/example/calculator"
                value={repositoryUrl}
                onChange={(e) => setRepositoryUrl(e.target.value)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-mono text-[11px]"
              />
            </div>
          </div>

          {/* Section 2: Initial Services Section */}
          <div className="pt-3 border-t border-borderColor space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-mono font-semibold uppercase text-textMuted flex items-center gap-1.5">
                <Server className="w-3.5 h-3.5 text-accentPrimary" />
                <span>Initial Services ({initialServices.length})</span>
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddServiceRow}
                className="gap-1 text-[11px] h-7 px-2"
              >
                <Plus className="w-3 h-3" />
                <span>Add Service</span>
              </Button>
            </div>

            {initialServices.length === 0 ? (
              <p className="text-[11px] text-textMuted italic font-mono bg-bgApp p-2.5 rounded border border-borderColor text-center">
                Optional: You can create a project with 0 services and add them later.
              </p>
            ) : (
              <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
                {initialServices.map((srv, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-bgApp border border-borderColor rounded-md space-y-2 relative"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[10px] uppercase font-bold text-accentPrimary">
                        Service #{idx + 1}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveServiceRow(idx)}
                        className="text-textMuted hover:text-statusDanger p-1 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <div>
                        <input
                          type="text"
                          required
                          placeholder="Service Name * (e.g. calculation-api)"
                          value={srv.name}
                          onChange={(e) => handleServiceChange(idx, 'name', e.target.value)}
                          className="w-full bg-bgSurface border border-borderColor rounded p-1.5 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-mono"
                        />
                      </div>

                      <div>
                        <select
                          value={srv.type || 'API'}
                          onChange={(e) => handleServiceChange(idx, 'type', e.target.value as ServiceType)}
                          className="w-full bg-bgSurface border border-borderColor rounded p-1.5 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-mono"
                        >
                          <option value="API">API</option>
                          <option value="Frontend">Frontend</option>
                          <option value="Backend">Backend</option>
                          <option value="Worker">Worker</option>
                          <option value="Database">Database</option>
                          <option value="Cache">Cache</option>
                          <option value="Queue">Queue</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <input
                        type="text"
                        placeholder="Description (Optional)"
                        value={srv.description || ''}
                        onChange={(e) => handleServiceChange(idx, 'description', e.target.value)}
                        className="w-full bg-bgSurface border border-borderColor rounded p-1.5 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-sans"
                      />
                      <input
                        type="text"
                        placeholder="Owner Team (Optional)"
                        value={srv.ownerTeam || ''}
                        onChange={(e) => handleServiceChange(idx, 'ownerTeam', e.target.value)}
                        className="w-full bg-bgSurface border border-borderColor rounded p-1.5 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-sans"
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {errorMessage && (
            <div className="p-2.5 bg-statusDanger/10 border border-statusDanger/30 rounded text-statusDanger text-xs font-mono">
              {errorMessage}
            </div>
          )}

          <div className="flex justify-end gap-2 pt-3 border-t border-borderColor">
            <Button type="button" variant="ghost" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isSubmitting} disabled={!name.trim()}>
              Create Project
            </Button>
          </div>
        </form>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
