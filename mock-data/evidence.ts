import { EvidenceItem } from '@/types';

export const mockEvidence: EvidenceItem[] = [
  {
    id: 'ev-1',
    incidentId: 'inc-1042',
    type: 'log',
    title: 'order-service-production.log',
    source: 'Datadog Ingestion',
    fileSize: 44040192, // 42 MB
    mimeType: 'text/plain',
    status: 'ready',
    rawContent: `2026-08-14T14:03:12Z [ERROR] order-service: HTTP POST https://payment.internal/v1/charge timed out after 3000ms. Retrying (1/5)...
2026-08-14T14:03:15Z [WARN] order-service: HTTP POST https://payment.internal/v1/charge timed out after 3000ms. Retrying (2/5)...
2026-08-14T14:03:18Z [ERROR] order-service: Payment request failed: 504 Gateway Timeout. Transaction rollback initiated for order #ord_9941.`,
    uploadedAt: '14:05 UTC',
  },
  {
    id: 'ev-2',
    incidentId: 'inc-1042',
    type: 'screenshot',
    title: 'dashboard-latency-spike.png',
    source: 'Grafana Screenshot',
    fileSize: 1887436, // 1.8 MB
    mimeType: 'image/png',
    status: 'ready',
    uploadedAt: '14:10 UTC',
  },
  {
    id: 'ev-3',
    incidentId: 'inc-1042',
    type: 'metric',
    title: 'payment_latency_histogram.csv',
    source: 'Prometheus Export',
    fileSize: 81920,
    status: 'ready',
    rawContent: `timestamp,service,p50,p95,p99,error_rate
13:30:00,payment-service,420,500,850,0.007
13:55:00,payment-service,1200,1800,2400,0.021
14:03:00,payment-service,2800,3500,4200,0.124`,
    uploadedAt: '14:12 UTC',
  },
  {
    id: 'ev-4',
    incidentId: 'inc-1042',
    type: 'deployment',
    title: 'v2.4.1 deployment manifest & diff',
    source: 'GitHub Release Action',
    fileSize: 12400,
    status: 'ready',
    rawContent: `Deployment v2.4.1 to shopflow-production
Author: Alex Chen
Commit: d8f3a9e
Changelog: Updated payment retry count default from 2 to 5 retries.`,
    uploadedAt: '13:30 UTC',
  },
];
