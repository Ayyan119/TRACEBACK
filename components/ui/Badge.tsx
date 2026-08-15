import React from 'react';
import { cn } from '@/lib/utils/cn';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'confidence' | 'outline';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = 'default',
  size = 'md',
  ...props
}) => {
  // Operational status label shape (small radius, compact dimensions, no large pills)
  const base = 'inline-flex items-center font-mono font-medium rounded tracking-wide uppercase border shrink-0';

  const variants = {
    default: 'bg-bgSurfaceHover text-textSecondary border-borderColor',
    success: 'bg-[var(--badge-healthy-bg)] text-[var(--badge-healthy-text)] border-[var(--badge-healthy-border)]',
    warning: 'bg-[var(--badge-warning-bg)] text-[var(--badge-warning-text)] border-[var(--badge-warning-border)]',
    danger: 'bg-[var(--badge-critical-bg)] text-[var(--badge-critical-text)] border-[var(--badge-critical-border)]',
    info: 'bg-[var(--badge-info-bg)] text-[var(--badge-info-text)] border-[var(--badge-info-border)]',
    confidence: 'bg-[var(--badge-confidence-bg)] text-[var(--badge-confidence-text)] border-[var(--badge-confidence-border)]',
    outline: 'border-borderColor text-textSecondary bg-transparent',
  };

  const sizes = {
    sm: 'px-1.5 py-0.5 text-[9px]',
    md: 'px-2 py-0.5 text-[10px]',
  };

  return (
    <span className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
};
