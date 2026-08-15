'use client';

import React from 'react';
import { KnowledgeDocument } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { FileText, Calendar, User, Layers, CheckCircle2, AlertTriangle, X, Trash2, Eye } from 'lucide-react';

interface DocumentDetailsModalProps {
  isOpen: boolean;
  doc: KnowledgeDocument;
  projectId: string;
  projectName?: string;
  onClose: () => void;
  onDelete: (doc: KnowledgeDocument) => void;
}

export const DocumentDetailsModal: React.FC<DocumentDetailsModalProps> = ({
  isOpen,
  doc,
  projectId,
  projectName,
  onClose,
  onDelete,
}) => {
  if (!isOpen) return null;

  const ext = doc.fileType || doc.name.split('.').pop()?.toUpperCase() || 'FILE';

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-bgSurface border border-borderColor rounded-lg w-full max-w-md p-5 space-y-4 shadow-2xl">
        <div className="flex items-center justify-between border-b border-borderColor pb-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-accentPrimary" />
            <h3 className="text-sm font-bold text-textPrimary font-mono">Knowledge Document Details</h3>
          </div>
          <button onClick={onClose} className="text-textMuted hover:text-textPrimary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4 text-xs">
          {/* Header Metadata Banner */}
          <div className="p-3 bg-bgApp border border-borderColor rounded space-y-2">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h4 className="font-bold text-textPrimary font-mono text-sm leading-tight">{doc.name}</h4>
                <p className="text-[11px] text-textMuted mt-0.5">Project Workspace: <strong className="text-accentPrimary font-mono">{projectName || projectId}</strong></p>
              </div>
              <Badge variant="outline" className="font-mono text-[9px] uppercase">{ext}</Badge>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <Badge variant="info" size="sm">{doc.category}</Badge>
              {doc.status === 'INDEXED' && (
                <Badge variant="success" size="sm" className="gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  <span>INDEXED</span>
                </Badge>
              )}
              {doc.status === 'INDEXING' && (
                <Badge variant="warning" size="sm" className="gap-1">
                  <span>INDEXING...</span>
                </Badge>
              )}
              {doc.status === 'FAILED' && (
                <Badge variant="danger" size="sm" className="gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  <span>FAILED</span>
                </Badge>
              )}
            </div>
          </div>

          {/* Key Attributes Grid */}
          <div className="grid grid-cols-2 gap-2 font-mono text-[11px]">
            <div className="p-2.5 bg-bgApp border border-borderColor rounded">
              <span className="text-[10px] text-textMuted block">File Size</span>
              <span className="font-bold text-textPrimary">{doc.fileSize || '320 KB'}</span>
            </div>

            <div className="p-2.5 bg-bgApp border border-borderColor rounded">
              <span className="text-[10px] text-textMuted block">Vector Chunks</span>
              <span className="font-bold text-accentPrimary">{doc.chunks} chunks</span>
            </div>

            <div className="p-2.5 bg-bgApp border border-borderColor rounded">
              <span className="text-[10px] text-textMuted block">Uploaded Date</span>
              <span className="text-textPrimary">{doc.uploadedAt}</span>
            </div>

            <div className="p-2.5 bg-bgApp border border-borderColor rounded">
              <span className="text-[10px] text-textMuted block">Uploaded By</span>
              <span className="text-textPrimary">{doc.uploadedBy || 'Alex Chen'}</span>
            </div>
          </div>

          {/* Description Summary */}
          {doc.summary && (
            <div className="space-y-1">
              <span className="text-[10px] text-textMuted uppercase font-mono tracking-wider">Document Summary</span>
              <p className="text-textSecondary leading-relaxed bg-bgApp p-2.5 rounded border border-borderColor text-[11px]">
                {doc.summary}
              </p>
            </div>
          )}

          {/* Action Footer */}
          <div className="flex items-center justify-between pt-3 border-t border-borderColor">
            <Button
              variant="danger"
              size="sm"
              onClick={() => {
                onClose();
                onDelete(doc);
              }}
              className="gap-1.5 font-mono text-[11px]"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete Document</span>
            </Button>

            <Button variant="ghost" size="sm" onClick={onClose} className="font-mono text-xs">
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
