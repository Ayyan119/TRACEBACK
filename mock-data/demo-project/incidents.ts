import { Incident } from '@/types';

export const demoIncidents: Incident[] = [
  {
    id: 'inc-demo-3001',
    code: 'DEMO-3001',
    projectId: 'demo-project',
    title: 'Canary test deployment memory leak',
    description: 'Transient heap memory allocation growth during canary load testing on cart-demo instance.',
    severity: 'Low',
    status: 'Monitoring',
    affectedService: 'cart-demo',
    affectedServices: ['cart-demo'],
    detectedAt: '15:10 UTC',
    duration: '1h 05m',
    confidence: 78,
    updatedAt: '10m ago',
    reporter: 'Chaos Bot',
    environment: 'Staging',
  },
];
