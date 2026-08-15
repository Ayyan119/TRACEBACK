'use client';

import React, { useState } from 'react';
import { ActivityTrace } from '@/types';
import { Card } from '@/components/ui/Card';
import { CheckCircle2, ChevronDown, ChevronUp, Clock, Terminal } from 'lucide-react';

export const InvestigationActivityTrace: React.FC<{ trace: ActivityTrace[] }> = ({ trace }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Card className="p-4 space-y-2 border-borderColor">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-xs font-semibold text-textPrimary hover:text-accentPrimary transition-colors"
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-accentPrimary" />
          <span>Investigation Activity ({trace.length} agent actions executed)</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isOpen && (
        <div className="pt-3 mt-2 border-t border-borderColor space-y-2 font-mono text-[11px]">
          {trace.map((item) => (
            <div key={item.id} className="flex items-center justify-between p-1.5 bg-bgApp rounded hover:bg-bgSurfaceHover/50 transition-colors">
              <div className="flex items-center gap-2">
                {item.status === 'done' ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-statusSuccess shrink-0" />
                ) : (
                  <Clock className="w-3.5 h-3.5 text-statusInfo animate-spin shrink-0" />
                )}
                <span className="text-textPrimary">{item.action}</span>
              </div>
              <span className="text-textMuted text-[10px]">{item.timestamp}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
