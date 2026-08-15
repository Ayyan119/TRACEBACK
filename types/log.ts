export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'FATAL';

export interface LogEvent {
  id: string;
  evidenceId: string;
  timestamp: string;
  level: LogLevel;
  service: string;
  message: string;
  stackTrace?: string;
  attributes?: Record<string, unknown>;
}

export interface LogStatistics {
  totalLogs: number;
  errorCount: number;
  warnCount: number;
  infoCount: number;
  levelBreakdown: Record<LogLevel, number>;
}
