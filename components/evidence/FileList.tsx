'use client';

import React from 'react';
import { EvidenceItem } from '@/types';
import { Badge } from '@/components/ui/Badge';
import { FileText, Image, Trash2, CheckCircle2 } from 'lucide-react';

interface FileListProps {
  items: EvidenceItem[];
  onDelete?: (id: string) => void;
}

export const FileList: React.FC<FileListProps> = ({ items, onDelete }) => {
  if (!items || items.length === 0) return null;

  return (
    <div className="space-y-2 pt-2">
      <span className="text-[10px] uppercase font-mono font-semibold text-textMuted tracking-wider block">
        Ingested File Artifacts ({items.length})
      </span>

      <div className="space-y-1.5 font-mono text-xs">
        {items.map((item) => (
          <div
            key={item.id}
            className="p-2.5 bg-bgApp border border-borderColor rounded flex items-center justify-between"
          >
            <div className="flex items-center gap-2.5">
              {item.type === 'screenshot' ? (
                <Image className="w-4 h-4 text-accentPrimary" />
              ) : (
                <FileText className="w-4 h-4 text-accentPrimary" />
              )}
              <div>
                <p className="font-semibold text-textPrimary">{item.title}</p>
                <p className="text-[10px] text-textMuted font-sans">
                  {item.source} • {((item.fileSize || 1024) / (1024 * 1024)).toFixed(1)} MB
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Badge variant="success" className="text-[9px] gap-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Ready</span>
              </Badge>
              {onDelete && (
                <button
                  onClick={() => onDelete(item.id)}
                  className="p-1 text-textMuted hover:text-statusDanger transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
