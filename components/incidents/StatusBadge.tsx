import React from 'react';
import { IncidentStatus } from '@/types';
import { Badge } from '@/components/ui/Badge';

export const StatusBadge: React.FC<{ status: IncidentStatus }> = ({ status }) => {
  const map: Record<IncidentStatus, 'danger' | 'warning' | 'info' | 'success' | 'default'> = {
    Investigating: 'info',
    Identified: 'warning',
    Monitoring: 'info',
    Resolved: 'success',
  };

  return <Badge variant={map[status] || 'default'}>{status}</Badge>;
};
