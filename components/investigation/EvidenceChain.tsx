import React from 'react';
import { EvidenceChainLink } from '@/types';
import { Card } from '@/components/ui/Card';
import { ArrowDown, Link2 } from 'lucide-react';

export const EvidenceChain: React.FC<{ chain: EvidenceChainLink[] }> = ({ chain }) => {
  return (
    <Card className="p-4 space-y-3">
      <div className="border-b border-borderColor pb-2">
        <h3 className="font-semibold text-xs text-textPrimary flex items-center gap-2">
          <Link2 className="w-3.5 h-3.5 text-accentPrimary" />
          <span>Evidence Chain Diagram (Causal Sequence)</span>
        </h3>
      </div>

      <div className="space-y-2 py-1">
        {chain.map((link, idx) => (
          <React.Fragment key={link.id}>
            <div className="p-3 bg-bgApp border border-borderColor rounded-md flex items-start gap-3 text-xs">
              <div className="w-6 h-6 rounded bg-accentSubtle border border-accentPrimary/40 flex items-center justify-center font-mono font-bold text-accentPrimary text-[11px] shrink-0">
                {link.stepNumber}
              </div>
              <div>
                <h4 className="font-semibold text-textPrimary">{link.title}</h4>
                <p className="text-[11px] text-textSecondary mt-0.5 leading-relaxed">{link.description}</p>
              </div>
            </div>

            {idx < chain.length - 1 && (
              <div className="flex justify-center py-0.5">
                <ArrowDown className="w-3.5 h-3.5 text-textMuted" />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </Card>
  );
};
