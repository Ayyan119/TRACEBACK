import React from 'react';
import { Card } from '@/components/ui/Card';
import { FileText, AlertTriangle } from 'lucide-react';

interface ExecutiveSummaryProps {
  summary?: string;
  rootCause?: string;
}

export const ExecutiveSummary: React.FC<ExecutiveSummaryProps> = ({ summary, rootCause }) => {
  if (!summary && !rootCause) return null;

  // Clean raw backend log prefixes (e.g. "FINAL RCA COMPLETE for <uuid>:")
  const cleanedSummary = summary
    ? summary.replace(/^FINAL RCA COMPLETE (for [a-f0-9\-]+:\s*)?/i, '').replace(/\(Confidence:\s*[\d\.]+%?\)/i, '').trim()
    : undefined;

  return (
    <Card className="p-5 space-y-4 border-borderColor bg-bgSurface">
      <div className="flex items-center gap-2 pb-3 border-b border-borderColor">
        <FileText className="w-4 h-4 text-accentPrimary" />
        <h2 className="text-sm font-semibold text-textPrimary tracking-tight">Executive diagnosis</h2>
      </div>

      <div className="space-y-4">
        {rootCause && (
          <div className="p-4 bg-statusDanger/5 border border-statusDanger/25 rounded-lg text-textPrimary">
            <div className="flex items-center gap-2 font-medium text-xs text-statusDanger mb-1">
              <AlertTriangle className="w-4 h-4 text-statusDanger shrink-0" />
              <span>Primary root cause</span>
            </div>
            <p className="font-semibold text-sm text-textPrimary leading-snug">{rootCause}</p>
          </div>
        )}

        {cleanedSummary && (
          <div className="space-y-1">
            <span className="text-xs text-textMuted font-medium block">
              Analysis summary
            </span>
            <p className="text-textPrimary text-xs leading-relaxed font-sans">{cleanedSummary}</p>
          </div>
        )}
      </div>
    </Card>
  );
};
