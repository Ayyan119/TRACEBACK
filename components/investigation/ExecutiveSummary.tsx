import React from 'react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
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
    <Card className="mb-6 border-borderColor bg-bgSurface shadow-md overflow-hidden">
      <CardHeader className="border-borderColor pb-2 bg-bgApp/50">
        <CardTitle className="flex items-center gap-2 text-textPrimary text-xs font-mono font-bold uppercase tracking-wide">
          <FileText className="w-4 h-4 text-accentPrimary" />
          <span>Executive Diagnosis & Root Cause</span>
        </CardTitle>
      </CardHeader>

      <div className="p-4 space-y-4 text-xs">
        {rootCause && (
          <div className="p-3.5 bg-statusDanger/10 border border-statusDanger/30 rounded-md text-textPrimary shadow-xs">
            <div className="flex items-center gap-2 font-semibold font-mono uppercase text-[11px] text-statusDanger mb-1.5">
              <AlertTriangle className="w-4 h-4 text-statusDanger shrink-0" />
              <span>Identified Primary Root Cause</span>
            </div>
            <p className="font-bold text-sm text-textPrimary leading-snug font-sans">{rootCause}</p>
          </div>
        )}

        {cleanedSummary && (
          <div className="space-y-1">
            <p className="text-textMuted uppercase font-mono text-[10px] tracking-wider font-semibold">
              Analysis Summary
            </p>
            <p className="text-textPrimary text-xs leading-relaxed font-sans">{cleanedSummary}</p>
          </div>
        )}
      </div>
    </Card>
  );
};
