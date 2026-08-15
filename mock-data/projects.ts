import { Project } from '@/types';

export const mockProjects: Project[] = [
  {
    id: 'shopflow',
    name: 'ShopFlow',
    slug: 'shopflow',
    description: 'Main e-commerce checkout pipeline, order management, and payment processor integrations.',
    environment: 'production',
    serviceCount: 6,
    activeIncidentCount: 1,
    createdAt: '2026-01-15T08:00:00Z',
    updatedAt: '2026-08-14T07:30:00Z',
  },
  {
    id: 'finbank',
    name: 'FinBank',
    slug: 'finbank',
    description: 'Core financial ledger, SWIFT wire settlement, and treasury accounting microservices.',
    environment: 'production',
    serviceCount: 6,
    activeIncidentCount: 1,
    createdAt: '2026-02-01T10:00:00Z',
    updatedAt: '2026-08-14T06:45:00Z',
  },
  {
    id: 'demo-project',
    name: 'Demo Project',
    slug: 'demo-project',
    description: 'Sandbox testing ground for automated chaos testing and canary deployments.',
    environment: 'staging',
    serviceCount: 3,
    activeIncidentCount: 1,
    createdAt: '2026-03-10T14:20:00Z',
    updatedAt: '2026-08-13T18:00:00Z',
  },
];
