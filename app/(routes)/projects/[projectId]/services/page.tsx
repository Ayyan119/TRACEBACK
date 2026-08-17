'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Project, Service } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ServiceFormModal } from '@/components/services/ServiceFormModal';
import { DeleteServiceModal } from '@/components/services/DeleteServiceModal';
import { Server, Activity, GitCommit, Layers, Plus, Edit2, Trash2, ExternalLink } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ProjectServicesPage() {
  const params = useParams();
  const projectId = (params?.projectId as string) || 'shopflow';

  const [project, setProject] = useState<Project | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Modal states
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [serviceToEdit, setServiceToEdit] = useState<Service | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [serviceToDelete, setServiceToDelete] = useState<Service | null>(null);

  const fetchServices = async () => {
    if (services.length === 0) {
      setIsLoading(true);
    }
    const [proj, data] = await Promise.all([
      api.getProject(projectId).catch(() => null),
      api.getServices({ projectId }).catch(() => []),
    ]);
    setProject(proj);
    setServices(data);
    if (data.length > 0) {
      if (!selectedService || !data.find((s) => s.id === selectedService.id)) {
        setSelectedService(data[0]);
      }
    } else {
      setSelectedService(null);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    fetchServices();
  }, [projectId]);

  const badgeMap: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
    Healthy: 'success',
    Degraded: 'warning',
    Critical: 'danger',
    Unknown: 'default',
  };

  const handleOpenAddModal = () => {
    setServiceToEdit(null);
    setIsFormModalOpen(true);
  };

  const handleOpenEditModal = (srv: Service) => {
    setServiceToEdit(srv);
    setIsFormModalOpen(true);
  };

  const handleOpenDeleteModal = (srv: Service) => {
    setServiceToDelete(srv);
    setIsDeleteModalOpen(true);
  };

  const projectName = project ? project.name : projectId;

  return (
    <div className="space-y-6 max-w-7xl mx-auto text-xs pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-borderColor pb-3">
        <div>
          <h1 className="text-lg font-bold text-textPrimary font-mono">
            {projectName} — Monitored Services Catalog
          </h1>
          <p className="text-xs text-textSecondary mt-0.5">
            Microservices topology, dependencies, and release history isolated to project <span className="font-mono text-accentPrimary">{projectName}</span>.
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleOpenAddModal}
          className="gap-1.5 font-semibold text-xs shrink-0 font-mono"
        >
          <Plus className="w-4 h-4" />
          <span>Add Service</span>
        </Button>
      </div>

      {isLoading ? (
        <Skeleton className="h-64" />
      ) : services.length === 0 ? (
        <Card className="p-8 text-center space-y-3 border-dashed border-borderColor max-w-lg mx-auto">
          <div className="w-12 h-12 rounded-full bg-bgApp border border-borderColor flex items-center justify-center mx-auto text-textMuted">
            <Server className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-textPrimary text-sm font-mono">No services configured yet</h3>
            <p className="text-textMuted text-xs mt-1">
              Add your first microservice to track health metrics, dependency maps, and releases for project {projectId}.
            </p>
          </div>
          <Button variant="primary" size="sm" onClick={handleOpenAddModal} className="gap-1.5 font-mono">
            <Plus className="w-4 h-4" />
            <span>Add Service</span>
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Services List Column */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-xs text-textPrimary font-mono">
                {projectName} Services ({services.length})
              </h3>
            </div>

            <div className="space-y-2">
              {services.map((srv) => {
                const isSelected = selectedService?.id === srv.id;
                return (
                  <Card
                    key={srv.id}
                    onClick={() => setSelectedService(srv)}
                    className={`p-3.5 cursor-pointer transition-all ${
                      isSelected ? 'border-accentPrimary bg-accentSubtle/10' : 'hover:border-borderColor/80'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold font-mono text-textPrimary text-xs">{srv.name}</span>
                      <Badge variant={badgeMap[srv.health] || 'default'} size="sm">{srv.health}</Badge>
                    </div>

                    <div className="flex items-center justify-between font-mono text-[11px] text-textMuted">
                      <span>Env: {srv.environment || 'Production'}</span>
                      <span className={srv.errorRatePercent > 1 ? 'text-statusDanger font-bold' : ''}>
                        Err: {srv.errorRatePercent}%
                      </span>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Detailed Service Overview */}
          {selectedService && (
            <div className="lg:col-span-2 space-y-4">
              <Card className="p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-borderColor pb-3">
                  <div className="flex items-center gap-3">
                    <Server className="w-5 h-5 text-accentPrimary" />
                    <div>
                      <h2 className="text-base font-bold text-textPrimary font-mono">{selectedService.name}</h2>
                      <p className="text-[11px] text-textMuted">
                        Owner: {selectedService.ownerTeam || 'Platform SRE'} • Type: {selectedService.type || 'Backend'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Badge variant={badgeMap[selectedService.health]}>{selectedService.health}</Badge>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleOpenEditModal(selectedService)}
                      className="gap-1 text-[11px] h-7 px-2"
                    >
                      <Edit2 className="w-3 h-3" />
                      <span>Edit</span>
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleOpenDeleteModal(selectedService)}
                      className="gap-1 text-[11px] h-7 px-2"
                    >
                      <Trash2 className="w-3 h-3" />
                      <span>Delete</span>
                    </Button>
                  </div>
                </div>

                {selectedService.description && (
                  <p className="text-xs text-textSecondary leading-relaxed">{selectedService.description}</p>
                )}

                <div className="grid grid-cols-2 gap-3 font-mono text-xs">
                  <div className="p-3 bg-bgApp border border-borderColor rounded">
                    <span className="text-[10px] text-textMuted block">Error Rate</span>
                    <span
                      className={`text-base font-bold ${
                        selectedService.errorRatePercent > 1 ? 'text-statusDanger' : 'text-statusSuccess'
                      }`}
                    >
                      {selectedService.errorRatePercent}%
                    </span>
                  </div>
                  <div className="p-3 bg-bgApp border border-borderColor rounded">
                    <span className="text-[10px] text-textMuted block">Active Incidents</span>
                    <span className="text-base font-bold text-statusWarning">{selectedService.recentIncidentsCount}</span>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-xs text-textPrimary mb-2 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-accentPrimary" />
                    <span>Service Topology Dependencies</span>
                  </h4>
                  {selectedService.dependencies.length === 0 ? (
                    <p className="text-textMuted text-[11px] italic font-mono">No external dependencies linked.</p>
                  ) : (
                    <div className="flex flex-wrap gap-2 font-mono">
                      {selectedService.dependencies.map((dep) => (
                        <span
                          key={dep.id}
                          className="px-2.5 py-1 bg-bgApp border border-borderColor rounded text-xs text-textPrimary flex items-center gap-1.5"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-accentPrimary" />
                          <span>{dep.name}</span>
                          <span className="text-[10px] text-textMuted">({dep.type})</span>
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div>
                  <h4 className="font-semibold text-xs text-textPrimary mb-2 flex items-center gap-1.5">
                    <GitCommit className="w-3.5 h-3.5 text-accentPrimary" />
                    <span>Recent Deployments ({projectName})</span>
                  </h4>
                  {selectedService.recentDeployments.length === 0 ? (
                    <p className="text-textMuted text-[11px] italic font-mono">No recent deployment releases recorded.</p>
                  ) : (
                    <div className="space-y-2 font-mono text-[11px]">
                      {selectedService.recentDeployments.map((d) => (
                        <div key={d.id} className="p-2.5 bg-bgApp border border-borderColor rounded flex items-center justify-between">
                          <div>
                            <span className="font-bold text-accentPrimary">{d.version}</span>
                            <span className="text-textMuted ml-2">by {d.author}</span>
                          </div>
                          <span className="text-textMuted text-[10px]">{d.deployedAt}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            </div>
          )}
        </div>
      )}

      {/* Service Form Modal (Create / Edit) */}
      <ServiceFormModal
        isOpen={isFormModalOpen}
        projectId={projectId}
        serviceToEdit={serviceToEdit}
        onClose={() => setIsFormModalOpen(false)}
        onSuccess={fetchServices}
      />

      {/* Delete Service Confirmation Modal */}
      {serviceToDelete && (
        <DeleteServiceModal
          isOpen={isDeleteModalOpen}
          service={serviceToDelete}
          projectId={projectId}
          projectName={projectName}
          onClose={() => setIsDeleteModalOpen(false)}
          onSuccess={fetchServices}
        />
      )}
    </div>
  );
}
