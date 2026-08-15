'use client';

import React, { useState } from 'react';
import { api } from '@/lib/api';
import { Service } from '@/types';
import { Button } from '@/components/ui/Button';
import { AlertTriangle, Trash2, X } from 'lucide-react';

interface DeleteServiceModalProps {
  isOpen: boolean;
  service: Service;
  projectId: string;
  projectName?: string;
  onClose: () => void;
  onSuccess: () => void;
}

export const DeleteServiceModal: React.FC<DeleteServiceModalProps> = ({
  isOpen,
  service,
  projectId,
  projectName,
  onClose,
  onSuccess,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);

  if (!isOpen) return null;

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await api.deleteService(service.id, projectId);
      onSuccess();
      onClose();
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-bgSurface border border-borderColor rounded-lg w-full max-w-md p-5 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-borderColor pb-3">
          <div className="flex items-center gap-2 text-statusDanger">
            <AlertTriangle className="w-4 h-4" />
            <h3 className="text-sm font-bold font-mono uppercase">Delete Microservice</h3>
          </div>
          <button onClick={onClose} className="text-textMuted hover:text-textPrimary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3 text-xs">
          <p className="text-textPrimary leading-relaxed">
            You are about to delete microservice <strong className="font-mono text-accentPrimary">{service.name}</strong> from project <strong className="font-mono text-textPrimary">{projectName || projectId}</strong>.
          </p>

          <p className="text-textMuted text-[11px] bg-bgApp p-2.5 rounded border border-borderColor font-mono">
            This will remove telemetry tracking, dependency links, and recent deployment history for this service. This action cannot be undone.
          </p>

          <div className="flex justify-end gap-2 pt-3 border-t border-borderColor">
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="danger" isLoading={isDeleting} onClick={handleDelete} className="gap-1.5 font-mono">
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete Service</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
