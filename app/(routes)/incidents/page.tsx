'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

export default function IncidentsRedirect() {
  const router = useRouter();

  useEffect(() => {
    api
      .getProjects()
      .then((projects) => {
        if (projects && projects.length > 0) {
          router.replace(`/projects/${projects[0].slug || projects[0].id}/incidents`);
        } else {
          router.replace('/projects');
        }
      })
      .catch(() => router.replace('/projects'));
  }, [router]);

  return (
    <div className="h-48 flex items-center justify-center text-xs font-mono text-textMuted">
      Loading workspace incidents...
    </div>
  );
}
