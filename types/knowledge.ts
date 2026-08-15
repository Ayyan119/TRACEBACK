export type KnowledgeCategory =
  | 'Technical Documentation'
  | 'Runbook'
  | 'Runbooks'
  | 'Architecture'
  | 'Previous Incident'
  | 'Previous incidents'
  | 'Post-Mortem'
  | 'Troubleshooting Guide'
  | 'Troubleshooting guides'
  | 'Technical documents'
  | 'API Documentation'
  | 'Database Documentation'
  | 'Deployment Documentation'
  | 'Other';

export type KnowledgeDocumentStatus =
  | 'UPLOADING'
  | 'PROCESSING'
  | 'INDEXING'
  | 'INDEXED'
  | 'FAILED'
  | 'Indexed'
  | 'Failed'
  | 'ready';

export interface KnowledgeDocument {
  id: string;
  projectId: string;
  name: string;
  title?: string;
  category: KnowledgeCategory | string;
  content?: string;
  fileUrl?: string;
  fileSize?: number | string;
  mimeType?: string;
  fileType?: string;
  chunkCount?: number;
  chunks?: number;
  status: KnowledgeDocumentStatus;
  createdAt?: string;
  updatedAt?: string;
  uploadedAt?: string;
  lastUpdated?: string;
  summary?: string;
  uploadedBy?: string;
  errorMessage?: string;
  tags?: string[];
}

export interface DocumentUploadRequest {
  projectId: string;
  file: File;
  title?: string;
  category?: KnowledgeCategory | string;
  summary?: string;
}
