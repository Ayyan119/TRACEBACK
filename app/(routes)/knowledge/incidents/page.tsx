'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { KnowledgeDocument } from '@/types';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { History, ArrowLeft } from 'lucide-react';
import { Skeleton } from '@/components/ui/Skeleton';

export default function KnowledgeIncidentsPage() {
  const [postMortems, setPostMortems] = useState<KnowledgeDocument[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.getKnowledge({ type: 'post_mortem' }).then((data) => {
      setPostMortems(data);
      setIsLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <Link href="/knowledge" className="inline-flex items-center gap-1.5 text-xs text-textSecondary hover:text-textPrimary">
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Knowledge Base</span>
      </Link>

      <div className="border-b border-borderColor pb-4">
        <h1 className="text-xl font-bold text-textPrimary">Closed Incident Post-Mortems Archive</h1>
        <p className="text-xs text-textSecondary mt-1">Vector indexed historical outages and verified resolutions.</p>
      </div>

      {isLoading ? (
        <Skeleton className="h-48" />
      ) : (
        <div className="space-y-3">
          {postMortems.map((doc) => (
            <Card key={doc.id} className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <History className="w-5 h-5 text-accentPrimary" />
                <div>
                  <h3 className="font-semibold text-xs text-textPrimary font-mono">{doc.name}</h3>
                  <p className="text-[11px] text-textSecondary mt-0.5">{doc.summary}</p>
                </div>
              </div>
              <Badge variant="success">Resolved</Badge>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
