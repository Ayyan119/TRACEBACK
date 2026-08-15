export type EvidenceType = 'log' | 'screenshot' | 'metric' | 'stack_trace' | 'deployment' | 'document';
export type EvidenceUploadStatus = 'selected' | 'uploading' | 'uploaded' | 'processing' | 'ready' | 'failed';

export interface EvidenceItem {
  id: string;
  incidentId: string;
  type: EvidenceType;
  title: string;
  source: string;
  fileUrl?: string;
  fileSize?: number;
  mimeType?: string;
  status: EvidenceUploadStatus;
  rawContent?: string;
  metadata?: Record<string, unknown>;
  uploadedAt: string;
}

export interface CreateEvidenceInput {
  incidentId: string;
  type: EvidenceType;
  title: string;
  source: string;
  rawContent?: string;
  file?: File;
}
