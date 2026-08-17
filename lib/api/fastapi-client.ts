import { ApiClient } from './client';
import { getStoredUserProfile } from '@/lib/userProfile';
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

export class FastApiClient implements ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });

    if (!res.ok) {
      const errorPayload = await res.json().catch(() => ({ detail: res.statusText }));
      const message = typeof errorPayload.detail === 'string'
        ? errorPayload.detail
        : Array.isArray(errorPayload.detail)
          ? errorPayload.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
          : errorPayload.error?.message || `API error: ${res.status}`;
      throw new Error(message);
    }

    if (res.status === 204) {
      return {} as T;
    }

    return res.json();
  }

  // PROJECTS
  async getProjects(params?: { search?: string; environment?: string }): Promise<Project[]> {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.append('search', params.search);
    if (params?.environment) queryParams.append('environment', params.environment);
    const query = queryParams.toString();
    const endpoint = query ? `/projects?${query}` : '/projects';
    return this.request<Project[]>(endpoint);
  }

  async getProject(id: string): Promise<Project | null> {
    try {
      return await this.request<Project>(`/projects/${id}`);
    } catch (err: any) {
      if (err.message && (err.message.includes('404') || err.message.includes('not found'))) {
        return null;
      }
      throw err;
    }
  }

  async createProject(input: CreateProjectInput): Promise<Project> {
    const { initialServices, ...projectData } = input;
    const project = await this.request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });

    if (initialServices && initialServices.length > 0) {
      for (const serviceInput of initialServices) {
        if (serviceInput.name && serviceInput.name.trim()) {
          try {
            await this.request<Service>(`/projects/${project.id}/services`, {
              method: 'POST',
              body: JSON.stringify(serviceInput),
            });
          } catch (e) {
            console.error(`Failed to create initial service ${serviceInput.name}:`, e);
          }
        }
      }
      const updatedProject = await this.getProject(project.id);
      return updatedProject || project;
    }

    return project;
  }

  async updateProject(id: string, input: Partial<Project>): Promise<Project> {
    return this.request<Project>(`/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    });
  }

  async deleteProject(id: string): Promise<boolean> {
    await this.request<void>(`/projects/${id}`, {
      method: 'DELETE',
    });
    return true;
  }

  async exportProject(id: string): Promise<ProjectExportReport> {
    return this.request<ProjectExportReport>(`/projects/${id}/export`);
  }

  // SERVICES
  async getServices(params?: { projectId?: string }): Promise<Service[]> {
    if (params?.projectId) {
      return this.request<Service[]>(`/projects/${params.projectId}/services`);
    }
    return this.request<Service[]>('/projects/default/services').catch(() => []);
  }

  async getService(id: string, projectId?: string): Promise<Service | null> {
    try {
      return await this.request<Service>(`/services/${id}`);
    } catch (err: any) {
      if (err.message && (err.message.includes('404') || err.message.includes('not found'))) {
        return null;
      }
      throw err;
    }
  }

  async createService(input: CreateServiceInput): Promise<Service> {
    const { projectId, ...serviceData } = input;
    const targetProjectId = projectId || 'default';
    return this.request<Service>(`/projects/${targetProjectId}/services`, {
      method: 'POST',
      body: JSON.stringify(serviceData),
    });
  }

  async updateService(id: string, input: Partial<Service>, projectId?: string): Promise<Service> {
    return this.request<Service>(`/services/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    });
  }

  async deleteService(id: string, projectId?: string): Promise<boolean> {
    await this.request<void>(`/services/${id}`, {
      method: 'DELETE',
    });
    return true;
  }

  // DEPLOYMENTS
  async getDeployments(params?: { serviceId?: string; projectId?: string }): Promise<Deployment[]> {
    if (params?.serviceId) {
      return this.request<Deployment[]>(`/services/${params.serviceId}/deployments`);
    }
    if (params?.projectId) {
      return this.request<Deployment[]>(`/projects/${params.projectId}/deployments`);
    }
    return [];
  }

  async createDeployment(input: CreateDeploymentInput): Promise<Deployment> {
    const { serviceId, ...deploymentData } = input;
    if (!serviceId) {
      throw new Error('serviceId is required to create a deployment');
    }
    return this.request<Deployment>(`/services/${serviceId}/deployments`, {
      method: 'POST',
      body: JSON.stringify(deploymentData),
    });
  }

  // INCIDENTS
  async getIncidents(params?: {
    projectId?: string;
    serviceId?: string;
    severity?: string;
    status?: string;
  }): Promise<Incident[]> {
    const { projectId, ...otherParams } = params || {};
    const queryParams = new URLSearchParams();
    if (otherParams.serviceId) queryParams.append('serviceId', otherParams.serviceId);
    if (otherParams.severity) queryParams.append('severity', otherParams.severity);
    if (otherParams.status) queryParams.append('status', otherParams.status);
    const query = queryParams.toString();

    const targetProjectId = projectId || 'default';
    const endpoint = query ? `/projects/${targetProjectId}/incidents?${query}` : `/projects/${targetProjectId}/incidents`;
    return this.request<Incident[]>(endpoint).catch(() => []);
  }

  async getIncident(id: string, projectId?: string): Promise<Incident | null> {
    try {
      return await this.request<Incident>(`/incidents/${id}`);
    } catch (err: any) {
      if (err.message && (err.message.includes('404') || err.message.includes('not found'))) {
        return null;
      }
      throw err;
    }
  }

  async createIncident(input: CreateIncidentInput): Promise<Incident> {
    const { projectId, ...incidentData } = input;
    const targetProjectId = projectId || 'default';
    return this.request<Incident>(`/projects/${targetProjectId}/incidents`, {
      method: 'POST',
      body: JSON.stringify(incidentData),
    });
  }

  async updateIncident(id: string, input: Partial<Incident>, projectId?: string): Promise<Incident> {
    return this.request<Incident>(`/incidents/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    });
  }

  async deleteIncident(id: string, projectId?: string): Promise<boolean> {
    await this.request<void>(`/incidents/${id}`, {
      method: 'DELETE',
    });
    return true;
  }

  async getIncidentHistory(projectId: string): Promise<any[]> {
    return this.request<any[]>(`/projects/${projectId}/incident-history`).catch(() => []);
  }

  async reindexIncidentHistory(incidentId: string): Promise<any> {
    return this.request<any>(`/incidents/${incidentId}/history/reindex`, {
      method: 'POST',
    });
  }

  async queryProjectLogs(projectId: string, filters?: Record<string, any>): Promise<any[]> {
    const queryParams = new URLSearchParams(filters as Record<string, string> || {}).toString();
    const endpoint = queryParams ? `/projects/${projectId}/logs?${queryParams}` : `/projects/${projectId}/logs`;
    return this.request<any[]>(endpoint).catch(() => []);
  }

  // EVIDENCE
  async getEvidence(incidentId: string, projectId?: string): Promise<EvidenceItem[]> {
    return this.request<EvidenceItem[]>(`/incidents/${incidentId}/evidence`).catch(() => []);
  }

  async createEvidence(input: CreateEvidenceInput): Promise<EvidenceItem> {
    const { incidentId, ...evidenceData } = input;
    return this.request<EvidenceItem>(`/incidents/${incidentId}/evidence`, {
      method: 'POST',
      body: JSON.stringify(evidenceData),
    });
  }

  async uploadEvidence(incidentId: string, file: File, title?: string, type?: string, source?: string): Promise<EvidenceItem> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) formData.append('title', title);
    if (type) formData.append('type', type);
    if (source) formData.append('source', source);

    const res = await fetch(`${this.baseUrl}/incidents/${incidentId}/evidence/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(typeof err.detail === 'string' ? err.detail : 'Failed to upload evidence file');
    }

    return res.json();
  }

  async deleteEvidence(evidenceId: string, projectId?: string): Promise<boolean> {
    await this.request<void>(`/evidence/${evidenceId}`, {
      method: 'DELETE',
    });
    return true;
  }

  // INVESTIGATION
  private formatInvestigationFromIncident(incident: Incident): Investigation {
    let parsedResult: any = null;
    if (incident.rootCauseSummary) {
      try {
        parsedResult = JSON.parse(incident.rootCauseSummary);
      } catch {
        parsedResult = null;
      }
    }

    const confidence = typeof parsedResult?.confidence === 'number' ? parsedResult.confidence : (typeof incident.confidence === 'number' ? incident.confidence : 0.0);
    const primaryH = parsedResult?.selected_hypothesis || parsedResult?.hypotheses?.[0];
    const rootCauseTitle = parsedResult?.final_report?.root_cause || primaryH?.title || primaryH?.likely_root_cause || "Root cause cannot be conclusively determined from the supplied evidence.";
    
    const summaryText = parsedResult?.investigation_summary || 
      parsedResult?.final_report?.incident_summary || 
      `AI Root-Cause Investigation conducted for incident ${incident.code}. Primary Root Cause: ${rootCauseTitle}`;

    const supportingEvList = (primaryH?.supporting_evidence_ids && primaryH.supporting_evidence_ids.length > 0)
      ? primaryH.supporting_evidence_ids
      : (parsedResult?.final_report?.supporting_evidence || []);

    const primaryHypothesis = primaryH
      ? {
          id: primaryH.hypothesis_id || `hyp-${incident.id}-1`,
          investigationId: incident.id,
          title: rootCauseTitle,
          description: primaryH.description || primaryH.likely_root_cause || summaryText,
          confidenceLabel: (confidence >= 90 ? 'HIGH' : confidence >= 70 ? 'MEDIUM' : 'LOW') as 'HIGH' | 'MEDIUM' | 'LOW',
          probability: confidence,
          status: 'primary' as const,
          evidenceItems: supportingEvList.map((eid: string, idx: number) => ({
            id: `ev-${idx}`,
            text: typeof eid === 'string' && (eid.startsWith('Evidence ID') || eid.startsWith('Supporting')) ? eid : `Supporting Evidence: ${eid}`,
            isSupporting: true,
          })),
        }
      : {
          id: `hyp-${incident.id}-1`,
          investigationId: incident.id,
          title: "Root cause cannot be conclusively determined from the supplied evidence.",
          description: summaryText,
          confidenceLabel: 'LOW' as const,
          probability: confidence,
          status: 'confirmed' as const,
          evidenceItems: [],
        };

    const altHypotheses = (parsedResult?.hypotheses || [])
      .filter((h: any) => h.hypothesis_id !== primaryH?.hypothesis_id)
      .map((h: any, idx: number) => ({
        id: h.hypothesis_id || `hyp-alt-${idx}`,
        investigationId: incident.id,
        title: h.title || 'Alternative Hypothesis',
        description: h.description || h.likely_root_cause || 'Evaluated candidate root cause.',
        confidenceLabel: (h.confidence >= 80 ? 'MEDIUM' : 'LOW') as 'HIGH' | 'MEDIUM' | 'LOW',
        probability: h.confidence || 0,
        status: 'alternative' as const,
        evidenceItems: [],
      }));

    const activityTrace = (parsedResult?.execution_trace || []).map((t: any, idx: number) => ({
      id: `trace-${idx}`,
      timestamp: t.timestamp || incident.updatedAt || new Date().toISOString(),
      action: `Node [${t.node}] (${t.duration_ms}ms): ${t.details}`,
      status: 'done' as const,
    }));

    if (activityTrace.length === 0) {
      activityTrace.push({
        id: 'act-1',
        timestamp: incident.updatedAt || new Date().toISOString(),
        action: 'Autonomous AI Root-Cause Agent Completed Analysis',
        status: 'done',
      });
    }

    const evidenceGaps = (parsedResult?.rejected_evidence || []).map((r: any, idx: number) => ({
      id: `gap-${idx}`,
      gapDescription: `File '${r.source_name || r.file_name || r.source}' rejected`,
      recommendedNextEvidence: r.reason || 'Irrelevant to current production incident',
      actionPrompt: 'Provide error telemetry or system metrics graph',
      impactLevel: 'Low' as const,
    }));

    if (Array.isArray(parsedResult?.final_report?.investigation_limitations)) {
      parsedResult.final_report.investigation_limitations.forEach((lim: string, idx: number) => {
        evidenceGaps.push({
          id: `lim-${idx}`,
          gapDescription: `Investigation Limitation: ${lim}`,
          recommendedNextEvidence: 'Attach supplementary system telemetry or detailed stack traces',
          actionPrompt: 'Provide metrics graph or additional log exports',
          impactLevel: 'Medium' as const,
        });
      });
    }

    const recommendations: any[] = [];
    if (primaryH?.recommended_next_check) {
      recommendations.push({
        id: 'rec-primary-check',
        category: 'Immediate' as const,
        action: primaryH.recommended_next_check,
        reason: 'Targeted root cause verification',
        expectedResult: 'Confirm or refute suspected failure mechanism',
        risk: 'Low' as const,
      });
    }
    if (parsedResult?.final_report?.recommended_verification && parsedResult.final_report.recommended_verification !== primaryH?.recommended_next_check) {
      recommendations.push({
        id: 'rec-verification',
        category: 'Immediate' as const,
        action: parsedResult.final_report.recommended_verification,
        reason: 'Root cause fix validation',
        expectedResult: 'Verify system stabilization',
        risk: 'Low' as const,
      });
    }
    if (parsedResult?.final_report?.recommended_remediation) {
      recommendations.push({
        id: 'rec-remediation',
        category: 'Long-term' as const,
        action: parsedResult.final_report.recommended_remediation,
        reason: 'Permanent prevention of recurrence',
        expectedResult: 'Restore system resilience',
        risk: 'Low' as const,
      });
    }

    const rawServicesList: string[] = [
      ...(Array.isArray(parsedResult?.final_report?.affected_services) ? parsedResult.final_report.affected_services : []),
      ...(Array.isArray(primaryH?.affected_services) ? primaryH.affected_services : []),
      ...(Array.isArray(incident.affectedServices) ? incident.affectedServices : (incident.affectedService ? [incident.affectedService] : [])),
    ].filter(Boolean);

    const specificServices = rawServicesList.filter((s) => s !== 'Backend' && s !== 'Backend Services');
    const finalAffectedServices = Array.from(new Set(specificServices.length > 0 ? specificServices : rawServicesList));

    const finalAffectedFunctionality =
      parsedResult?.final_report?.affected_functionality ||
      (incident.title ? incident.title.replace(/^Title:\s*/i, '') : finalAffectedServices.join(', '));

    const runId = parsedResult?.investigation_run_id || parsedResult?.investigation_id || `inv-${incident.id}-${Date.now()}`;
    const invNumber = parsedResult?.investigation_number || 1;

    return {
      id: runId,
      incidentId: incident.id,
      runId: runId,
      investigationNumber: invNumber,
      title: incident.title ? incident.title.replace(/^(AI Root-Cause Analysis:\s*)+/i, '') : 'Incident Investigation',
      status: 'completed',
      severity: incident.severity,
      confidence: Math.round(confidence * 10) / 10,
      confidenceSource: parsedResult?.confidence_source,
      analysisStatus: parsedResult?.analysis_status,
      summary: summaryText,
      impact: {
        affectedFunctionality: finalAffectedFunctionality,
        affectedServices: finalAffectedServices.length > 0 ? finalAffectedServices : ['Primary Service'],
        estimatedImpact: `${incident.severity} Impact`,
        startTime: incident.detectedAt || incident.createdAt || new Date().toISOString(),
        currentDuration: incident.duration || 'Active',
      },
      detectedChanges: [],
      primaryHypothesis,
      alternativeHypotheses: altHypotheses,
      timeline: [],
      evidenceChain: [],
      recommendations,
      evidenceGaps,
      activityTrace,
      createdAt: incident.createdAt || new Date().toISOString(),
      updatedAt: incident.updatedAt || new Date().toISOString(),
    };
  }

  async getInvestigation(incidentId: string, projectId?: string): Promise<Investigation | null> {
    try {
      const incident = await this.getIncident(incidentId, projectId);
      if (!incident) return null;

      if (!incident.rootCauseSummary) {
        return await this.startInvestigation(incidentId, { projectId });
      }

      return this.formatInvestigationFromIncident(incident);
    } catch {
      return null;
    }
  }

  async startInvestigation(incidentId: string, options?: { forceRestart?: boolean; projectId?: string }): Promise<Investigation> {
    const profile = getStoredUserProfile();
    const updatedIncident = await this.request<Incident>(`/incidents/${incidentId}/investigate`, {
      method: 'POST',
      headers: {
        'X-User-Name': profile.name,
        'X-User-Role': profile.role,
      },
      body: JSON.stringify({
        force_restart: options?.forceRestart ?? true,
        user_name: profile.name,
        user_role: profile.role,
      }),
    });

    return this.formatInvestigationFromIncident(updatedIncident);
  }

  async resolveIncident(incidentId: string, projectId?: string): Promise<Incident> {
    return this.request<Incident>(`/incidents/${incidentId}/resolve`, {
      method: 'POST',
    });
  }

  async getInvestigationRuns(incidentId: string): Promise<any[]> {
    try {
      return await this.request<any[]>(`/incidents/${incidentId}/investigations`);
    } catch {
      return [];
    }
  }

  async getInvestigationRun(incidentId: string, runId: string): Promise<any | null> {
    try {
      return await this.request<any>(`/incidents/${incidentId}/investigations/${runId}`);
    } catch {
      return null;
    }
  }

  async askInvestigationChat(
    incidentId: string,
    question: string,
    messagesHistory: Array<{ role: string; content: string }>,
    projectId?: string
  ): Promise<{ reply: string }> {
    const pid = projectId || 'shopflow';
    return this.request<{ reply: string }>(`/projects/${pid}/incidents/${incidentId}/chat`, {
      method: 'POST',
      body: JSON.stringify({
        question,
        messages: messagesHistory,
      }),
    });
  }

  // LOGS
  async getLogs(incidentId: string, params?: { level?: string; search?: string; projectId?: string }): Promise<LogEvent[]> {
    try {
      const query = new URLSearchParams(params as Record<string, string>).toString();
      const data = await this.request<{ logs: LogEvent[] }>(`/incidents/${incidentId}/logs?${query}`);
      return data.logs || [];
    } catch {
      return [];
    }
  }

  async getLogStatistics(incidentId: string, projectId?: string): Promise<LogStatistics> {
    try {
      return await this.request<LogStatistics>(`/incidents/${incidentId}/logs/statistics`);
    } catch {
      return {
        totalLogs: 0,
        errorCount: 0,
        warnCount: 0,
        infoCount: 0,
        levelBreakdown: { DEBUG: 0, INFO: 0, WARN: 0, ERROR: 0, FATAL: 0 },
      };
    }
  }

  // KNOWLEDGE
  private formatKnowledgeDocument(doc: any): KnowledgeDocument {
    return {
      ...doc,
      name: doc.title || doc.name || 'Untitled Document',
      chunks: doc.chunks ?? doc.chunkCount ?? 0,
    };
  }

  async getKnowledge(params?: { query?: string; type?: string; category?: string; projectId?: string }): Promise<KnowledgeDocument[]> {
    const { projectId, ...otherParams } = params || {};
    const queryParams = new URLSearchParams();
    if (otherParams.query) queryParams.append('query', otherParams.query);
    if (otherParams.category || otherParams.type) queryParams.append('category', (otherParams.category || otherParams.type)!);
    const queryStr = queryParams.toString();

    const targetProjectId = projectId || 'default';
    const endpoint = queryStr ? `/projects/${targetProjectId}/knowledge?${queryStr}` : `/projects/${targetProjectId}/knowledge`;
    try {
      const docs = await this.request<KnowledgeDocument[]>(endpoint);
      return docs.map((d) => this.formatKnowledgeDocument(d));
    } catch {
      return [];
    }
  }

  async createKnowledge(doc: Partial<KnowledgeDocument> & { projectId?: string }): Promise<KnowledgeDocument> {
    const { projectId, name, ...docData } = doc;
    const title = docData.title || name || 'Untitled Document';
    const targetProjectId = projectId || 'default';

    const res = await this.request<KnowledgeDocument>(`/projects/${targetProjectId}/knowledge`, {
      method: 'POST',
      body: JSON.stringify({ ...docData, title }),
    });
    return this.formatKnowledgeDocument(res);
  }

  async uploadKnowledge(request: DocumentUploadRequest): Promise<KnowledgeDocument> {
    const formData = new FormData();
    formData.append('file', request.file);
    const title = request.title || request.file.name;
    formData.append('title', title);
    if (request.category) formData.append('category', request.category);

    const res = await fetch(`${this.baseUrl}/projects/${request.projectId}/knowledge/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(typeof err.detail === 'string' ? err.detail : 'Failed to upload knowledge document');
    }

    const data = await res.json();
    return this.formatKnowledgeDocument(data);
  }

  async retryKnowledgeIndexing(id: string, projectId?: string): Promise<KnowledgeDocument> {
    const doc = await this.request<KnowledgeDocument>(`/knowledge/${id}`);
    return this.formatKnowledgeDocument(doc);
  }

  async deleteKnowledge(id: string, projectId?: string): Promise<boolean> {
    await this.request<void>(`/knowledge/${id}`, {
      method: 'DELETE',
    });
    return true;
  }
}
