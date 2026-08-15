'use client';

import React, { useRef } from 'react';
import { UploadCloud, FileText } from 'lucide-react';

interface EvidenceDropzoneProps {
  onUpload: (files: File[]) => void;
}

export const EvidenceDropzone: React.FC<EvidenceDropzoneProps> = ({ onUpload }) => {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(Array.from(e.target.files));
    }
  };

  return (
    <div
      onClick={() => inputRef.current?.click()}
      className="border-2 border-dashed border-borderColor hover:border-accentPrimary/60 bg-bgApp hover:bg-bgSurfaceHover/40 rounded-lg p-6 text-center cursor-pointer transition-colors space-y-2 select-none"
    >
      <input
        type="file"
        ref={inputRef}
        onChange={handleFileChange}
        multiple
        className="hidden"
      />
      <div className="w-10 h-10 rounded-full bg-accentSubtle text-accentPrimary mx-auto flex items-center justify-center border border-accentPrimary/30">
        <UploadCloud className="w-5 h-5" />
      </div>
      <div>
        <p className="font-semibold text-xs text-textPrimary">
          Click or Drag & Drop Telemetry Evidence Files
        </p>
        <p className="text-[10px] text-textMuted font-mono mt-0.5">
          Supports .log, .json, .csv, .png, .txt, .pdf (Max 50MB)
        </p>
      </div>
    </div>
  );
};
