import {
  Project,
  CreateProjectInput,
  ProjectExportReport,
  Service,
  CreateServiceInput,
  Deployment,
  CreateDeploymentInput,
  Incident,
  CreateIncidentInput,
  EvidenceItem,
  CreateEvidenceInput,
  Investigation,
  LogEvent,
  LogStatistics,
  KnowledgeDocument,
  DocumentUploadRequest,
} from '@/types';

export interface ApiClient {
  // Projects
  getProjects(params?: { search?: string; environment?: string }): Promise<Project[]>;
  getProject(id: string): Promise<Project | null>;
  createProject(input: CreateProjectInput): Promise<Project>;
  updateProject(id: string, input: Partial<Project>): Promise<Project>;
  deleteProject(id: string): Promise<boolean>;
  exportProject(id: string): Promise<ProjectExportReport>;

  // Services
  getServices(params?: { projectId?: string }): Promise<Service[]>;
  getService(id: string, projectId?: string): Promise<Service | null>;
  createService(input: CreateServiceInput): Promise<Service>;
  updateService(id: string, input: Partial<Service>, projectId?: string): Promise<Service>;
  deleteService(id: string, projectId?: string): Promise<boolean>;

  // Deployments
  getDeployments(params?: { serviceId?: string; projectId?: string }): Promise<Deployment[]>;
  createDeployment(input: CreateDeploymentInput): Promise<Deployment>;

  // Incidents
  getIncidents(params?: {
    projectId?: string;
    serviceId?: string;
    severity?: string;
    status?: string;
  }): Promise<Incident[]>;
  getIncident(id: string, projectId?: string): Promise<Incident | null>;
  createIncident(input: CreateIncidentInput): Promise<Incident>;
  updateIncident(id: string, input: Partial<Incident>, projectId?: string): Promise<Incident>;
  deleteIncident(id: string, projectId?: string): Promise<boolean>;

  // Evidence
  getEvidence(incidentId: string, projectId?: string): Promise<EvidenceItem[]>;
  createEvidence(input: CreateEvidenceInput): Promise<EvidenceItem>;
  uploadEvidence(incidentId: string, file: File, title?: string, type?: string, source?: string): Promise<EvidenceItem>;
  deleteEvidence(evidenceId: string, projectId?: string): Promise<boolean>;

  // Investigation
  getInvestigation(incidentId: string, projectId?: string): Promise<Investigation | null>;
  startInvestigation(incidentId: string, options?: { forceRestart?: boolean; projectId?: string }): Promise<Investigation>;
  resolveIncident(incidentId: string, projectId?: string): Promise<Incident>;
  askInvestigationChat(
    incidentId: string,
    question: string,
    messagesHistory: Array<{ role: string; content: string }>,
    projectId?: string
  ): Promise<{ reply: string }>;

  // Logs
  getLogs(incidentId: string, params?: { level?: string; search?: string; projectId?: string }): Promise<LogEvent[]>;
  getLogStatistics(incidentId: string, projectId?: string): Promise<LogStatistics>;

  // Knowledge
  getKnowledge(params?: { query?: string; type?: string; projectId?: string }): Promise<KnowledgeDocument[]>;
  createKnowledge(doc: Partial<KnowledgeDocument>): Promise<KnowledgeDocument>;
  uploadKnowledge(request: DocumentUploadRequest): Promise<KnowledgeDocument>;
  retryKnowledgeIndexing(id: string, projectId?: string): Promise<KnowledgeDocument>;
  deleteKnowledge(id: string, projectId?: string): Promise<boolean>;

  // User Profile
  getUserMe(): Promise<any>;
  saveUserProfile(name: string, role: string, openaiApiKey?: string): Promise<any>;
  getAllUsers(): Promise<any[]>;
}
