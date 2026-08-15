'use client';

import React, { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';
import { KnowledgeCategory } from '@/types';
import { Button } from '@/components/ui/Button';
import { UploadCloud, FileText, Trash2, X, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface AddKnowledgeModalProps {
  isOpen: boolean;
  projectId: string;
  projectName?: string;
  onClose: () => void;
  onSuccess: () => void;
}

const ALLOWED_EXTENSIONS = ['PDF', 'DOCX', 'DOC', 'MD', 'TXT', 'CSV', 'JSON', 'YAML', 'YML', 'LOG'];
const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024; // 50 MB

export const AddKnowledgeModal: React.FC<AddKnowledgeModalProps> = ({
  isOpen,
  projectId,
  projectName,
  onClose,
  onSuccess,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [category, setCategory] = useState<KnowledgeCategory>('Runbook');
  const [summary, setSummary] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [statusText, setStatusText] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setSelectedFiles([]);
      setSummary('');
      setErrorMsg(null);
      setStatusText(null);
      setIsSubmitting(false);
      setCategory('Runbook');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const validateAndAddFiles = (files: FileList | File[]) => {
    setErrorMsg(null);
    const valid: File[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const ext = file.name.split('.').pop()?.toUpperCase() || '';

      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        setErrorMsg(`"${file.name}" has an unsupported format. Allowed: PDF, DOCX, DOC, MD, TXT, CSV, JSON, YAML, LOG.`);
        continue;
      }

      if (file.size > MAX_FILE_SIZE_BYTES) {
        setErrorMsg(`"${file.name}" exceeds the 50 MB file size limit.`);
        continue;
      }

      valid.push(file);
    }

    if (valid.length > 0) {
      setSelectedFiles((prev) => [...prev, ...valid]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndAddFiles(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndAddFiles(e.target.files);
    }
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
    if (selectedFiles.length <= 1) setErrorMsg(null);
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) return;

    setIsSubmitting(true);
    try {
      setStatusText('Uploading...');
      await new Promise((r) => setTimeout(r, 400));

      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        setStatusText(`Indexing document ${i + 1} of ${selectedFiles.length}...`);

        await api.uploadKnowledge({
          projectId,
          file,
          category,
          summary: summary.trim() || undefined,
        });
      }

      setStatusText('Indexed');
      await new Promise((r) => setTimeout(r, 200));

      onSuccess();
      onClose();
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to upload document');
    } finally {
      setIsSubmitting(false);
      setStatusText(null);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-bgSurface border border-borderColor rounded-lg w-full max-w-lg p-5 space-y-4 shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-borderColor pb-3">
          <div>
            <h3 className="text-sm font-bold text-textPrimary font-mono">Add Knowledge Document</h3>
            <p className="text-[11px] text-textMuted mt-0.5">
              Upload technical documentation, runbooks, post-mortems, or troubleshooting guides for <strong className="text-accentPrimary font-mono">{projectName || projectId}</strong>.
            </p>
          </div>
          <button onClick={onClose} className="text-textMuted hover:text-textPrimary p-1">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Validation Error Banner */}
        {errorMsg && (
          <div className="p-3 bg-statusDanger/10 border border-statusDanger/30 rounded flex items-start gap-2 text-statusDanger font-mono text-[11px]">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <div className="flex-1">{errorMsg}</div>
            <button onClick={() => setErrorMsg(null)} className="hover:text-textPrimary">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* File Upload Area */}
          <div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              multiple
              accept=".pdf,.docx,.doc,.md,.txt,.csv,.json,.yaml,.yml,.log"
              className="hidden"
            />

            {selectedFiles.length === 0 ? (
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragOver(true);
                }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`p-6 border-2 border-dashed rounded-lg text-center cursor-pointer transition-all ${
                  isDragOver
                    ? 'border-accentPrimary bg-accentSubtle/20'
                    : 'border-borderColor bg-bgApp hover:border-accentPrimary/60 hover:bg-bgSurfaceHover/50'
                }`}
              >
                <UploadCloud className="w-8 h-8 text-accentPrimary mx-auto mb-2" />
                <p className="font-bold text-textPrimary text-xs font-mono">
                  Drop files here or <span className="text-accentPrimary underline">Browse files</span>
                </p>
                <p className="text-[10px] text-textMuted font-mono mt-1">
                  PDF, DOCX, DOC, MD, TXT, CSV, JSON, YAML, LOG
                </p>
                <p className="text-[10px] text-textMuted font-mono mt-0.5">Maximum file size: 50 MB</p>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between font-mono text-[11px] text-textMuted border-b border-borderColor pb-1">
                  <span>Selected Files ({selectedFiles.length})</span>
                  <button
                    type="button"
                    onClick={() => setSelectedFiles([])}
                    className="text-statusDanger hover:underline"
                  >
                    Remove all
                  </button>
                </div>

                <div className="space-y-1.5 max-h-40 overflow-y-auto">
                  {selectedFiles.map((f, idx) => {
                    const ext = f.name.split('.').pop()?.toUpperCase() || 'FILE';
                    return (
                      <div
                        key={idx}
                        className="p-2.5 bg-bgApp border border-borderColor rounded flex items-center justify-between font-mono text-xs"
                      >
                        <div className="flex items-center gap-2 truncate">
                          <FileText className="w-4 h-4 text-accentPrimary shrink-0" />
                          <span className="font-semibold text-textPrimary truncate">{f.name}</span>
                          <span className="px-1.5 py-0.5 text-[9px] bg-bgSurface border border-borderColor rounded text-textMuted uppercase">
                            {ext}
                          </span>
                          <span className="text-[10px] text-textMuted">{formatSize(f.size)}</span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveFile(idx)}
                          className="text-textMuted hover:text-statusDanger p-1 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    );
                  })}
                </div>

                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-[11px] font-mono text-accentPrimary hover:underline flex items-center gap-1 mt-1"
                >
                  <span>+ Add another file</span>
                </button>
              </div>
            )}
          </div>

          {/* Optional Metadata Section */}
          <div className="space-y-3 pt-2 border-t border-borderColor">
            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Category (Optional)
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value as KnowledgeCategory)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary font-sans"
              >
                <option value="Technical Documentation">Technical Documentation</option>
                <option value="Runbook">Runbook</option>
                <option value="Architecture">Architecture</option>
                <option value="Previous Incident">Previous Incident</option>
                <option value="Post-Mortem">Post-Mortem</option>
                <option value="Troubleshooting Guide">Troubleshooting Guide</option>
                <option value="API Documentation">API Documentation</option>
                <option value="Database Documentation">Database Documentation</option>
                <option value="Deployment Documentation">Deployment Documentation</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-mono text-textSecondary mb-1">
                Description / Summary (Optional)
              </label>
              <textarea
                rows={2}
                placeholder="Briefly describe what this technical document contains..."
                value={summary}
                onChange={(e) => setSummary(e.target.value)}
                className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary focus:outline-none focus:border-accentPrimary resize-none font-sans"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-3 border-t border-borderColor">
            <Button type="button" variant="ghost" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
              disabled={selectedFiles.length === 0}
              className="font-mono text-xs"
            >
              {statusText ? (
                statusText
              ) : selectedFiles.length > 1 ? (
                `Upload & Index ${selectedFiles.length} Documents`
              ) : (
                'Upload & Index'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
