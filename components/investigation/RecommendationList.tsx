import React from 'react';
import { ActionableRecommendation } from '@/types';
import { Card } from '@/components/ui/Card';
import { ShieldCheck } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export const RecommendationList: React.FC<{ recommendations: ActionableRecommendation[] }> = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <Card className="p-5 border-borderColor bg-bgSurface space-y-4">
      <div className="flex items-center gap-2 pb-3 border-b border-borderColor">
        <ShieldCheck className="w-4 h-4 text-accentPrimary shrink-0" />
        <h2 className="text-sm font-semibold text-textPrimary tracking-tight">Recommended actions</h2>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="p-4 bg-bgApp border border-borderColor rounded-lg space-y-3 text-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2.5">
                <Badge variant={rec.category === 'Immediate' ? 'danger' : rec.category === 'Investigation' ? 'warning' : 'info'} className="text-[10px] font-mono">
                  {rec.category}
                </Badge>
                <span className="font-semibold text-textPrimary text-xs font-sans">{rec.action}</span>
              </div>
              <span className="text-[11px] font-mono text-textMuted shrink-0">
                Risk: <strong className="text-textSecondary font-semibold">{rec.risk}</strong>
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-2.5 border-t border-borderColor/60">
              <div>
                <span className="text-[11px] text-textMuted font-medium block">Reason / Context:</span>
                <p className="mt-0.5 text-textSecondary leading-relaxed">{rec.reason}</p>
              </div>
              <div>
                <span className="text-[11px] text-textMuted font-medium block">Expected outcome:</span>
                <p className="text-statusSuccess mt-0.5 font-medium">{rec.expectedResult}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
