import { Investigation, KnowledgeDocument, EvidenceItem, LogEvent } from '@/types';

export const demoInvestigations: Record<string, Investigation> = {
  'inc-demo-3001': {
    id: 'inv-demo-3001',
    incidentId: 'inc-demo-3001',
    title: 'Canary test deployment memory leak',
    status: 'analyzing',
    severity: 'Low',
    confidence: 78,
    summary: 'Uncollected node buffer references in v0.9.1-beta canary worker.',
    impact: {
      affectedFunctionality: 'Canary Sandbox Cart',
      affectedServices: ['cart-demo'],
      estimatedImpact: 'Sandbox test sessions delayed',
      startTime: '15:10 UTC',
      currentDuration: '1h 05m',
    },
    detectedChanges: [
      {
        id: 'd-mc-1',
        name: 'Heap Used',
        baseline: '120 MB',
        current: '890 MB',
        percentChange: '+641%',
        isNegative: true,
      },
    ],
    primaryHypothesis: {
      id: 'd-hyp-1',
      investigationId: 'inv-demo-3001',
      title: 'Unclosed event listener in session cache worker',
      description: 'Event emitter listeners accumulating without unsubscribe on disconnect.',
      confidenceLabel: 'MEDIUM',
      probability: 0.78,
      status: 'primary',
      evidenceItems: [
        { id: 'd-ev-1', text: 'Heap profile shows 14,000 EventEmitter instances', isSupporting: true },
      ],
    },
    alternativeHypotheses: [],
    timeline: [
      {
        id: 'd-tl-1',
        investigationId: 'inv-demo-3001',
        timestamp: '15:10 UTC',
        title: 'Canary load test initiated',
        description: 'Automated synthetic traffic injection started.',
        category: 'action',
        severity: 'info',
      },
    ],
    evidenceChain: [],
    recommendations: [
      {
        id: 'd-rec-1',
        category: 'Immediate',
        action: 'Restart canary container pod.',
        reason: 'Flush leaked heap allocations.',
        expectedResult: 'Reset heap memory to 120MB.',
        risk: 'Low',
      },
    ],
    evidenceGaps: [],
    activityTrace: [
      { id: 'd-act-1', timestamp: '15:12:00', action: 'Captured V8 heap snapshot', status: 'done' },
    ],
    createdAt: '2026-08-14T15:12:00Z',
    updatedAt: '2026-08-14T15:15:00Z',
  },
};

export const demoKnowledge: KnowledgeDocument[] = [
  {
    id: 'kn-demo-1',
    projectId: 'demo-project',
    name: 'sandbox-testing-guide.md',
    category: 'Runbooks',
    chunks: 42,
    status: 'Indexed',
    lastUpdated: '3 days ago',
    summary: 'Guidelines for running chaos experiments in the sandbox.',
    tags: ['sandbox', 'chaos', 'testing'],
  },
];

export const demoEvidence: EvidenceItem[] = [
  {
    id: 'ev-demo-1',
    incidentId: 'inc-demo-3001',
    type: 'log',
    title: 'cart-demo-stdout.log',
    source: 'Canary Log Stream',
    fileSize: 1200000,
    status: 'ready',
    rawContent: '2026-08-14T15:10:12Z [WARN] cart-demo: High memory usage threshold exceeded (890MB)',
    uploadedAt: '15:11 UTC',
  },
];

export const demoLogs: LogEvent[] = [
  {
    id: 'log-demo-1',
    evidenceId: 'ev-demo-1',
    timestamp: '2026-08-14T15:10:12Z',
    level: 'WARN',
    service: 'cart-demo',
    message: 'High memory usage threshold exceeded (890MB)',
    attributes: { memoryMb: 890 },
  },
];
