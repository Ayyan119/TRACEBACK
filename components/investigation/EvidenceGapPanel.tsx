import React from 'react';
import { EvidenceGapItem } from '@/types';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { AlertCircle, UploadCloud } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

interface EvidenceGapPanelProps {
  gaps: EvidenceGapItem[];
  onUploadClick?: () => void;
}

export const EvidenceGapPanel: React.FC<EvidenceGapPanelProps> = ({ gaps, onUploadClick }) => {
  if (!gaps || gaps.length === 0) return null;

  return (
    <Card className="p-4 border-amber-900/40 bg-amber-950/10 space-y-3">
      <div className="flex items-center justify-between border-b border-amber-800/30 pb-2">
        <h3 className="font-semibold text-xs text-statusWarning flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          <span>Evidence Gaps & Recommended Ingestion</span>
        </h3>
        <Badge variant="warning" className="text-[9px]">Action Needed</Badge>
      </div>

      <div className="space-y-3">
        {gaps.map((gap) => (
          <div key={gap.id} className="p-3 bg-bgApp border border-borderColor rounded-md space-y-2 text-xs">
            <div className="flex items-start justify-between gap-2">
              <p className="text-textSecondary leading-relaxed">{gap.gapDescription}</p>
              <Badge variant={gap.impactLevel === 'High' ? 'danger' : 'warning'} className="text-[9px]">
                {gap.impactLevel} Impact
              </Badge>
            </div>

            <div className="p-2 bg-bgSurface border border-borderColor rounded text-[11px] font-mono text-textPrimary flex items-center justify-between flex-wrap gap-2">
              <span>{gap.recommendedNextEvidence}</span>
              <Button size="sm" variant="primary" onClick={onUploadClick} className="gap-1.5 text-[11px] h-7 px-3">
                <UploadCloud className="w-3.5 h-3.5" />
                <span>{gap.actionPrompt}</span>
              </Button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
