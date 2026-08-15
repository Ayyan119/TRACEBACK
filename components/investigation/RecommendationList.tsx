import React from 'react';
import { ActionableRecommendation } from '@/types';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { ShieldCheck, ArrowRight, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export const RecommendationList: React.FC<{ recommendations: ActionableRecommendation[] }> = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <Card className="p-4 border-statusSuccess/30 bg-statusSuccess/5 space-y-3 shadow-xs">
      <CardHeader className="p-0 border-statusSuccess/20 pb-2">
        <CardTitle className="text-xs uppercase font-mono font-bold tracking-wider text-statusSuccess flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-statusSuccess shrink-0" />
          <span>Actionable Remediation Recommendations</span>
        </CardTitle>
      </CardHeader>

      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="p-3 bg-bgSurface border border-borderColor rounded-md space-y-2 text-xs shadow-xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Badge variant={rec.category === 'Immediate' ? 'danger' : rec.category === 'Investigation' ? 'warning' : 'info'} className="uppercase text-[9px] font-mono font-bold">
                  {rec.category}
                </Badge>
                <span className="font-bold text-textPrimary text-xs font-sans">{rec.action}</span>
              </div>
              <Badge variant={rec.risk === 'High' ? 'danger' : rec.risk === 'Medium' ? 'warning' : 'default'} className="text-[9px] font-mono shrink-0">
                Risk: {rec.risk}
              </Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] text-textSecondary pt-2 border-t border-borderColor/60">
              <div>
                <span className="font-mono text-textMuted uppercase text-[9px] block font-semibold">Reason / Context:</span>
                <p className="mt-0.5 leading-relaxed font-sans">{rec.reason}</p>
              </div>
              <div>
                <span className="font-mono text-textMuted uppercase text-[9px] block font-semibold">Expected Outcome:</span>
                <p className="text-statusSuccess mt-0.5 font-bold font-sans">{rec.expectedResult}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
