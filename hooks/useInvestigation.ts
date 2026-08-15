import { useState, useEffect, useCallback } from 'react';
import { Investigation } from '@/types';
import { api } from '@/lib/api';

export function useInvestigation(incidentId: string) {
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isTriggering, setIsTriggering] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInvestigation = useCallback(async () => {
    if (!incidentId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getInvestigation(incidentId);
      setInvestigation(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to fetch investigation state');
    } finally {
      setIsLoading(false);
    }
  }, [incidentId]);

  const startInvestigation = async (options?: { forceRestart?: boolean }) => {
    setIsTriggering(true);
    setError(null);
    try {
      const data = await api.startInvestigation(incidentId, options);
      setInvestigation(data);
      return data;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start investigation';
      setError(msg);
      throw err;
    } finally {
      setIsTriggering(false);
    }
  };

  useEffect(() => {
    fetchInvestigation();
  }, [fetchInvestigation]);

  return {
    investigation,
    isLoading,
    isTriggering,
    error,
    refetch: fetchInvestigation,
    startInvestigation,
  };
}
