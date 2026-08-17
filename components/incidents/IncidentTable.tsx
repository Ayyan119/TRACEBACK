'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Incident } from '@/types';
import { SeverityBadge } from './SeverityBadge';
import { StatusBadge } from './StatusBadge';
import { Badge } from '@/components/ui/Badge';
import { Sparkles, ExternalLink, Trash2, CheckCircle2, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { DeleteIncidentModal } from './DeleteIncidentModal';
import { api } from '@/lib/api';

interface IncidentTableProps {
  incidents: Incident[];
  isLoading?: boolean;
  projectName?: string;
  onRefresh?: () => void;
}

export const IncidentTable: React.FC<IncidentTableProps> = ({ incidents, isLoading = false, projectName, onRefresh }) => {
  const [incidentToDelete, setIncidentToDelete] = useState<Incident | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deletedIds, setDeletedIds] = useState<string[]>([]);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const visibleIncidents = incidents.filter((inc) => !deletedIds.includes(inc.id));

  const handleStatusChange = async (incidentId: string, newStatus: string) => {
    setUpdatingId(incidentId);
    try {
      if (newStatus === 'Resolved') {
        await api.resolveIncident(incidentId);
      } else {
        await api.updateIncident(incidentId, { status: newStatus as any });
      }
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Failed to update status:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 bg-bgSecondary border border-borderColor rounded animate-pulse" />
        ))}
      </div>
    );
  }

  if (visibleIncidents.length === 0) {
    return (
      <div className="text-center py-8 bg-bgSecondary border border-borderColor rounded">
        <p className="text-textSecondary text-xs font-mono">No incidents match the selected filters.</p>
      </div>
    );
  }

  const handleOpenDelete = (inc: Incident) => {
    setIncidentToDelete(inc);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteSuccess = () => {
    if (incidentToDelete) {
      setDeletedIds((prev) => [...prev, incidentToDelete.id]);
    }
    if (onRefresh) {
      onRefresh();
    }
  };

  return (
    <div className="bg-bgSurface border border-borderColor rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-textSecondary">
          <thead className="bg-bgSecondary text-textMuted uppercase font-mono border-b border-borderColor text-[10px] tracking-wider">
            <tr>
              <th className="px-3 py-2.5">
                <span className="inline-flex items-center gap-1">
                  Status <ChevronDown className="w-3 h-3 text-accentPrimary" />
                </span>
              </th>
              <th className="px-3 py-2.5">Incident</th>
              <th className="px-3 py-2.5">Severity</th>
              <th className="px-3 py-2.5">Affected Service</th>
              <th className="px-3 py-2.5 font-mono">Detected</th>
              <th className="px-3 py-2.5 font-mono">Duration</th>
              <th className="px-3 py-2.5 font-mono">Confidence</th>
              <th className="px-3 py-2.5 font-mono">Updated</th>
              <th className="px-3 py-2.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-borderColor font-sans">
            {visibleIncidents.map((incident) => {
              const pid = incident.projectId || 'shopflow';
              const isUpdating = updatingId === incident.id;
              const isResolved = incident.status === 'Resolved';

              return (
                <tr key={incident.id} className="hover:bg-bgSurfaceHover/60 transition-colors">
                  {/* Left Side Neutral Status Change Dropdown */}
                  <td className="px-3 py-3">
                    <div className="relative inline-flex items-center">
                      <select
                        value=""
                        disabled={isUpdating}
                        onChange={(e) => {
                          if (e.target.value) handleStatusChange(incident.id, e.target.value);
                        }}
                        className="bg-bgApp border border-borderColor text-textSecondary hover:text-textPrimary hover:border-accentPrimary font-mono text-[11px] font-semibold rounded px-2.5 py-1 cursor-pointer focus:outline-none appearance-none pr-6 transition-colors"
                        title="Click to change status"
                      >
                        <option value="" disabled className="text-textMuted bg-bgSurface">
                          Status
                        </option>
                        <option value="Investigating" className="bg-bgSurface text-textPrimary">Investigating</option>
                        <option value="Identified" className="bg-bgSurface text-textPrimary">Identified</option>
                        <option value="Monitoring" className="bg-bgSurface text-textPrimary">Monitoring</option>
                        <option value="Resolved" className="bg-bgSurface text-statusSuccess font-bold">✓ Resolved</option>
                      </select>
                      <ChevronDown className="w-3 h-3 absolute right-2 top-2 pointer-events-none text-textMuted" />
                    </div>
                  </td>
                  <td className="px-3 py-3">
                    <Link
                      href={`/projects/${pid}/incidents/${incident.id}`}
                      className="font-semibold text-textPrimary hover:text-accentPrimary flex items-center gap-1.5 group"
                    >
                      <span className="font-mono text-accentPrimary font-bold text-[11px]">{incident.code}:</span>
                      <span>{incident.title}</span>
                      <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  </td>
                  <td className="px-3 py-3">
                    <SeverityBadge severity={incident.severity} />
                  </td>
                  <td className="px-3 py-3 font-mono text-[11px] text-textPrimary">
                    {incident.affectedService}
                  </td>
                  <td className="px-3 py-3 font-mono text-[11px] text-textMuted">{incident.detectedAt}</td>
                  <td className="px-3 py-3 font-mono text-[11px] text-textMuted">{incident.duration}</td>
                  <td className="px-3 py-3 font-mono text-[11px]">
                    <Badge variant="confidence" size="sm">
                      {incident.confidence}%
                    </Badge>
                  </td>
                  <td className="px-3 py-3 font-mono text-[11px] text-textMuted">{incident.updatedAt}</td>
                  <td className="px-3 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {/* Right side: Beautiful text badge showing current status */}
                      <StatusBadge status={incident.status} />

                      <Link href={`/projects/${pid}/incidents/${incident.id}/investigation`}>
                        <Button size="sm" variant="outline" className="gap-1 text-[11px] h-7 px-2 font-mono">
                          <Sparkles className="w-3 h-3 text-accentPrimary" />
                          <span>Report</span>
                        </Button>
                      </Link>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleOpenDelete(incident)}
                        className="gap-1 text-[10px] h-7 px-2 font-mono"
                        title="Delete Incident"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {incidentToDelete && (
        <DeleteIncidentModal
          isOpen={isDeleteModalOpen}
          incident={incidentToDelete}
          projectId={incidentToDelete.projectId || 'shopflow'}
          projectName={projectName}
          onClose={() => setIsDeleteModalOpen(false)}
          onSuccess={handleDeleteSuccess}
        />
      )}
    </div>
  );
};
