'use client';

import React from 'react';
import { Investigation } from '@/types';
import { Sparkles, RefreshCw, CheckCircle2, AlertCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';

interface InvestigationHeaderProps {
  investigation: Investigation | null;
  onRestart?: () => void;
  isRestarting?: boolean;
}

export const InvestigationHeader: React.FC<InvestigationHeaderProps> = ({
  investigation,
  onRestart,
  isRestarting = false,
}) => {
  if (!investigation) return null;

  const isCompleted = investigation.status === 'completed';
  const isFailed = investigation.status === 'failed';

  return (
    <div className="bg-bgSurface border border-borderColor rounded-lg p-5 mb-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-md bg-accentSubtle text-accentPrimary border border-accentPrimary/30">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-textPrimary flex items-center gap-2">
                AI Investigation Pipeline
                {isCompleted && (
                  <Badge variant="success" className="gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Completed</span>
                  </Badge>
                )}
                {isFailed && (
                  <Badge variant="danger" className="gap-1">
                    <AlertCircle className="w-3 h-3" />
                    <span>Failed</span>
                  </Badge>
                )}
                {!isCompleted && !isFailed && (
                  <Badge variant="info" className="gap-1">
                    <Clock className="w-3 h-3 animate-spin" />
                    <span>{investigation.status.replace('_', ' ')}</span>
                  </Badge>
                )}
              </h1>
              <p className="text-xs text-textSecondary">{investigation.currentStep || investigation.summary}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {investigation.confidence !== undefined && (
            <div className="text-right border-r border-borderColor pr-4">
              <p className="text-[10px] text-textMuted uppercase font-mono tracking-wider">
                {investigation.confidenceSource === 'fallback' ? 'Fallback Status' : 'AI Confidence'}
              </p>
              <p className={`text-lg font-bold font-mono ${investigation.confidenceSource === 'fallback' ? 'text-amber-400' : 'text-accentPrimary'}`}>
                {investigation.confidenceSource === 'fallback' ? 'Degraded' : `${investigation.confidence}%`}
              </p>
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={onRestart}
            isLoading={isRestarting}
            className="gap-2 text-xs"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Re-run Investigation</span>
          </Button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mt-4 pt-4 border-t border-borderColor">
        <div className="flex items-center justify-between text-xs text-textMuted font-mono mb-1.5">
          <span>Execution Progress</span>
          <span>{investigation.progress}%</span>
        </div>
        <div className="w-full h-1.5 bg-bgApp rounded-full overflow-hidden">
          <div
            className="h-full bg-accentPrimary transition-all duration-500 rounded-full"
            style={{ width: `${investigation.progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};
