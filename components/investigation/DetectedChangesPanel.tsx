import React from 'react';
import { MetricChange } from '@/types';
import { Card } from '@/components/ui/Card';
import { Activity, ArrowUpRight } from 'lucide-react';

export const DetectedChangesPanel: React.FC<{ metrics: MetricChange[] }> = ({ metrics }) => {
  return (
    <Card className="p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-borderColor pb-2">
        <h3 className="font-semibold text-xs text-textPrimary flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-accentPrimary" />
          <span>Detected Changes (vs 30-Day Baseline)</span>
        </h3>
        <span className="text-[10px] font-mono text-textMuted">Measured 14:03–14:25 UTC</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {metrics.map((m) => (
          <div key={m.id} className="p-3 bg-bgApp border border-borderColor rounded-md space-y-1 font-mono">
            <p className="text-[10px] text-textMuted font-sans">{m.name}</p>
            <div className="flex items-baseline justify-between pt-0.5">
              <span className="text-xs text-textMuted">{m.baseline} →</span>
              <span className="text-sm font-bold text-textPrimary">{m.current}</span>
            </div>
            <div className={`flex items-center gap-1 text-[11px] font-bold ${m.isNegative ? 'text-statusDanger' : 'text-statusSuccess'}`}>
              <ArrowUpRight className="w-3 h-3" />
              <span>{m.percentChange}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
