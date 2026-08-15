'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Card, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { EvidenceDropzone } from '@/components/evidence/EvidenceDropzone';
import { FileList } from '@/components/evidence/FileList';
import { ArrowLeft, Sparkles, UploadCloud, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Project, EvidenceItem } from '@/types';

export default function ProjectNewIncidentPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = (params?.projectId as string) || '';

  const [project, setProject] = useState<Project | null>(null);
  const [description, setDescription] = useState(
    'Orders are completing, but application checkout latency is approximately 10x slower than normal.'
  );

  // Separate file staging state
  const [stagedLogFile, setStagedLogFile] = useState<File | null>(null);
  const [stagedEvidenceFiles, setStagedEvidenceFiles] = useState<File[]>([]);
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([]);

  // Optional Context fields
  const [showOptionalContext, setShowOptionalContext] = useState(false);
  const [affectedService, setAffectedService] = useState('');
  const [environment, setEnvironment] = useState('Production');
  const [deploymentChange, setDeploymentChange] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [modalError, setModalError] = useState<string | null>(null);

  useEffect(() => {
    api.getProject(projectId).then(setProject).catch(() => null);
  }, [projectId]);

  const projectName = project ? project.name : projectId;
  const countWords = (text: string) => {
    if (!text || !text.trim()) return 0;
    return text.trim().split(/\s+/).filter(Boolean).length;
  };

  const descriptionWordCount = countWords(description);

  // 1. Mandatory Log File Upload Handler
  const handleLogFileUpload = async (files: File[]) => {
    if (!files || files.length === 0) return;
    setValidationError(null);
    const logFile = files[0];
    setStagedLogFile(logFile);
  };

  // 2. Optional Evidence Attachments Upload Handler (Max 10 files)
  const handleEvidenceFileUpload = async (files: File[]) => {
    setValidationError(null);

    if (stagedEvidenceFiles.length + files.length > 10) {
      setValidationError(
        'Maximum 10 evidence files allowed. The incident log is separate and does not count toward this limit.'
      );
      return;
    }

    setStagedEvidenceFiles((prev) => [...prev, ...files]);
    for (const f of files) {
      let type: EvidenceItem['type'] = 'log';
      if (f.name.endsWith('.png') || f.name.endsWith('.jpg') || f.name.endsWith('.jpeg') || f.name.endsWith('.webp')) {
        type = 'screenshot';
      } else if (f.name.endsWith('.pdf') || f.name.endsWith('.docx') || f.name.endsWith('.pptx')) {
        type = 'document';
      }
      setEvidenceItems((prev) => [
        {
          id: `staged-${Date.now()}-${f.name}`,
          incidentId: 'draft',
          type,
          title: f.name,
          source: 'User Upload',
          fileSize: f.size,
          status: 'ready',
          uploadedAt: 'Staged for upload',
        },
        ...prev,
      ]);
    }
  };

  // Pre-modal Validation before opening popup
  const handleOpenConfirmModal = () => {
    setValidationError(null);

    if (descriptionWordCount === 0) {
      setValidationError('Incident description is required.');
      return;
    }

    if (descriptionWordCount > 2000) {
      setValidationError('Incident description cannot exceed 2,000 words.');
      return;
    }

    if (!stagedLogFile) {
      setValidationError('A log file is required to report an incident. Please attach a log file in the Incident Log area below.');
      return;
    }

    if (stagedEvidenceFiles.length > 10) {
      setValidationError(
        'Maximum 10 evidence files allowed. The incident log is separate and does not count toward this limit.'
      );
      return;
    }

    setModalError(null);
    setShowConfirmModal(true);
  };

  // Create Incident API Call
  const handleCreateIncident = async () => {
    setIsSubmitting(true);
    setModalError(null);

    try {
      const newInc = await api.createIncident({
        title: description.slice(0, 60) + (description.length > 60 ? '...' : ''),
        description,
        projectId,
        affectedService: affectedService || undefined,
        environment,
      });

      // Upload compulsory Log File
      if (stagedLogFile) {
        try {
          await api.uploadEvidence(newInc.id, stagedLogFile, `Mandatory Log: ${stagedLogFile.name}`, 'log', 'Incident Creation');
        } catch (err: any) {
          console.error('Failed to upload mandatory log file:', err);
        }
      }

      // Upload optional Evidence Files
      for (const f of stagedEvidenceFiles) {
        let type = 'document';
        if (f.name.endsWith('.png') || f.name.endsWith('.jpg') || f.name.endsWith('.jpeg') || f.name.endsWith('.webp')) {
          type = 'screenshot';
        }
        try {
          await api.uploadEvidence(newInc.id, f, f.name, type, 'User Upload');
        } catch (err: any) {
          console.error('Failed to upload evidence file:', err);
        }
      }

      setShowConfirmModal(false);
      setStagedLogFile(null);
      setStagedEvidenceFiles([]);
      setEvidenceItems([]);
      router.push(`/projects/${projectId}/incidents/${newInc.id}`);
    } catch (err: any) {
      setModalError(err.message || 'Failed to create incident report.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto text-xs pb-12">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-borderColor pb-3">
        <Link
          href={`/projects/${projectId}/incidents`}
          className="inline-flex items-center gap-1.5 text-textSecondary hover:text-textPrimary transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to {projectName} Incidents</span>
        </Link>
        <Badge variant="outline" className="font-mono">
          Workspace: {projectName}
        </Badge>
      </div>

      <div className="border-b border-borderColor pb-3">
        <h1 className="text-lg font-bold text-textPrimary">Report Production Incident & Ingest Evidence</h1>
        <p className="text-xs text-textSecondary mt-0.5">
          Ingest raw telemetry, symptoms, and required logs. Traceback AI engine will correlate anomalies and identify root cause.
        </p>
      </div>

      {validationError && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-red-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* Main Form */}
      <div className="space-y-5">
        {/* Step 1: Problem Symptom Description */}
        <Card className="p-4 space-y-3">
          <CardHeader className="p-0 border-b border-borderColor pb-2">
            <CardTitle className="text-xs font-semibold text-textPrimary flex items-center justify-between">
              <span>Incident Description (Maximum 2,000 words) *</span>
              <span className={`text-[10px] font-mono ${descriptionWordCount > 2000 ? 'text-red-400 font-bold' : 'text-textMuted'}`}>
                {descriptionWordCount} / 2,000 words
              </span>
            </CardTitle>
          </CardHeader>

          <textarea
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe observed behavior, slowdowns, HTTP error status codes, or customer complaints (Maximum 2,000 words)..."
            className={`w-full bg-bgApp border rounded-md p-3 text-xs text-textPrimary placeholder:text-textMuted focus:outline-none font-sans resize-none leading-relaxed ${
              descriptionWordCount > 2000 ? 'border-red-500/60 focus:border-red-500' : 'border-borderColor focus:border-accentPrimary'
            }`}
          />
          {descriptionWordCount > 2000 && (
            <p className="text-[11px] text-red-400 font-medium">Incident description cannot exceed 2,000 words.</p>
          )}
        </Card>

        {/* Step 2: SEPARATE INCIDENT LOG FILE AREA (REQUIRED - UNLIMITED SIZE) */}
        <Card className="p-4 space-y-3 border-accentPrimary/40 bg-accentPrimary/5">
          <CardHeader className="p-0 border-b border-borderColor pb-2">
            <CardTitle className="text-xs font-semibold text-textPrimary flex items-center justify-between">
              <span className="text-accentPrimary font-bold flex items-center gap-1.5">
                <span>Incident Log File * (REQUIRED — 1 log file)</span>
              </span>
              <Badge variant="info" className="text-[10px]">Unlimited Size Supported</Badge>
            </CardTitle>
          </CardHeader>

          <p className="text-[11px] text-textSecondary">
            A log file (.log, .txt, .syslog, .json) is <strong className="text-accentPrimary">mandatory</strong>. File size is <strong className="text-textPrimary">unlimited</strong> and does not count toward evidence limits.
          </p>

          {stagedLogFile ? (
            <div className="p-3 bg-bgApp border border-accentPrimary/40 rounded-md flex items-center justify-between font-mono">
              <div className="flex items-center gap-3 overflow-hidden">
                <div className="w-8 h-8 rounded bg-accentPrimary/10 border border-accentPrimary/30 flex items-center justify-center text-accentPrimary shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div className="truncate">
                  <div className="text-xs font-bold text-textPrimary truncate">{stagedLogFile.name}</div>
                  <div className="text-[10px] text-textMuted">
                    {(stagedLogFile.size / (1024 * 1024)).toFixed(2)} MB • Mandatory Incident Telemetry Log
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setStagedLogFile(null)}
                className="text-[10px] text-red-400 hover:text-red-300 border-red-500/30"
              >
                Change Log File
              </Button>
            </div>
          ) : (
            <EvidenceDropzone onUpload={handleLogFileUpload} />
          )}
        </Card>

        {/* Step 3: SEPARATE TELEMETRY EVIDENCE ATTACHMENTS AREA (OPTIONAL - MAX 10 FILES) */}
        <Card className="p-4 space-y-3">
          <CardHeader className="p-0 border-b border-borderColor pb-2">
            <CardTitle className="text-xs font-semibold text-textPrimary flex items-center justify-between">
              <span className="font-bold text-textPrimary">Evidence Files (Optional — up to 10 files total)</span>
              <span className="text-[10px] text-textMuted font-mono">
                Evidence files: {stagedEvidenceFiles.length} / 10
              </span>
            </CardTitle>
          </CardHeader>

          <p className="text-[11px] text-textSecondary">
            Attach optional context such as technical documents (PDF, DOCX, PPTX - max 3 pages each) or screenshots/diagrams (PNG, JPG, WEBP). Documents and images share this limit.
          </p>

          <EvidenceDropzone onUpload={handleEvidenceFileUpload} />
          <FileList
            items={evidenceItems}
            onDelete={(id) => {
              setEvidenceItems((prev) => prev.filter((i) => i.id !== id));
              setStagedEvidenceFiles((prev) => prev.filter((f) => !id.includes(f.name)));
            }}
          />
        </Card>

        {/* Step 4: Optional Context Collapsible */}
        <Card className="p-4 space-y-3">
          <button
            onClick={() => setShowOptionalContext(!showOptionalContext)}
            className="w-full flex items-center justify-between text-xs font-semibold text-textPrimary hover:text-accentPrimary transition-colors"
          >
            <div className="flex items-center gap-2">
              <span>Optional Additional Context</span>
              <span className="text-[10px] font-mono text-textMuted italic">
                (Traceback will attempt to determine these automatically)
              </span>
            </div>
            {showOptionalContext ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showOptionalContext && (
            <div className="pt-3 border-t border-borderColor grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono">
              <div>
                <label className="block text-[10px] text-textMuted uppercase mb-1">Suspected Service</label>
                <input
                  type="text"
                  placeholder="e.g. payment-service"
                  value={affectedService}
                  onChange={(e) => setAffectedService(e.target.value)}
                  className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary"
                />
              </div>

              <div>
                <label className="block text-[10px] text-textMuted uppercase mb-1">Environment</label>
                <select
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value)}
                  className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary"
                >
                  <option value="Production">Production</option>
                  <option value="Staging">Staging</option>
                  <option value="Canary">Canary</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] text-textMuted uppercase mb-1">Recent Release Tag</label>
                <input
                  type="text"
                  placeholder="e.g. v2.4.1"
                  value={deploymentChange}
                  onChange={(e) => setDeploymentChange(e.target.value)}
                  className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary"
                />
              </div>
            </div>
          )}
        </Card>

        {/* Form Action */}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="outline" onClick={() => router.push(`/projects/${projectId}/incidents`)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            disabled={!description.trim() || !stagedLogFile}
            onClick={handleOpenConfirmModal}
            className="gap-2 font-semibold"
          >
            <Sparkles className="w-4 h-4" />
            <span>Launch AI Root Cause Investigation</span>
          </Button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-black/75 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-bgSurface border border-borderColor rounded-lg w-full max-w-md p-5 space-y-4 shadow-2xl">
            <h3 className="text-sm font-bold text-textPrimary flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-accentPrimary" />
              <span>Confirm AI Investigation Launch</span>
            </h3>

            {modalError && (
              <div className="p-3 bg-red-500/10 border border-red-500/30 rounded text-red-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{modalError}</span>
              </div>
            )}

            <div className="p-3 bg-bgApp border border-borderColor rounded text-xs space-y-2 font-mono">
              <div className="flex justify-between">
                <span className="text-textMuted">Project:</span>
                <span className="font-bold text-accentPrimary">{projectName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-textMuted">Required Log File:</span>
                <span className="text-accentPrimary font-bold">{stagedLogFile ? stagedLogFile.name : 'Missing'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-textMuted">Evidence Attachments:</span>
                <span className="text-textPrimary">{stagedEvidenceFiles.length} / 10 files</span>
              </div>
              <div className="flex justify-between">
                <span className="text-textMuted">Target Environment:</span>
                <span className="text-textPrimary">{environment}</span>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-borderColor">
              <Button variant="ghost" onClick={() => setShowConfirmModal(false)}>
                Go Back
              </Button>
              <Button variant="primary" isLoading={isSubmitting} onClick={handleCreateIncident}>
                Confirm & Launch Engine
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
