'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Incident } from '@/types';
import { Button } from '@/components/ui/Button';
import { AlertTriangle, Trash2, X } from 'lucide-react';

interface DeleteIncidentModalProps {
  isOpen: boolean;
  incident: Incident;
  projectId: string;
  projectName?: string;
  onClose: () => void;
  onSuccess?: () => void;
}

export const DeleteIncidentModal: React.FC<DeleteIncidentModalProps> = ({
  isOpen,
  incident,
  projectId,
  projectName,
  onClose,
  onSuccess,
}) => {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleDelete = async () => {
    setIsDeleting(true);
    setErrorMsg(null);
    try {
      await api.deleteIncident(incident.id, projectId);
      onClose();
      if (onSuccess) {
        onSuccess();
      } else {
        router.push(`/projects/${projectId}/incidents`);
      }
      router.refresh();
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to delete incident record');
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
            <h3 className="text-sm font-bold font-mono uppercase">Delete Incident Record</h3>
          </div>
          <button onClick={onClose} className="text-textMuted hover:text-textPrimary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3 text-xs">
          <p className="text-textPrimary leading-relaxed">
            Incident: <strong className="font-mono text-statusDanger">{incident.code}</strong> — {incident.title}
          </p>

          <p className="text-textMuted text-[11px] bg-bgApp p-2.5 rounded border border-borderColor font-mono">
            This will permanently remove this incident report and its associated AI root-cause investigation data from project <strong className="text-textPrimary">{projectName || projectId}</strong>.
          </p>

          <div className="flex justify-end gap-2 pt-3 border-t border-borderColor">
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="danger" isLoading={isDeleting} onClick={handleDelete} className="gap-1.5 font-mono">
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete Incident</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
