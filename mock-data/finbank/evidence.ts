import { EvidenceItem, LogEvent } from '@/types';

export const finbankEvidence: EvidenceItem[] = [
  {
    id: 'ev-fin-1',
    incidentId: 'inc-finbank-2001',
    type: 'log',
    title: 'ledger-service-stdout.log',
    source: 'FinBank CloudWatch Stream',
    fileSize: 32400100,
    status: 'ready',
    rawContent: `2026-08-14T12:20:10Z [ERROR] ledger-service: Lock acquisition timeout (840ms) on table ledger_entries for tenant_id=tn_8912.
2026-08-14T12:20:14Z [WARN] ledger-service: Batch worker #4 retrying transaction reconciliation query...`,
    uploadedAt: '12:22 UTC',
  },
  {
    id: 'ev-fin-2',
    incidentId: 'inc-finbank-2001',
    type: 'deployment',
    title: '0042_ledger_idx.sql migration diff',
    source: 'GitHub Actions Migration',
    fileSize: 4200,
    status: 'ready',
    rawContent: `-- DROP INDEX idx_ledger_tenant_created;`,
    uploadedAt: '12:15 UTC',
  },
];

export const finbankLogs: LogEvent[] = [
  {
    id: 'log-fin-1',
    evidenceId: 'ev-fin-1',
    timestamp: '2026-08-14T12:20:10Z',
    level: 'ERROR',
    service: 'ledger-service',
    message: 'Lock acquisition timeout (840ms) on table ledger_entries for tenant_id=tn_8912.',
    stackTrace: `goroutine 921 [running]:
github.com/finbank/ledger-service/pkg/db.AcquireBatchLock(...)
    /app/pkg/db/reconcile.go:88 +0x21a`,
    attributes: { tenantId: 'tn_8912', waitTimeMs: 840 },
  },
  {
    id: 'log-fin-2',
    evidenceId: 'ev-fin-1',
    timestamp: '2026-08-14T12:20:14Z',
    level: 'WARN',
    service: 'ledger-service',
    message: 'Batch worker #4 retrying transaction reconciliation query...',
    attributes: { workerId: 4 },
  },
];
