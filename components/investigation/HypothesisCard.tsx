'use client';

import React, { useState } from 'react';
import { Hypothesis } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';

export const HypothesisCard: React.FC<{ hypothesis: Hypothesis }> = ({ hypothesis }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isPrimary = hypothesis.status === 'primary';

  // Fix probability display (handles both 0.945 and 94.5 inputs)
  const probabilityPercent = Math.min(
    100,
    Math.max(0, hypothesis.probability > 1 ? Math.round(hypothesis.probability) : Math.round(hypothesis.probability * 100))
  );

  return (
    <Card className={`p-4 border-borderColor transition-all ${isPrimary ? 'border-accentPrimary/50 bg-bgSurface shadow-xs' : 'bg-bgApp'}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h4 className="text-xs font-bold text-textPrimary font-sans">{hypothesis.title}</h4>
            {isPrimary && (
              <Badge variant="info" className="text-[9px] font-mono gap-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Primary</span>
              </Badge>
            )}
          </div>
          <p className="text-[11px] text-textSecondary leading-relaxed">{hypothesis.description}</p>
        </div>

        <div className="text-right shrink-0">
          <Badge variant={probabilityPercent > 0 ? "confidence" : "warning"} className="font-mono text-[10px]">
            {probabilityPercent > 0 ? `${hypothesis.confidenceLabel} • ${probabilityPercent}% confidence` : 'Unverified'}
          </Badge>
        </div>
      </div>

      {/* Expandable Supporting Evidence */}
      {hypothesis.evidenceItems && hypothesis.evidenceItems.length > 0 && (
        <div className="mt-3 pt-2 border-t border-borderColor">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-[10px] font-mono text-accentPrimary hover:underline cursor-pointer"
          >
            <span>{isExpanded ? 'Hide Supporting Evidence' : `View Supporting Evidence (${hypothesis.evidenceItems.length})`}</span>
            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>

          {isExpanded && (
            <div className="mt-2 space-y-1 font-mono text-[11px]">
              {hypothesis.evidenceItems.map((item) => {
                // Format raw ID text like "Supporting Evidence ID: EVD-LOG-REF-1" into clean labels
                const cleanLabel = item.text.replace(/Supporting Evidence ID:\s*/i, 'Verified Evidence: ');
                return (
                  <div key={item.id} className="flex items-center gap-2 text-textSecondary">
                    <span className={item.isSupporting ? 'text-statusSuccess font-bold' : 'text-statusDanger font-bold'}>
                      {item.isSupporting ? '✓' : '✗'}
                    </span>
                    <span>{cleanLabel}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </Card>
  );
};
