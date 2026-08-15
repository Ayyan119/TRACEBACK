export type DeploymentStatus = 'Success' | 'Failed' | 'Rolled_Back' | 'In_Progress';

export interface Deployment {
  id: string;
  projectId: string;
  serviceId: string;
  version: string;
  commitHash?: string;
  author: string;
  environment?: string;
  status: DeploymentStatus;
  summary?: string;
  configChanges?: any;
  diffSummary?: string;
  prUrl?: string;
  deployedAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateDeploymentInput {
  projectId?: string;
  serviceId?: string;
  version: string;
  commitHash?: string;
  author?: string;
  environment?: string;
  status?: DeploymentStatus;
  summary?: string;
  configChanges?: any;
  diffSummary?: string;
  prUrl?: string;
  deployedAt?: string;
}
