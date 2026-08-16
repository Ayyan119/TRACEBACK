export type InvestigationStatus =
  | 'idle'
  | 'starting'
  | 'analyzing'
  | 'retrieving_evidence'
  | 'generating_hypotheses'
  | 'validating'
  | 'completed'
  | 'failed';

export type HypothesisStatus = 'primary' | 'alternative' | 'confirmed' | 'rejected' | 'inconclusive';

export interface ImpactDetails {
  affectedFunctionality: string;
  affectedServices: string[];
  estimatedImpact: string;
  startTime: string;
  currentDuration: string;
}

export interface MetricChange {
  id: string;
  name: string;
  baseline: string;
  current: string;
  percentChange: string;
  isNegative: boolean;
}

export interface Hypothesis {
  id: string;
  investigationId: string;
  title: string;
  description: string;
  confidenceLabel: 'HIGH' | 'MEDIUM' | 'LOW';
  probability: number;
  status: HypothesisStatus;
  evidenceItems: {
    id: string;
    text: string;
    isSupporting: boolean;
  }[];
}

export interface TimelineEvent {
  id: string;
  investigationId: string;
  timestamp: string;
  title: string;
  description: string;
  category?: 'deployment' | 'alert' | 'anomaly' | 'config_change' | 'action';
  severity?: 'info' | 'warning' | 'critical';
}

export interface EvidenceChainLink {
  id: string;
  stepNumber: number;
  title: string;
  description: string;
}

export interface ActionableRecommendation {
  id: string;
  category: 'Immediate' | 'Investigation' | 'Long-term';
  action: string;
  reason: string;
  expectedResult: string;
  risk: 'Low' | 'Medium' | 'High';
}

export interface EvidenceGapItem {
  id: string;
  gapDescription: string;
  recommendedNextEvidence: string;
  actionPrompt: string;
  impactLevel: 'High' | 'Medium' | 'Low';
}

export interface ActivityTrace {
  id: string;
  timestamp: string;
  action: string;
  status: 'done' | 'running' | 'pending';
}

export interface FollowUpQuestion {
  id: string;
  question: string;
  answer?: string;
  timestamp?: string;
}

export interface Investigation {
  id: string;
  incidentId: string;
  title: string;
  status: InvestigationStatus;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  confidence: number;
  confidenceSource?: 'llm' | 'fallback' | 'unavailable';
  analysisStatus?: 'success' | 'degraded' | 'failed';
  summary: string;
  currentStep?: string;
  progress?: number;
  impact: ImpactDetails;
  detectedChanges: MetricChange[];
  primaryHypothesis: Hypothesis;
  alternativeHypotheses: Hypothesis[];
  timeline: TimelineEvent[];
  evidenceChain: EvidenceChainLink[];
  recommendations: ActionableRecommendation[];
  evidenceGaps: EvidenceGapItem[];
  activityTrace: ActivityTrace[];
  createdAt: string;
  updatedAt: string;
}
