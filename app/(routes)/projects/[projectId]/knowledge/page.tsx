'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Project, KnowledgeDocument, KnowledgeCategory } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { AddKnowledgeModal } from '@/components/knowledge/AddKnowledgeModal';
import { DocumentDetailsModal } from '@/components/knowledge/DocumentDetailsModal';
import { DeleteKnowledgeModal } from '@/components/knowledge/DeleteKnowledgeModal';
import { Search, UploadCloud, FileText, CheckCircle2, Trash2, Eye, AlertTriangle, RefreshCw, Plus } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

const categories: KnowledgeCategory[] = [
  'Technical Documentation',
  'Runbook',
  'Architecture',
  'Previous Incident',
  'Post-Mortem',
  'Troubleshooting Guide',
  'API Documentation',
  'Database Documentation',
  'Deployment Documentation',
  'Other',
];

export default function ProjectKnowledgePage() {
  const params = useParams();
  const projectId = (params?.projectId as string) || 'shopflow';

  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // Modal states
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const [selectedDocForDetails, setSelectedDocForDetails] = useState<KnowledgeDocument | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

  const [docToDelete, setDocToDelete] = useState<KnowledgeDocument | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const fetchDocs = async () => {
    setIsLoading(true);
    const [proj, data] = await Promise.all([
      api.getProject(projectId).catch(() => null),
      api.getKnowledge({
        projectId,
        query: search,
        type: activeCategory !== 'ALL' ? activeCategory : undefined,
      }).catch(() => []),
    ]);
    setProject(proj);
    setDocuments(data);
    setIsLoading(false);
  };

  useEffect(() => {
    fetchDocs();
  }, [projectId, search, activeCategory]);

  const handleOpenDetails = (doc: KnowledgeDocument) => {
    setSelectedDocForDetails(doc);
    setIsDetailsModalOpen(true);
  };

  const handleOpenDelete = (doc: KnowledgeDocument) => {
    setDocToDelete(doc);
    setIsDeleteModalOpen(true);
  };

  const handleRetryIndexing = async (doc: KnowledgeDocument) => {
    await api.retryKnowledgeIndexing(doc.id, projectId);
    fetchDocs();
  };

  const renderStatusBadge = (doc: KnowledgeDocument) => {
    switch (doc.status) {
      case 'INDEXED':
        return (
          <Badge variant="success" size="sm" className="gap-1 font-mono">
            <CheckCircle2 className="w-3 h-3" />
            <span>INDEXED</span>
          </Badge>
        );
      case 'INDEXING':
      case 'PROCESSING':
      case 'UPLOADING':
        return (
          <Badge variant="warning" size="sm" className="gap-1 font-mono">
            <RefreshCw className="w-3 h-3 animate-spin" />
            <span>{doc.status}</span>
          </Badge>
        );
      case 'FAILED':
        return (
          <Badge variant="danger" size="sm" className="gap-1 font-mono">
            <AlertTriangle className="w-3 h-3" />
            <span>FAILED</span>
          </Badge>
        );
      default:
        return (
          <Badge variant="success" size="sm" className="gap-1 font-mono">
            <CheckCircle2 className="w-3 h-3" />
            <span>INDEXED</span>
          </Badge>
        );
    }
  };

  const projectName = project ? project.name : projectId;

  return (
    <div className="space-y-5 max-w-7xl mx-auto text-xs pb-10">
      {/* Top Bar Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-borderColor pb-3">
        <div>
          <h1 className="text-lg font-bold text-textPrimary font-mono">
            {projectName} — Vector Knowledge Base
          </h1>
          <p className="text-xs text-textSecondary mt-0.5">
            Technical documents, runbooks, architecture specs, and post-mortems isolated to project <span className="font-mono text-accentPrimary">{projectName}</span>.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={() => setIsAddModalOpen(true)}
          className="gap-1.5 text-xs font-semibold shrink-0 font-mono"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Add Knowledge Document</span>
        </Button>
      </div>

      {/* Category Pills & Search */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 font-mono">
          <button
            onClick={() => setActiveCategory('ALL')}
            className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
              activeCategory === 'ALL'
                ? 'bg-accentPrimary text-white font-semibold'
                : 'bg-bgSurface text-textSecondary hover:bg-bgSurfaceHover border border-borderColor'
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors whitespace-nowrap ${
                activeCategory === cat
                  ? 'bg-accentPrimary text-white font-semibold'
                  : 'bg-bgSurface text-textSecondary hover:bg-bgSurfaceHover border border-borderColor'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-textMuted" />
          <input
            type="text"
            placeholder="Filter knowledge documents..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-bgSurface border border-borderColor rounded pl-8 pr-3 py-1.5 text-xs text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentPrimary"
          />
        </div>
      </div>

      {/* Documents Table or Empty State */}
      {isLoading ? (
        <Skeleton className="h-64" />
      ) : documents.length === 0 ? (
        <Card className="p-8 text-center space-y-3 border-dashed border-borderColor max-w-lg mx-auto">
          <div className="w-12 h-12 rounded-full bg-bgApp border border-borderColor flex items-center justify-center mx-auto text-accentPrimary">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-textPrimary text-sm font-mono">No knowledge documents yet in {projectName}</h3>
            <p className="text-textMuted text-xs mt-1 leading-relaxed">
              Upload runbooks, architecture documents, post-mortems, and troubleshooting guides to give TRACEBACK technical context during AI investigations.
            </p>
          </div>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsAddModalOpen(true)}
            className="gap-1.5 font-mono text-xs"
          >
            <Plus className="w-4 h-4" />
            <span>Add Knowledge Document</span>
          </Button>
        </Card>
      ) : (
        <Card className="p-0 overflow-hidden border-borderColor">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-textSecondary">
              <thead className="bg-bgSecondary text-textMuted uppercase font-mono border-b border-borderColor text-[10px] tracking-wider">
                <tr>
                  <th className="px-4 py-2.5">Document</th>
                  <th className="px-4 py-2.5">Category</th>
                  <th className="px-4 py-2.5 font-mono">Size</th>
                  <th className="px-4 py-2.5 font-mono">Chunks</th>
                  <th className="px-4 py-2.5">Status</th>
                  <th className="px-4 py-2.5 font-mono">Uploaded</th>
                  <th className="px-4 py-2.5 text-right font-mono">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-borderColor font-sans">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-bgSurfaceHover/60 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-accentPrimary shrink-0" />
                        <div>
                          <p className="font-semibold text-textPrimary font-mono">{doc.name}</p>
                          {doc.summary && (
                            <p className="text-[11px] text-textMuted line-clamp-1 font-sans">{doc.summary}</p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="outline" size="sm" className="font-mono text-[10px]">
                        {doc.category}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-textMuted">
                      {doc.fileSize || '320 KB'}
                    </td>
                    <td className="px-4 py-3 font-mono text-[11px] text-textMuted">
                      {doc.chunks ? `${doc.chunks} chunks` : '-'}
                    </td>
                    <td className="px-4 py-3">{renderStatusBadge(doc)}</td>
                    <td className="px-4 py-3 font-mono text-[11px] text-textMuted">{doc.uploadedAt}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {doc.status === 'FAILED' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleRetryIndexing(doc)}
                            className="gap-1 text-[10px] h-7 px-2 font-mono"
                          >
                            <RefreshCw className="w-3 h-3" />
                            <span>Retry</span>
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleOpenDetails(doc)}
                          className="gap-1 text-[10px] h-7 px-2 font-mono"
                        >
                          <Eye className="w-3 h-3" />
                          <span>View</span>
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleOpenDelete(doc)}
                          className="gap-1 text-[10px] h-7 px-2 font-mono"
                        >
                          <Trash2 className="w-3 h-3" />
                          <span>Delete</span>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Add Knowledge Modal */}
      <AddKnowledgeModal
        isOpen={isAddModalOpen}
        projectId={projectId}
        projectName={projectName}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={fetchDocs}
      />

      {/* Document Details Modal */}
      {selectedDocForDetails && (
        <DocumentDetailsModal
          isOpen={isDetailsModalOpen}
          doc={selectedDocForDetails}
          projectId={projectId}
          projectName={projectName}
          onClose={() => setIsDetailsModalOpen(false)}
          onDelete={handleOpenDelete}
        />
      )}

      {/* Delete Knowledge Confirmation Modal */}
      {docToDelete && (
        <DeleteKnowledgeModal
          isOpen={isDeleteModalOpen}
          doc={docToDelete}
          projectId={projectId}
          projectName={projectName}
          onClose={() => setIsDeleteModalOpen(false)}
          onSuccess={fetchDocs}
        />
      )}
    </div>
  );
}
