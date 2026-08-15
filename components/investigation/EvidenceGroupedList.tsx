'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { FileText, Image, Activity, GitCommit, BookOpen, ChevronDown, ChevronUp, History } from 'lucide-react';

export const EvidenceGroupedList: React.FC = () => {
  const [expandedId, setExpandedId] = useState<string | null>('ev-log');

  const groups = [
    {
      category: 'Logs',
      icon: FileText,
      items: [
        {
          id: 'ev-log',
          title: 'order-service-production.log',
          source: 'Datadog Log Stream',
          timestamp: '14:03:12 UTC',
          relevance: 'High (96%)',
          excerpt: `2026-08-14T14:03:12Z [ERROR] order-service: HTTP POST https://payment.internal/v1/charge timed out after 3000ms. Retrying (1/5)...`,
          whyItMatters: 'Proves client HTTP connection timeouts originated on payment.internal route before retries fired.',
        },
      ],
    },
    {
      category: 'Metrics',
      icon: Activity,
      items: [
        {
          id: 'ev-metric',
          title: 'payment_latency_histogram.csv',
          source: 'Prometheus Telemetry',
          timestamp: '14:03:00 UTC',
          relevance: 'High (92%)',
          excerpt: `14:03:00,payment-service,2800ms(P50),3500ms(P95),4200ms(P99)`,
          whyItMatters: 'Confirms 7x P95 latency surge specifically on payment-service API.',
        },
      ],
    },
    {
      category: 'Screenshots',
      icon: Image,
      items: [
        {
          id: 'ev-screenshot',
          title: 'dashboard-latency-spike.png',
          source: 'Grafana Snapshot',
          timestamp: '14:10 UTC',
          relevance: 'Medium (88%)',
          excerpt: '[Image binary verified: 1.8 MB PNG file showing step-function latency curve at 13:55 UTC]',
          whyItMatters: 'Visual confirmation of step-function change in response times at 13:55 UTC.',
        },
      ],
    },
    {
      category: 'Deployments',
      icon: GitCommit,
      items: [
        {
          id: 'ev-deployment',
          title: 'v2.4.1 deployment manifest & diff (commit d8f3a9e)',
          source: 'GitHub Actions Release',
          timestamp: '13:30 UTC',
          relevance: 'High (94%)',
          excerpt: `Author: Alex Chen | Change: Increased default retry attempt limit from 2 to 5 retries.`,
          whyItMatters: 'Explains retry amplification: increased retry attempts multiplied connection load by 2.5x under latency.',
        },
      ],
    },
    {
      category: 'Documentation',
      icon: BookOpen,
      items: [
        {
          id: 'ev-doc',
          title: 'payment-service-runbook.md',
          source: 'ShopFlow Runbooks',
          timestamp: 'Indexed 2h ago',
          relevance: 'Medium (81%)',
          excerpt: `Section 4.2: Payment gateway timeout threshold is 3s. Retry backoff must be exponential (initial 100ms, max 3s).`,
          whyItMatters: 'Documents baseline configuration expectations for payment timeouts.',
        },
      ],
    },
    {
      category: 'Previous Incidents',
      icon: History,
      items: [
        {
          id: 'ev-postmortem',
          title: 'q2-payment-timeout-postmortem.md',
          source: 'Post-Mortem Archive',
          timestamp: 'May 12, 2026',
          relevance: 'High (89%)',
          excerpt: `Identical symptom pattern: retry loop without exponential backoff exhausted connection pool during gateway delay.`,
          whyItMatters: 'Past incident confirms identical failure pattern on payment dependency.',
        },
      ],
    },
  ];

  return (
    <Card className="p-4 space-y-4">
      <div className="border-b border-borderColor pb-2">
        <h3 className="font-semibold text-xs text-textPrimary flex items-center gap-2">
          <FileText className="w-3.5 h-3.5 text-accentPrimary" />
          <span>Evidence Artifacts (Grouped by Telemetry Source)</span>
        </h3>
      </div>

      <div className="space-y-4">
        {groups.map((group) => {
          const GroupIcon = group.icon;
          return (
            <div key={group.category} className="space-y-2">
              <h4 className="text-[11px] font-mono font-semibold uppercase text-textMuted flex items-center gap-1.5 tracking-wider">
                <GroupIcon className="w-3 h-3 text-accentPrimary" />
                <span>{group.category} ({group.items.length})</span>
              </h4>

              <div className="space-y-2">
                {group.items.map((item) => {
                  const isExpanded = expandedId === item.id;
                  return (
                    <div key={item.id} className="p-3 bg-bgApp border border-borderColor rounded-md space-y-2 text-xs">
                      <div
                        onClick={() => setExpandedId(isExpanded ? null : item.id)}
                        className="flex items-center justify-between cursor-pointer"
                      >
                        <div>
                          <p className="font-semibold text-textPrimary">{item.title}</p>
                          <p className="text-[10px] text-textMuted font-mono mt-0.5">
                            Source: {item.source} • Timestamp: {item.timestamp}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="info" className="text-[9px] font-mono">{item.relevance}</Badge>
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="pt-2 border-t border-borderColor space-y-2 font-mono text-[11px]">
                          <div className="p-2 bg-black/60 rounded border border-borderColor text-textPrimary overflow-x-auto">
                            <code>{item.excerpt}</code>
                          </div>
                          <div className="p-2 bg-accentSubtle/20 border border-accentPrimary/30 rounded text-accentPrimary font-sans text-xs">
                            <span className="font-semibold font-mono text-[10px] uppercase block mb-0.5">Why It Matters:</span>
                            {item.whyItMatters}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
