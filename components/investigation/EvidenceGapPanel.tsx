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
    <Card className="p-5 border-borderColor bg-bgSurface space-y-4">
      <div className="flex items-center justify-between border-b border-borderColor pb-3">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-statusWarning" />
          <h2 className="text-sm font-semibold text-textPrimary tracking-tight">Missing evidence gaps</h2>
        </div>
        <Badge variant="warning" className="text-[10px] font-mono">Action recommended</Badge>
      </div>

      <div className="space-y-3">
        {gaps.map((gap) => (
          <div key={gap.id} className="p-3.5 bg-bgApp border border-borderColor rounded-lg space-y-2.5 text-xs">
            <div className="flex items-start justify-between gap-2">
              <p className="text-textSecondary leading-relaxed">{gap.gapDescription}</p>
              <Badge variant={gap.impactLevel === 'High' ? 'danger' : 'warning'} className="text-[10px] font-mono">
                {gap.impactLevel} impact
              </Badge>
            </div>

            <div className="p-2.5 bg-bgSurface border border-borderColor rounded-md text-xs font-mono text-textPrimary flex items-center justify-between flex-wrap gap-2">
              <span>{gap.recommendedNextEvidence}</span>
              <Button size="sm" variant="primary" onClick={onUploadClick} className="gap-1.5 text-xs h-7 px-3 font-mono">
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
