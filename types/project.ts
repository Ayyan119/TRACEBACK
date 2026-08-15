import { CreateServiceInput } from './service';

export type EnvironmentTier = 'production' | 'staging' | 'development';

export interface Project {
  id: string;
  name: string;
  slug: string;
  description?: string;
  environment: EnvironmentTier;
  serviceCount: number;
  activeIncidentCount: number;
  ownerTeam?: string;
  repositoryUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProjectInput {
  name: string;
  slug?: string;
  description?: string;
  environment: EnvironmentTier;
  ownerTeam?: string;
  repositoryUrl?: string;
  initialServices?: CreateServiceInput[];
}

export interface ProjectExportReport {
  project: Project;
  services: any[];
  incidents: any[];
  knowledge: any[];
  investigations: any[];
  deployments: any[];
  logs: any[];
  exportedAt: string;
}
