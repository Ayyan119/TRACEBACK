import React from 'react';
import { IncidentSeverity } from '@/types';
import { Badge } from '@/components/ui/Badge';

export const SeverityBadge: React.FC<{ severity: IncidentSeverity }> = ({ severity }) => {
  const map: Record<IncidentSeverity, 'danger' | 'warning' | 'info' | 'default'> = {
    Critical: 'danger',
    High: 'danger',
    Medium: 'warning',
    Low: 'info',
  };

  return <Badge variant={map[severity] || 'default'}>{severity}</Badge>;
};
