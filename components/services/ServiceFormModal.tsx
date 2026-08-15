'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Service, ServiceType } from '@/types';
import { Button } from '@/components/ui/Button';
import { Server, X } from 'lucide-react';

interface ServiceFormModalProps {
  isOpen: boolean;
  projectId: string;
  serviceToEdit?: Service | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const ServiceFormModal: React.FC<ServiceFormModalProps> = ({
  isOpen,
  projectId,
  serviceToEdit,
  onClose,
  onSuccess,
}) => {
  const isEditing = !!serviceToEdit;

  const [name, setName] = useState('');
  const [type, setType] = useState<ServiceType>('API');
  const [description, setDescription] = useState('');
  const [ownerTeam, setOwnerTeam] = useState('');
  const [repositoryUrl, setRepositoryUrl] = useState('');
  const [environment, setEnvironment] = useState('Production');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      if (serviceToEdit) {
        setName(serviceToEdit.name || '');
        setType(serviceToEdit.type || 'API');
        setDescription(serviceToEdit.description || '');
        setOwnerTeam(serviceToEdit.ownerTeam || '');
        setRepositoryUrl(serviceToEdit.repositoryUrl || '');
        setEnvironment(serviceToEdit.environment || 'Production');
      } else {
        setName('');
        setType('API');
        setDescription('');
        setOwnerTeam('');
        setRepositoryUrl('');
        setEnvironment('Production');
      }
    }
  }, [isOpen, serviceToEdit]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    try {
      if (isEditing && serviceToEdit) {
        await api.updateService(serviceToEdit.id, {
          name: name.trim(),
          type,
          description: description.trim() || undefined,
          ownerTeam: ownerTeam.trim() || undefined,
          repositoryUrl: repositoryUrl.trim() || undefined,
          environment: environment.trim() || undefined,
        }, projectId);
      } else {
        await api.createService({
          projectId,
          name: name.trim(),
          type,
          description: description.trim() || undefined,
          ownerTeam: ownerTeam.trim() || undefined,
          repositoryUrl: repositoryUrl.trim() || undefined,
          environment: environment.trim() || undefined,
        });
      }

      onSuccess();
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-bgSurface border border-borderColor rounded-lg w-full max-w-md p-5 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-borderColor pb-3">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-accentPrimary" />
            <h3 className="text-sm font-bold text-textPrimary font-mono">
              {isEditing ? `Edit Service (${serviceToEdit?.name})` : 'Add New Microservice'}
            </h3>
          </div>
          <button onClick={onClose} className="text-textMuted hover:text-textPrimary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="block text-[11px] font-mono text-textSecondary mb-1">
              Service Name *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. calculation-api"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-mono"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Service Type
              </label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as ServiceType)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-mono"
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

            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Owner Team (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Backend Team"
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
              placeholder="Handles calculation requests and algorithmic execution..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary resize-none font-sans"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Repository URL (Optional)
              </label>
              <input
                type="url"
                placeholder="e.g. https://github.com/example/api"
                value={repositoryUrl}
                onChange={(e) => setRepositoryUrl(e.target.value)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-mono text-[11px]"
              />
            </div>

            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Environment
              </label>
              <input
                type="text"
                placeholder="Production"
                value={environment}
                onChange={(e) => setEnvironment(e.target.value)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-sans"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-borderColor">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" isLoading={isSubmitting} disabled={!name.trim()}>
              {isEditing ? 'Save Changes' : 'Create Service'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
