import { ApiClient } from './client';
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
  LogLevel,
  LogStatistics,
  KnowledgeDocument,
  DocumentUploadRequest,
} from '@/types';

import { mockProjects } from '@/mock-data/projects';
import { shopflowServices } from '@/mock-data/shopflow/services';
import { shopflowIncidents } from '@/mock-data/shopflow/incidents';
import { shopflowInvestigations, shopflowKnowledge, shopflowEvidence, shopflowLogs } from '@/mock-data/shopflow/investigations';

import { finbankServices } from '@/mock-data/finbank/services';
import { finbankIncidents } from '@/mock-data/finbank/incidents';
import { finbankInvestigations } from '@/mock-data/finbank/investigations';
import { finbankKnowledge } from '@/mock-data/finbank/knowledge';
import { finbankEvidence, finbankLogs } from '@/mock-data/finbank/evidence';

import { demoServices } from '@/mock-data/demo-project/services';
import { demoIncidents } from '@/mock-data/demo-project/incidents';
import { demoInvestigations, demoKnowledge, demoEvidence, demoLogs } from '@/mock-data/demo-project/investigations';

const delay = (ms = 60) => new Promise((resolve) => setTimeout(resolve, ms));

export class MockApiClient implements ApiClient {
  private projects: Project[] = [...mockProjects];

  private customProjectData: Record<
    string,
    {
      services: Service[];
      incidents: Incident[];
      investigations: Record<string, Investigation>;
      knowledge: KnowledgeDocument[];
      evidence: EvidenceItem[];
      logs: LogEvent[];
    }
  > = {};

  // Helper method to retrieve project-specific collections
  private getProjectData(projectId?: string) {
    const pid = projectId?.toLowerCase() || 'shopflow';

    if (this.customProjectData[pid]) {
      return this.customProjectData[pid];
    }

    if (pid === 'finbank') {
      return {
        services: finbankServices,
        incidents: finbankIncidents,
        investigations: finbankInvestigations,
        knowledge: finbankKnowledge,
        evidence: finbankEvidence,
        logs: finbankLogs,
      };
    }
    if (pid === 'demo-project' || pid === 'demo') {
      return {
        services: demoServices,
        incidents: demoIncidents,
        investigations: demoInvestigations,
        knowledge: demoKnowledge,
        evidence: demoEvidence,
        logs: demoLogs,
      };
    }
    if (pid === 'shopflow') {
      return {
        services: shopflowServices,
        incidents: shopflowIncidents,
        investigations: shopflowInvestigations,
        knowledge: shopflowKnowledge,
        evidence: shopflowEvidence,
        logs: shopflowLogs,
      };
    }

    if (!this.customProjectData[pid]) {
      this.customProjectData[pid] = {
        services: [],
        incidents: [],
        investigations: {},
        knowledge: [],
        evidence: [],
        logs: [],
      };
    }
    return this.customProjectData[pid];
  }

  // PROJECTS
  async getProjects(params?: { search?: string; environment?: string }): Promise<Project[]> {
    await delay();
    let result = [...this.projects];
    if (params?.search) {
      const query = params.search.toLowerCase();
      result = result.filter(
        (p) => p.name.toLowerCase().includes(query) || p.description?.toLowerCase().includes(query)
      );
    }
    if (params?.environment) {
      result = result.filter((p) => p.environment === params.environment);
    }
    return result;
  }

  async getProject(id: string): Promise<Project | null> {
    await delay();
    const found = this.projects.find((p) => p.id === id || p.slug === id);
    return found || null;
  }

