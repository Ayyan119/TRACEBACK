'use client';

import React, { useState, useRef } from 'react';
import { api } from '@/lib/api';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Image as ImageIcon, FileUp, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { EvidenceType } from '@/types';

interface EvidenceUploaderProps {
  incidentId: string;
  onUploadComplete?: () => void;
}

export const EvidenceUploader: React.FC<EvidenceUploaderProps> = ({ incidentId, onUploadComplete }) => {
  const [activeTab, setActiveTab] = useState<'text' | 'file'>('file');
  const [evidenceType, setEvidenceType] = useState<EvidenceType>('log');
  const [rawText, setRawText] = useState('');
  const [title, setTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (!title) {
        setTitle(file.name);
      }
      setErrorMessage(null);

      // Auto-detect type
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (['png', 'jpg', 'jpeg', 'webp', 'svg'].includes(ext || '')) {
        setEvidenceType('screenshot');
      } else if (['log', 'txt'].includes(ext || '')) {
        setEvidenceType('log');
      }
    }
  };

  const handleUploadFile = async () => {
    if (!selectedFile) return;

    setIsSubmitting(true);
    setStatusMessage('Uploading evidence file...');
    setErrorMessage(null);

    try {
      await api.uploadEvidence(
        incidentId,
        selectedFile,
        title.trim() || selectedFile.name,
        evidenceType,
        'User Upload'
      );

      setStatusMessage('Evidence file successfully uploaded & attached!');
      setSelectedFile(null);
      setTitle('');
      if (fileInputRef.current) fileInputRef.current.value = '';

      if (onUploadComplete) onUploadComplete();
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to upload evidence file');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleProcessText = async () => {
    if (!rawText.trim()) return;

    setIsSubmitting(true);
    setStatusMessage('Processing text evidence...');
    setErrorMessage(null);

    try {
      await api.createEvidence({
        incidentId,
        type: evidenceType,
        title: title.trim() || `${evidenceType.toUpperCase()} Snippet`,
        source: 'User Input',
        rawContent: rawText.trim(),
      });

      setStatusMessage('Telemetry snippet attached successfully!');
      setRawText('');
      setTitle('');

      if (onUploadComplete) onUploadComplete();
    } catch (err: any) {
      setErrorMessage(err?.message || 'Failed to process telemetry snippet');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-bgSurface border border-borderColor rounded-lg p-5 space-y-4 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-borderColor pb-3">
        <h3 className="text-sm font-semibold text-textPrimary flex items-center gap-2 font-mono">
          <UploadCloud className="w-4 h-4 text-accentPrimary" />
          <span>Ingest Telemetry & Evidence</span>
        </h3>

        <div className="flex items-center gap-2">
          <select
            value={evidenceType}
            onChange={(e) => setEvidenceType(e.target.value as EvidenceType)}
            className="bg-bgApp border border-borderColor text-textPrimary text-xs rounded px-2.5 py-1 focus:outline-none focus:border-accentPrimary font-mono"
          >
            <option value="log">Application Log (.log)</option>
            <option value="screenshot">Screenshot / Image (.png, .jpg, .webp)</option>
            <option value="stack_trace">Stack Trace (.txt)</option>
            <option value="metric">Metrics / CSV Export</option>
            <option value="deployment">Deployment Manifest / Diff</option>
            <option value="document">Technical Document</option>
          </select>
        </div>
      </div>

      {/* Mode Selector Tabs */}
      <div className="flex items-center gap-2 border-b border-borderColor/60 pb-2">
        <button
          type="button"
          onClick={() => {
            setActiveTab('file');
            setErrorMessage(null);
            setStatusMessage(null);
          }}
          className={`px-3 py-1 rounded text-xs font-mono transition-colors flex items-center gap-1.5 ${
            activeTab === 'file'
              ? 'bg-accentPrimary text-white font-semibold'
              : 'bg-bgApp text-textSecondary hover:bg-bgSurfaceHover border border-borderColor'
          }`}
        >
          <FileUp className="w-3.5 h-3.5" />
          <span>Attach File / Image</span>
        </button>
        <button
          type="button"
          onClick={() => {
            setActiveTab('text');
            setErrorMessage(null);
            setStatusMessage(null);
          }}
          className={`px-3 py-1 rounded text-xs font-mono transition-colors flex items-center gap-1.5 ${
            activeTab === 'text'
              ? 'bg-accentPrimary text-white font-semibold'
              : 'bg-bgApp text-textSecondary hover:bg-bgSurfaceHover border border-borderColor'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Paste Text / Stack Trace</span>
        </button>
      </div>

      {/* Common Title Input */}
      <div className="space-y-1">
        <label className="text-[11px] text-textMuted font-mono block">Evidence Title (Optional):</label>
        <input
          type="text"
          placeholder="e.g., Auth Service Memory Panic Trace"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full bg-bgApp border border-borderColor rounded p-2 text-xs text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentPrimary font-mono"
        />
      </div>

      {/* File Upload Mode */}
      {activeTab === 'file' && (
        <div className="space-y-3">
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-borderColor hover:border-accentPrimary/60 bg-bgApp hover:bg-bgSurfaceHover/40 rounded-lg p-6 text-center cursor-pointer transition-colors space-y-2 select-none"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".png,.jpg,.jpeg,.webp,.svg,.log,.txt,.json,.csv,.pdf"
              className="hidden"
            />
            <div className="w-10 h-10 rounded-full bg-accentSubtle text-accentPrimary mx-auto flex items-center justify-center border border-accentPrimary/30">
              {evidenceType === 'screenshot' ? <ImageIcon className="w-5 h-5" /> : <FileUp className="w-5 h-5" />}
            </div>
            <div>
              <p className="font-semibold text-xs text-textPrimary">
                {selectedFile ? selectedFile.name : 'Click to select image or log file'}
              </p>
              <p className="text-[10px] text-textMuted font-mono mt-0.5">
                {selectedFile
                  ? `${(selectedFile.size / 1024).toFixed(1)} KB — ${selectedFile.type || 'File'}`
                  : 'Supports PNG, JPG, WEBP, LOG, TXT, PDF, JSON (Max 50MB)'}
              </p>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button
              variant="primary"
              size="sm"
              onClick={handleUploadFile}
              disabled={!selectedFile || isSubmitting}
              className="gap-2 text-xs font-mono"
            >
              {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <UploadCloud className="w-3.5 h-3.5" />}
              <span>Upload & Attach File</span>
            </Button>
          </div>
        </div>
      )}

      {/* Text Paste Mode */}
      {activeTab === 'text' && (
        <div className="space-y-3">
          <textarea
            rows={5}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste log output, panic stack trace, or configuration payload here..."
            className="w-full bg-bgApp border border-borderColor rounded-md p-3 font-mono text-xs text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentPrimary resize-none"
          />

          <div className="flex justify-end pt-2">
            <Button
              variant="primary"
              size="sm"
              onClick={handleProcessText}
              disabled={!rawText.trim() || isSubmitting}
              className="gap-2 text-xs font-mono"
            >
              {isSubmitting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <FileText className="w-3.5 h-3.5" />}
              <span>Process & Attach Text Snippet</span>
            </Button>
          </div>
        </div>
      )}

      {/* Status Messages */}
      {statusMessage && !errorMessage && (
        <div className="p-2.5 bg-emerald-950/30 border border-emerald-800/40 rounded text-statusSuccess text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{statusMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-2.5 bg-rose-950/30 border border-rose-800/40 rounded text-statusDanger text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
