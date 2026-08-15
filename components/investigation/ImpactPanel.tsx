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
    <Card className="p-4 space-y-3 border-borderColor bg-bgSurface">
      <div className="border-b border-borderColor pb-2">
        <h3 className="font-bold text-xs text-textPrimary flex items-center gap-2 font-mono uppercase tracking-wider">
          <AlertCircle className="w-3.5 h-3.5 text-statusWarning" />
          <span>System & Customer Impact</span>
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="p-2.5 bg-bgApp border border-borderColor rounded-md">
          <span className="text-[10px] text-textMuted flex items-center gap-1 font-mono uppercase tracking-wider font-semibold">
            <Layers className="w-3 h-3 text-accentPrimary" />
            Functionality
          </span>
          <p className="font-bold text-textPrimary mt-1 text-[11px] font-sans">{impact.affectedFunctionality}</p>
        </div>

        <div className="p-2.5 bg-bgApp border border-borderColor rounded-md">
          <span className="text-[10px] text-textMuted flex items-center gap-1 font-mono uppercase tracking-wider font-semibold">
            <Server className="w-3 h-3 text-accentPrimary" />
            Affected Services
          </span>
          <p className="font-bold text-textPrimary mt-1 text-[11px] font-mono">
            {impact.affectedServices.join(', ')}
          </p>
        </div>

        <div className="p-2.5 bg-bgApp border border-borderColor rounded-md">
          <span className="text-[10px] text-textMuted flex items-center gap-1 font-mono uppercase tracking-wider font-semibold">
            <Clock className="w-3 h-3 text-accentPrimary" />
            Duration
          </span>
          <p className="font-bold text-textPrimary mt-1 text-[11px] font-mono">
            {impact.currentDuration} {formattedStartTime ? `(Started ${formattedStartTime})` : ''}
          </p>
        </div>

        <div className="p-2.5 bg-bgApp border border-borderColor rounded-md">
          <span className="text-[10px] text-textMuted flex items-center gap-1 font-mono uppercase tracking-wider font-semibold">
            Estimated Impact
          </span>
          <p className="font-bold text-statusDanger mt-1 text-[11px] font-sans">{impact.estimatedImpact}</p>
        </div>
      </div>
    </Card>
  );
};
