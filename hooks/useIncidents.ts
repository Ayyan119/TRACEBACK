import { useState, useEffect, useCallback } from 'react';
import { Incident } from '@/types';
import { api } from '@/lib/api';

export function useIncidents(params?: {
  projectId?: string;
  serviceId?: string;
  severity?: string;
  status?: string;
}) {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIncidents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getIncidents(params);
      setIncidents(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch incidents');
    } finally {
      setIsLoading(false);
    }
  }, [params?.projectId, params?.serviceId, params?.severity, params?.status]);

  useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  return { incidents, isLoading, error, refetch: fetchIncidents };
}
