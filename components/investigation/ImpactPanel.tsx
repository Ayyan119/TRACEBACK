import React from 'react';
import { ImpactDetails } from '@/types';
import { Card } from '@/components/ui/Card';
import { AlertCircle, Clock, Server, Layers } from 'lucide-react';

export const ImpactPanel: React.FC<{ impact: ImpactDetails }> = ({ impact }) => {
  // Format raw ISO string (e.g. 2026-08-15T15:18:50.050120Z) into clean readable date
  const formatTime = (timeStr?: string) => {
    if (!timeStr) return '';
    try {
      const date = new Date(timeStr);
      if (isNaN(date.getTime())) return timeStr;
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' UTC';
    } catch {
      return timeStr;
    }
  };

  const formattedStartTime = formatTime(impact.startTime);

  return (
    <Card className="p-5 space-y-4 border-borderColor bg-bgSurface">
      <div className="flex items-center gap-2 pb-3 border-b border-borderColor">
        <AlertCircle className="w-4 h-4 text-statusWarning" />
        <h2 className="text-sm font-semibold text-textPrimary tracking-tight">System & customer impact</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="p-3 bg-bgApp border border-borderColor rounded-lg space-y-1">
          <span className="text-[11px] text-textMuted font-medium flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-accentPrimary" />
            Functionality
          </span>
          <p className="font-semibold text-textPrimary text-xs font-sans leading-snug">{impact.affectedFunctionality}</p>
        </div>

        <div className="p-3 bg-bgApp border border-borderColor rounded-lg space-y-1">
          <span className="text-[11px] text-textMuted font-medium flex items-center gap-1.5">
            <Server className="w-3.5 h-3.5 text-accentPrimary" />
            Affected services
          </span>
          <div className="flex flex-wrap gap-1 mt-0.5">
            {impact.affectedServices.map((svc) => (
              <span key={svc} className="font-mono text-xs text-textPrimary font-medium px-1.5 py-0.5 bg-bgSurface border border-borderColor rounded">
                {svc}
              </span>
            ))}
          </div>
        </div>

        <div className="p-3 bg-bgApp border border-borderColor rounded-lg space-y-1">
          <span className="text-[11px] text-textMuted font-medium flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-accentPrimary" />
            Duration
          </span>
          <p className="font-medium text-textPrimary text-xs font-mono leading-snug">
            {impact.currentDuration} {formattedStartTime ? `(${formattedStartTime})` : ''}
          </p>
        </div>

        <div className="p-3 bg-bgApp border border-borderColor rounded-lg space-y-1">
          <span className="text-[11px] text-textMuted font-medium block">
            Impact level
          </span>
          <p className="font-semibold text-statusDanger text-xs font-sans">{impact.estimatedImpact}</p>
        </div>
      </div>
    </Card>
  );
};
