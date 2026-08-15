import { formatDistanceToNow, parseISO, format } from 'date-fns';

export function formatTimeAgo(isoString: string): string {
  try {
    return formatDistanceToNow(parseISO(isoString), { addSuffix: true });
  } catch {
    return isoString;
  }
}

export function formatDate(isoString: string, formatStr: string = 'MMM d, yyyy HH:mm:ss'): string {
  try {
    return format(parseISO(isoString), formatStr);
  } catch {
    return isoString;
  }
}

export function formatBytes(bytes?: number): string {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}
