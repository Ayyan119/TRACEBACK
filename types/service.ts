export type ServiceHealth = 'Healthy' | 'Degraded' | 'Critical' | 'Unknown';

export type ServiceType =
  | 'API'
  | 'Frontend'
  | 'Backend'
  | 'Worker'
  | 'Database'
  | 'Cache'
  | 'Queue'
  | 'Other';

export interface ServiceDependency {
  id: string;
  name: string;
  type: 'internal' | 'external' | 'database' | 'cache';
}

export interface Service {
  id: string;
  projectId: string;
  name: string;
  health: ServiceHealth;
  type?: ServiceType;
  description?: string;
  latencyMs: number;
  errorRatePercent: number;
  recentIncidentsCount: number;
  dependencies: ServiceDependency[];
  recentDeployments: {
    id: string;
    version: string;
    deployedAt: string;
    author: string;
  }[];
  ownerTeam?: string;
  repositoryUrl?: string;
  environment?: string;
}

export interface CreateServiceInput {
  projectId?: string;
  name: string;
  type?: ServiceType;
  description?: string;
  ownerTeam?: string;
  repositoryUrl?: string;
  environment?: string;
}
