import React from 'react';
import { TimelineEvent } from '@/types';
import { formatDate } from '@/lib/utils/format';
import { GitCommit, AlertCircle, Activity, Wrench, ShieldAlert } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';

export const Timeline: React.FC<{ events: TimelineEvent[] }> = ({ events }) => {
  const categoryIcons = {
    deployment: GitCommit,
    alert: AlertCircle,
    anomaly: Activity,
    config_change: Wrench,
    action: ShieldAlert,
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xs uppercase font-mono tracking-wider text-textMuted">
          Incident Chronology & Timeline
        </CardTitle>
      </CardHeader>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-borderColor">
        {events.map((event) => {
          const Icon = (event.category && categoryIcons[event.category]) ? categoryIcons[event.category] : Activity;
          return (
            <div key={event.id} className="relative flex items-start gap-4 text-xs">
              <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-bgSurface border border-borderColor flex items-center justify-center text-accentPrimary z-10">
                <Icon className="w-3 h-3" />
              </div>

              <div className="flex-1 bg-bgApp/50 border border-borderColor rounded-md p-3">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-semibold text-textPrimary">{event.title}</span>
                  <span className="font-mono text-[10px] text-textMuted">
                    {formatDate(event.timestamp, 'HH:mm:ss (MMM d)')}
                  </span>
                </div>
                <p className="text-textSecondary leading-relaxed text-[11px]">{event.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
