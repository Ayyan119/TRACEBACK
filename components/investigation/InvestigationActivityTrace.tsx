'use client';

import React, { useState } from 'react';
import { ActivityTrace } from '@/types';
import { Card } from '@/components/ui/Card';
import { CheckCircle2, ChevronDown, ChevronUp, Terminal } from 'lucide-react';

export const InvestigationActivityTrace: React.FC<{ trace: ActivityTrace[] }> = ({ trace }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Card className="p-4 space-y-2 border-borderColor bg-bgSurface">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-xs font-semibold text-textPrimary hover:text-accentPrimary transition-colors"
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-textMuted" />
          <span className="font-sans text-xs">Investigation execution log ({trace.length} actions)</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-textMuted" /> : <ChevronDown className="w-4 h-4 text-textMuted" />}
      </button>

      {isOpen && (
        <div className="pt-3 mt-2 border-t border-borderColor space-y-1.5 font-mono text-[11px]">
          {trace.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-2 bg-bgApp border border-borderColor/60 rounded text-xs">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-statusSuccess shrink-0" />
                <span className="text-textPrimary">{item.action}</span>
              </div>
              <span className="text-textMuted text-[11px]">{item.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
