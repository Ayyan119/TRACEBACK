export type IncidentSeverity = 'Critical' | 'High' | 'Medium' | 'Low';
export type IncidentStatus = 'Investigating' | 'Identified' | 'Monitoring' | 'Resolved';

export interface Incident {
  id: string;
  projectId: string;
  code: string; // e.g. INC-1001
  title: string;
  description: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  affectedService: string;
  affectedServices?: string[];
  detectedAt: string;
  duration: string;
  confidence: number;
  rootCauseSummary?: string;
  resolvedAt?: string;
  createdAt?: string;
  updatedAt: string;
  reporter?: string;
  environment?: string;
}

export interface CreateIncidentInput {
  projectId: string;
  title: string;
  description: string;
  severity?: IncidentSeverity;
  affectedService?: string;
  affectedServices?: string[];
  detectedAt?: string;
  environment?: string;
  userHypothesis?: string;
}
