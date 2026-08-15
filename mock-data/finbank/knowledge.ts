import { KnowledgeDocument } from '@/types';

export const finbankKnowledge: KnowledgeDocument[] = [
  {
    id: 'kn-fin-1',
    projectId: 'finbank',
    name: 'ledger-service-runbook.md',
    category: 'Runbooks',
    chunks: 142,
    status: 'Indexed',
    lastUpdated: '1 day ago',
    summary: 'Operational procedures for end-of-day ledger reconciliation and lock purging.',
    tags: ['ledger', 'finbank', 'runbook', 'postgres'],
  },
  {
    id: 'kn-fin-2',
    projectId: 'finbank',
    name: 'transaction-processing.md',
    category: 'Architecture',
    chunks: 110,
    status: 'Indexed',
    lastUpdated: '4 days ago',
    summary: 'ISO 20022 message flow and interbank wire settlement architecture specs.',
    tags: ['swift', 'transactions', 'architecture'],
  },
  {
    id: 'kn-fin-3',
    projectId: 'finbank',
    name: 'banking-payment-reconciliation.md',
    category: 'Technical documents',
    chunks: 88,
    status: 'Indexed',
    lastUpdated: '1 week ago',
    summary: 'Double-entry bookkeeping validation rules and audit trail constraints.',
    tags: ['reconciliation', 'audit', 'bookkeeping'],
  },
];
