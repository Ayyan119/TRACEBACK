'use client';

import React, { useState } from 'react';
import { EvidenceItem } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { FileText, Image, ChevronDown, ChevronUp } from 'lucide-react';

export const EvidenceViewer: React.FC<{ evidence: EvidenceItem[] }> = ({ evidence }) => {
  const [selectedId, setSelectedId] = useState<string | null>(evidence[0]?.id || null);

  const activeItem = evidence.find((e) => e.id === selectedId) || evidence[0];

  return (
    <Card className="p-4 space-y-3">
      <div className="border-b border-borderColor pb-2 flex items-center justify-between">
        <h3 className="font-semibold text-xs text-textPrimary flex items-center gap-2">
          <FileText className="w-3.5 h-3.5 text-accentPrimary" />
          <span>Ingested Telemetry Artifacts ({evidence.length})</span>
        </h3>
      </div>

      <div className="space-y-2">
        {evidence.map((item) => {
          const isSelected = item.id === activeItem?.id;
          return (
            <div
              key={item.id}
              onClick={() => setSelectedId(item.id)}
              className={`p-3 bg-bgApp border rounded-md cursor-pointer transition-all space-y-2 text-xs ${
                isSelected ? 'border-accentPrimary bg-accentSubtle/10' : 'border-borderColor hover:border-borderColor/80'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-textPrimary font-mono">{item.title}</p>
                  <p className="text-[10px] text-textMuted font-mono">Source: {item.source} • {item.uploadedAt}</p>
                </div>
                <Badge variant="outline" className="text-[9px] uppercase font-mono">{item.type}</Badge>
              </div>

              {isSelected && item.rawContent && (
                <div className="pt-2 border-t border-borderColor font-mono text-[11px]">
                  <div className="p-2.5 bg-black/60 rounded border border-borderColor text-textPrimary overflow-x-auto">
                    <pre className="whitespace-pre-wrap">{item.rawContent}</pre>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
};
