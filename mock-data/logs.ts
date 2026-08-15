import { LogEvent, LogStatistics } from '@/types';

export const mockLogs: LogEvent[] = [
  {
    id: 'log-1',
    evidenceId: 'ev-1',
    timestamp: '2026-08-14T14:03:12Z',
    level: 'ERROR',
    service: 'order-service',
    message: 'HTTP POST https://payment.internal/v1/charge timed out after 3000ms. Retrying (1/5)...',
    stackTrace: `goroutine 481 [running]:
github.com/shopflow/order-service/pkg/payment.(*Client).Charge(0xc000492100)
    /app/pkg/payment/client.go:84 +0x1b2`,
    attributes: { traceId: 'tr_8912401', clientIp: '10.244.3.18', durationMs: 3002 },
  },
  {
    id: 'log-2',
    evidenceId: 'ev-1',
    timestamp: '2026-08-14T14:03:15Z',
    level: 'WARN',
    service: 'order-service',
    message: 'HTTP POST https://payment.internal/v1/charge timed out after 3000ms. Retrying (2/5)...',
    attributes: { traceId: 'tr_8912401', attempt: 2 },
  },
  {
    id: 'log-3',
    evidenceId: 'ev-1',
    timestamp: '2026-08-14T14:03:18Z',
    level: 'FATAL',
    service: 'order-service',
    message: 'Payment request failed: 504 Gateway Timeout. Transaction rollback initiated for order #ord_9941.',
    stackTrace: `goroutine 481 [running]:
github.com/shopflow/order-service/internal/orders.CreateOrder(...)
    /app/internal/orders/service.go:142 +0x24a`,
    attributes: { traceId: 'tr_8912401', orderId: 'ord_9941', status: 504 },
  },
  {
    id: 'log-4',
    evidenceId: 'ev-1',
    timestamp: '2026-08-14T14:03:20Z',
    level: 'WARN',
    service: 'payment-service',
    message: 'Inbound pool connection queue size 88/100 reached.',
    attributes: { activeConns: 88, maxConns: 100 },
  },
  {
    id: 'log-5',
    evidenceId: 'ev-1',
    timestamp: '2026-08-14T14:03:25Z',
    level: 'INFO',
    service: 'order-service',
    message: 'Health check probe ping executed successfully in 1.2ms.',
    attributes: { probe: 'liveness' },
  },
];

export const mockLogStatistics: LogStatistics = {
  totalLogs: 1420,
  errorCount: 382,
  warnCount: 110,
  infoCount: 928,
  levelBreakdown: {
    FATAL: 42,
    ERROR: 340,
    WARN: 110,
    INFO: 928,
    DEBUG: 0,
  },
};
