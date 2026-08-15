import React from 'react';
import { cn } from '@/lib/utils/cn';

export const Skeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => {
  return <div className={cn('animate-pulse rounded bg-bgSurfaceHover/80', className)} {...props} />;
};
