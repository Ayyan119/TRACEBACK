'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname, useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Incident, Service, KnowledgeDocument } from '@/types';
import { Search, AlertTriangle, Server, FileText, ArrowRight, X } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

export const GlobalSearch: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const router = useRouter();
  const pathname = usePathname();
  const params = useParams();
  const [query, setQuery] = useState('');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [docs, setDocs] = useState<KnowledgeDocument[]>([]);

  let currentProjectId = (params?.projectId as string) || 'shopflow';
  if (!params?.projectId && pathname) {
    const match = pathname.match(/\/projects\/([^\/]+)/);
    if (match) currentProjectId = match[1];
  }

  useEffect(() => {
    if (!isOpen) return;

    const fetchData = async () => {
      const [incData, srvData, docData] = await Promise.all([
        api.getIncidents({ projectId: currentProjectId }),
        api.getServices({ projectId: currentProjectId }),
        api.getKnowledge({ projectId: currentProjectId }),
      ]);
      setIncidents(incData);
      setServices(srvData);
      setDocs(docData);
    };

    fetchData();
  }, [isOpen, currentProjectId]);

  if (!isOpen) return null;

  const filteredIncidents = query
    ? incidents.filter((i) => i.title.toLowerCase().includes(query.toLowerCase()) || i.code.toLowerCase().includes(query.toLowerCase()))
    : incidents;

  const filteredServices = query
    ? services.filter((s) => s.name.toLowerCase().includes(query.toLowerCase()))
    : services;

  const filteredDocs = query
    ? docs.filter((d) => d.name.toLowerCase().includes(query.toLowerCase()) || d.summary?.toLowerCase().includes(query.toLowerCase()))
    : docs;

  const handleNavigate = (path: string) => {
    onClose();
    router.push(path);
  };

  return (
    <div className="fixed inset-0 bg-black/75 backdrop-blur-xs z-50 flex items-start justify-center pt-20 p-4">
      <div className="bg-bgSurface border border-borderColor rounded-lg w-full max-w-2xl overflow-hidden shadow-2xl space-y-0 text-xs">
        {/* Search Input Bar */}
        <div className="p-3 border-b border-borderColor flex items-center gap-2 bg-bgApp">
          <Search className="w-4 h-4 text-accentPrimary shrink-0" />
          <input
            type="text"
            placeholder={`Search ${currentProjectId.toUpperCase()} incidents, services, documents...`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="w-full bg-transparent text-sm text-textPrimary placeholder:text-textMuted focus:outline-none font-sans"
          />
          <Badge variant="outline" className="font-mono text-[10px] uppercase">
            {currentProjectId}
          </Badge>
          <button onClick={onClose} className="p-1 text-textMuted hover:text-textPrimary">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search Results Content */}
        <div className="max-h-96 overflow-y-auto p-3 space-y-4 font-sans">
          {/* Incidents Section */}
          {filteredIncidents.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[10px] font-mono font-semibold uppercase text-textMuted flex items-center gap-1.5">
                <AlertTriangle className="w-3 h-3 text-statusDanger" />
                <span>Incidents ({filteredIncidents.length})</span>
              </span>

              <div className="space-y-1">
                {filteredIncidents.map((inc) => (
                  <div
                    key={inc.id}
                    onClick={() => handleNavigate(`/projects/${currentProjectId}/incidents/${inc.id}/investigation`)}
                    className="p-2.5 bg-bgApp hover:bg-bgSurfaceHover border border-borderColor rounded flex items-center justify-between cursor-pointer transition-colors"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-accentPrimary">{inc.code}</span>
                        <span className="font-semibold text-textPrimary">{inc.title}</span>
                      </div>
                      <p className="text-[11px] text-textMuted mt-0.5">{inc.affectedService} • {inc.detectedAt}</p>
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-textMuted" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Services Section */}
          {filteredServices.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[10px] font-mono font-semibold uppercase text-textMuted flex items-center gap-1.5">
                <Server className="w-3 h-3 text-accentPrimary" />
                <span>Services ({filteredServices.length})</span>
              </span>

              <div className="grid grid-cols-2 gap-2">
                {filteredServices.map((srv) => (
                  <div
                    key={srv.id}
                    onClick={() => handleNavigate(`/projects/${currentProjectId}/services`)}
                    className="p-2 bg-bgApp hover:bg-bgSurfaceHover border border-borderColor rounded flex items-center justify-between cursor-pointer"
                  >
                    <span className="font-mono font-bold text-textPrimary text-xs">{srv.name}</span>
                    <Badge variant={srv.health === 'Healthy' ? 'success' : srv.health === 'Degraded' ? 'warning' : 'danger'}>
                      {srv.health}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Knowledge Section */}
          {filteredDocs.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[10px] font-mono font-semibold uppercase text-textMuted flex items-center gap-1.5">
                <FileText className="w-3 h-3 text-accentPrimary" />
                <span>Knowledge Documents ({filteredDocs.length})</span>
              </span>

              <div className="space-y-1">
                {filteredDocs.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => handleNavigate(`/projects/${currentProjectId}/knowledge`)}
                    className="p-2 bg-bgApp hover:bg-bgSurfaceHover border border-borderColor rounded flex items-center justify-between cursor-pointer"
                  >
                    <div>
                      <span className="font-mono font-semibold text-textPrimary">{doc.name}</span>
                      <p className="text-[10px] text-textMuted">{doc.category} • {doc.chunks} chunks</p>
                    </div>
                    <Badge variant="outline">{doc.status}</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