  async createProject(input: CreateProjectInput): Promise<Project> {
    await delay(120);
    const pid = input.slug || input.name.toLowerCase().replace(/[^a-z0-9]+/g, '-');

    const createdServices: Service[] = [];
    if (input.initialServices && input.initialServices.length > 0) {
      input.initialServices.forEach((s, idx) => {
        if (s.name && s.name.trim()) {
          createdServices.push({
            id: `srv-${pid}-${Date.now()}-${idx}`,
            projectId: pid,
            name: s.name.trim(),
            type: s.type || 'Backend',
            description: s.description,
            health: 'Healthy',
            latencyMs: 12 + Math.floor(Math.random() * 20),
            errorRatePercent: 0.0,
            recentIncidentsCount: 0,
            dependencies: [],
            recentDeployments: [],
            ownerTeam: s.ownerTeam,
            repositoryUrl: s.repositoryUrl,
            environment: s.environment || input.environment,
          });
        }
      });
    }

    const newProject: Project = {
      id: pid,
      name: input.name,
      slug: pid,
      description: input.description || `${input.name} workspace environment.`,
      environment: input.environment,
      serviceCount: createdServices.length,
      activeIncidentCount: 0,
      ownerTeam: input.ownerTeam,
      repositoryUrl: input.repositoryUrl,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    this.projects.push(newProject);
    this.customProjectData[pid] = {
      services: createdServices,
      incidents: [],
      investigations: {},
      knowledge: [],
      evidence: [],
      logs: [],
    };

    return newProject;
  }

  async updateProject(id: string, input: Partial<Project>): Promise<Project> {
    await delay();
    const index = this.projects.findIndex((p) => p.id === id || p.slug === id);
    if (index === -1) throw new Error(`Project ${id} not found`);

    this.projects[index] = {
      ...this.projects[index],
      ...input,
      updatedAt: new Date().toISOString(),
    };
    return this.projects[index];
  }

  async deleteProject(id: string): Promise<boolean> {
    await delay(150);
    const index = this.projects.findIndex((p) => p.id === id || p.slug === id);
    if (index !== -1) {
      const pid = this.projects[index].id;
      this.projects.splice(index, 1);
      delete this.customProjectData[pid];
      return true;
    }
    return false;
  }

  async exportProject(id: string): Promise<ProjectExportReport> {
    await delay(100);
    const project = await this.getProject(id);
    if (!project) throw new Error(`Project ${id} not found`);

    const data = this.getProjectData(project.id);
    const deployments: any[] = [];
    data.services.forEach((s) => {
      s.recentDeployments.forEach((d) => deployments.push({ ...d, service: s.name }));
    });

    return {
      project,
      services: data.services,
      incidents: data.incidents,
      knowledge: data.knowledge,
      investigations: Object.values(data.investigations),
      deployments,
      logs: data.logs,
      exportedAt: new Date().toISOString(),
    };
  }

  // SERVICES
  async getServices(params?: { projectId?: string }): Promise<Service[]> {
    await delay();
    const data = this.getProjectData(params?.projectId);
    return [...data.services];
  }

  async getService(id: string, projectId?: string): Promise<Service | null> {
    await delay();
    const data = this.getProjectData(projectId);
    return data.services.find((s) => s.id === id || s.name === id) || null;
  }

  async createService(input: CreateServiceInput): Promise<Service> {
    await delay(100);
    const pid = input.projectId || 'shopflow';
    const data = this.getProjectData(pid);
    const newService: Service = {
      id: `srv-${pid}-${Date.now()}`,
      projectId: pid,
      name: input.name,
      type: input.type || 'Backend',
      description: input.description,
      health: 'Healthy',
      latencyMs: 15,
      errorRatePercent: 0.0,
      recentIncidentsCount: 0,
      dependencies: [],
      recentDeployments: [],
      ownerTeam: input.ownerTeam,
      repositoryUrl: input.repositoryUrl,
      environment: input.environment || 'Production',
    };

    data.services.push(newService);

    // Update service count on project metadata
    const proj = this.projects.find((p) => p.id === pid);
    if (proj) proj.serviceCount += 1;

    return newService;
  }

  async updateService(id: string, input: Partial<Service>, projectId?: string): Promise<Service> {
    await delay(100);
    const data = this.getProjectData(projectId);
    const srv = data.services.find((s) => s.id === id || s.name === id);
    if (!srv) throw new Error(`Service ${id} not found`);

    Object.assign(srv, input);
    return srv;
  }

  async deleteService(id: string, projectId?: string): Promise<boolean> {
    await delay(100);
    const data = this.getProjectData(projectId);
    const index = data.services.findIndex((s) => s.id === id || s.name === id);
    if (index !== -1) {
      const pid = data.services[index].projectId;
      data.services.splice(index, 1);

      // Update service count on project metadata
      const proj = this.projects.find((p) => p.id === pid);
      if (proj && proj.serviceCount > 0) proj.serviceCount -= 1;

      return true;
    }
    return false;
  }

  // DEPLOYMENTS
  async getDeployments(params?: { serviceId?: string; projectId?: string }): Promise<Deployment[]> {
    await delay();
    const data = this.getProjectData(params?.projectId);
    const deployments: Deployment[] = [];
    data.services.forEach((s) => {
      if (!params?.serviceId || s.id === params.serviceId || s.name === params.serviceId) {
        s.recentDeployments.forEach((d) => {
          deployments.push({
            id: d.id,
            projectId: s.projectId,
            serviceId: s.id,
            version: d.version,
            author: d.author,
            status: 'Success',
            deployedAt: d.deployedAt,
            createdAt: d.deployedAt,
            updatedAt: d.deployedAt,
          });
        });
      }
    });
    return deployments;
  }

  async createDeployment(input: CreateDeploymentInput): Promise<Deployment> {
    await delay(100);
    const data = this.getProjectData(input.projectId);
    const srv = data.services.find((s) => s.id === input.serviceId || s.name === input.serviceId);
    const pid = input.projectId || srv?.projectId || 'shopflow';
    const sid = input.serviceId || srv?.id || 'srv-1';

    const newDep: Deployment = {
      id: `dep-${Date.now()}`,
      projectId: pid,
      serviceId: sid,
      version: input.version,
      commitHash: input.commitHash,
      author: input.author || 'CI/CD Pipeline',
      environment: input.environment || 'Production',
      status: input.status || 'Success',
      summary: input.summary,
      configChanges: input.configChanges,
      diffSummary: input.diffSummary,
      prUrl: input.prUrl,
      deployedAt: input.deployedAt || new Date().toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    if (srv) {
      srv.recentDeployments.unshift({
        id: newDep.id,
        version: newDep.version,
        deployedAt: newDep.deployedAt,
        author: newDep.author,
      });
    }

    return newDep;
  }

  // INCIDENTS
  async getIncidents(params?: {
    projectId?: string;
    serviceId?: string;
    severity?: string;
    status?: string;
  }): Promise<Incident[]> {
    await delay();
    const data = this.getProjectData(params?.projectId);
    let result = [...data.incidents];

    if (params?.serviceId) {
      const targetService = params.serviceId;
      result = result.filter(
        (i) => i.affectedService === targetService || i.affectedServices?.includes(targetService)
      );
    }
    if (params?.severity) {
      result = result.filter((i) => i.severity.toLowerCase() === params.severity?.toLowerCase());
    }
    if (params?.status) {
      result = result.filter((i) => i.status.toLowerCase() === params.status?.toLowerCase());
    }
    return result;
  }

  async getIncident(id: string, projectId?: string): Promise<Incident | null> {
    await delay();
    if (projectId) {
      const data = this.getProjectData(projectId);
      const inc = data.incidents.find((i) => i.id === id || i.code.toLowerCase() === id.toLowerCase());
      if (inc) return inc;
    }
    for (const p of this.projects) {
      const data = this.getProjectData(p.id);
      const inc = data.incidents.find((i) => i.id === id || i.code.toLowerCase() === id.toLowerCase());
      if (inc) return inc;
    }
    return null;
  }

  async createIncident(input: CreateIncidentInput): Promise<Incident> {
    await delay(120);
    const pid = input.projectId || 'shopflow';
    const data = this.getProjectData(pid);
    const newId = `inc-${pid}-${Date.now()}`;
    const newIncident: Incident = {
      id: newId,
      code: `INC-${Math.floor(1000 + Math.random() * 9000)}`,
      projectId: pid,
      title: input.title || 'Reported Incident',
      description: input.description,
      severity: input.severity || 'High',
      status: 'Investigating',
      affectedService: input.affectedService || (data.services[0]?.name || 'system-core'),
      affectedServices: [input.affectedService || (data.services[0]?.name || 'system-core')],
      detectedAt: 'Just now',
      duration: '0m',
      confidence: 85,
      updatedAt: 'Just now',
      reporter: 'User Input',
      environment: input.environment || 'Production',
    };

    data.incidents.unshift(newIncident);

    const proj = this.projects.find((p) => p.id === pid);
    if (proj) proj.activeIncidentCount += 1;

    return newIncident;
  }

  async updateIncident(id: string, input: Partial<Incident>, projectId?: string): Promise<Incident> {
    await delay(100);
    const inc = await this.getIncident(id, projectId);
    if (!inc) throw new Error(`Incident ${id} not found`);

    Object.assign(inc, input);
    if (input.status === 'Resolved' && !inc.resolvedAt) {
      inc.resolvedAt = new Date().toISOString();
    }
    return inc;
  }

  async deleteIncident(id: string, projectId?: string): Promise<boolean> {
    await delay(100);
    const data = this.getProjectData(projectId);
    const index = data.incidents.findIndex((i) => i.id === id || i.code.toLowerCase() === id.toLowerCase());
    if (index !== -1) {
      const inc = data.incidents[index];
      const pid = inc.projectId;
      data.incidents.splice(index, 1);
      delete data.investigations[inc.id];

      const proj = this.projects.find((p) => p.id === pid);
      if (proj && inc.status !== 'Resolved' && proj.activeIncidentCount > 0) {
        proj.activeIncidentCount -= 1;
      }
      return true;
    }
    return false;
  }

  // EVIDENCE
  async getEvidence(incidentId: string, projectId?: string): Promise<EvidenceItem[]> {
    await delay();
    const data = this.getProjectData(projectId);
    return data.evidence.filter((e) => e.incidentId === incidentId || !e.incidentId);
  }

  async createEvidence(input: CreateEvidenceInput): Promise<EvidenceItem> {
    await delay(100);
    const newEvidence: EvidenceItem = {
      id: `ev-${Date.now()}`,
      incidentId: input.incidentId,
      type: input.type,
      title: input.title,
      source: input.source || 'Manual Upload',
      fileSize: input.rawContent?.length || 1024,
      status: 'ready',
      rawContent: input.rawContent,
      uploadedAt: 'Just now',
    };
    return newEvidence;
  }

  async uploadEvidence(incidentId: string, file: File, title?: string, type?: string, source?: string): Promise<EvidenceItem> {
    await delay(150);
    return {
      id: `ev-${Date.now()}`,
      incidentId,
      type: (type as any) || 'log',
      title: title || file.name,
      source: source || 'User Upload',
      fileSize: file.size,
      mimeType: file.type || 'text/plain',
      status: 'ready',
      fileUrl: `/static/uploads/${file.name}`,
      uploadedAt: new Date().toISOString(),
    };
  }

  async deleteEvidence(evidenceId: string, projectId?: string): Promise<boolean> {
    await delay(100);
    return true;
  }

  // INVESTIGATION
  async getInvestigation(incidentId: string, projectId?: string): Promise<Investigation | null> {
    await delay();
    const data = this.getProjectData(projectId);
    return data.investigations[incidentId] || Object.values(data.investigations)[0] || null;
  }

  async startInvestigation(incidentId: string, options?: { forceRestart?: boolean; projectId?: string }): Promise<Investigation> {
    await delay(250);
    const inv = await this.getInvestigation(incidentId, options?.projectId);
    if (!inv) {
      throw new Error(`Investigation for incident ${incidentId} not found`);
    }
    return { ...inv, status: 'analyzing', confidence: 91 };
  }

  // LOGS
  async getLogs(incidentId: string, params?: { level?: string; search?: string; projectId?: string }): Promise<LogEvent[]> {
    await delay();
    const data = this.getProjectData(params?.projectId);
    let result = [...data.logs];

    if (params?.level && params.level !== 'ALL') {
      result = result.filter((l) => l.level === params.level);
    }
    if (params?.search) {
      const q = params.search.toLowerCase();
      result = result.filter((l) => l.message.toLowerCase().includes(q) || l.service.toLowerCase().includes(q));
    }
    return result;
  }

  async getLogStatistics(incidentId: string, projectId?: string): Promise<LogStatistics> {
    await delay();
    const logs = await this.getLogs(incidentId, { projectId });
    const levelBreakdown: Record<LogLevel, number> = {
      DEBUG: 0,
      INFO: 0,
      WARN: 0,
      ERROR: 0,
      FATAL: 0,
    };

    logs.forEach((l) => {
      levelBreakdown[l.level] = (levelBreakdown[l.level] || 0) + 1;
    });

    return {
      totalLogs: logs.length,
      errorCount: levelBreakdown.ERROR + levelBreakdown.FATAL,
      warnCount: levelBreakdown.WARN,
      infoCount: levelBreakdown.INFO,
      levelBreakdown,
    };
  }

  // KNOWLEDGE
  async getKnowledge(params?: { query?: string; type?: string; projectId?: string }): Promise<KnowledgeDocument[]> {
    await delay();
    const data = this.getProjectData(params?.projectId);
    let result = [...data.knowledge];

    if (params?.type && params.type !== 'ALL') {
      result = result.filter((k) => k.category.toLowerCase() === params.type?.toLowerCase());
    }
    if (params?.query) {
      const q = params.query.toLowerCase();
      result = result.filter(
        (k) => k.name.toLowerCase().includes(q) || k.summary?.toLowerCase().includes(q)
      );
    }
    return result;
  }

  async createKnowledge(doc: Partial<KnowledgeDocument>): Promise<KnowledgeDocument> {
    await delay(120);
    const pid = doc.projectId || 'shopflow';
    const data = this.getProjectData(pid);
    const newDoc: KnowledgeDocument = {
      id: `kn-${Date.now()}`,
      projectId: pid,
      name: doc.name || 'new-document.md',
      category: (doc.category as any) || 'Runbook',
      chunks: doc.chunks || 45,
      status: 'INDEXED',
      uploadedAt: 'Just now',
      summary: doc.summary || 'User uploaded documentation',
      uploadedBy: 'Alex Chen',
    };
    data.knowledge.unshift(newDoc);
    return newDoc;
  }

  async uploadKnowledge(request: DocumentUploadRequest): Promise<KnowledgeDocument> {
    await delay(100);
    const pid = request.projectId || 'shopflow';
    const data = this.getProjectData(pid);

    const ext = request.file.name.split('.').pop()?.toUpperCase() || 'TXT';
    const size = request.file.size;
    const formattedSize =
      size < 1024
        ? `${size} B`
        : size < 1024 * 1024
        ? `${(size / 1024).toFixed(1)} KB`
        : `${(size / (1024 * 1024)).toFixed(1)} MB`;

    const newDoc: KnowledgeDocument = {
      id: `kn-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      projectId: pid,
      name: request.file.name,
      category: request.category || 'Runbook',
      fileSize: formattedSize,
      fileType: ext,
      chunks: Math.floor(Math.random() * 120) + 16,
      status: 'INDEXED',
      uploadedAt: 'Just now',
      summary: request.summary || `Technical documentation file: ${request.file.name}`,
      uploadedBy: 'Alex Chen',
    };

    data.knowledge.unshift(newDoc);
    return newDoc;
  }

  async retryKnowledgeIndexing(id: string, projectId?: string): Promise<KnowledgeDocument> {
    await delay(150);
    const data = this.getProjectData(projectId);
    const doc = data.knowledge.find((k) => k.id === id);
    if (!doc) throw new Error(`Document ${id} not found`);

    doc.status = 'INDEXED';
    doc.errorMessage = undefined;
    return doc;
  }

  async deleteKnowledge(id: string, projectId?: string): Promise<boolean> {
    await delay(100);
    const data = this.getProjectData(projectId);
    const index = data.knowledge.findIndex((k) => k.id === id || k.name === id);
    if (index !== -1) {
      data.knowledge.splice(index, 1);
      return true;
    }
    return false;
  }
}
