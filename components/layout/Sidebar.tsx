'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { Project } from '@/types';
import { CreateProjectModal } from '@/components/projects/CreateProjectModal';
import { UserProfileModal } from '@/components/user/UserProfileModal';
import {
  UserProfile,
  DEFAULT_USER_PROFILE,
  getStoredUserProfile,
  getInitials,
} from '@/lib/userProfile';
import {
  LayoutDashboard,
  AlertTriangle,
  Server,
  BookOpen,
  Settings,
  FolderGit2,
  Plus,
  ArrowRight,
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const params = useParams();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile>(DEFAULT_USER_PROFILE);
  const [mounted, setMounted] = useState(false);

  // Current active project ID
  let currentProjectId = (params?.projectId as string) || '';
  if (!currentProjectId && pathname) {
    const match = pathname.match(/\/projects\/([^\/]+)/);
    if (match) currentProjectId = match[1];
  }
  if (['incidents', 'services', 'knowledge', 'settings', 'new'].includes(currentProjectId)) {
    currentProjectId = projects.length > 0 ? (projects[0].slug || projects[0].id) : '';
  }
  if (!currentProjectId && projects.length > 0) {
    currentProjectId = projects[0].slug || projects[0].id;
  }

  const fetchProjects = async () => {
    try {
      const data = await api.getProjects();
      setProjects(data || []);
    } catch {
      setProjects([]);
    }
  };

  const syncProfile = () => {
    setUserProfile(getStoredUserProfile());
  };

  useEffect(() => {
    setMounted(true);
    fetchProjects();
    syncProfile();

    const handleUpdate = () => {
      syncProfile();
      fetchProjects();
    };
    window.addEventListener('tb_user_profile_updated', handleUpdate);
    return () => window.removeEventListener('tb_user_profile_updated', handleUpdate);
  }, []);

  const navItems = [
    {
      name: 'Overview',
      href: currentProjectId ? `/projects/${currentProjectId}` : '/projects',
      icon: LayoutDashboard,
    },
    {
      name: 'Incidents',
      href: currentProjectId ? `/projects/${currentProjectId}/incidents` : '/incidents',
      icon: AlertTriangle,
    },
    {
      name: 'Services',
      href: currentProjectId ? `/projects/${currentProjectId}/services` : '/services',
      icon: Server,
    },
    {
      name: 'Knowledge',
      href: currentProjectId ? `/projects/${currentProjectId}/knowledge` : '/knowledge',
      icon: BookOpen,
    },
    {
      name: 'Settings',
      href: currentProjectId ? `/projects/${currentProjectId}/settings` : '/settings',
      icon: Settings,
    },
  ];

  const initials = getInitials(userProfile.name);

  return (
    <aside className="w-60 bg-bgSurface/90 backdrop-blur-md border-r border-borderColor flex flex-col h-screen sticky top-0 z-40 select-none">
      {/* Brand Header */}
      <div className="h-14 px-4 flex items-center justify-between border-b border-borderColor">
        <Link href={`/projects/${currentProjectId}`} className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-mono font-extrabold text-sm shadow-md shadow-blue-500/25 group-hover:scale-105 transition-transform">
            T
          </div>
          <div>
            <span className="font-bold text-textPrimary font-mono tracking-tight text-sm bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">TRACEBACK</span>
            <span className="text-[9px] text-textMuted font-mono block leading-none">v1.0.4 • SRE Engine</span>
          </div>
        </Link>
      </div>

      {/* Main Navigation Links */}
      <div className="p-3 space-y-1">
        <div className="px-2.5 py-1 text-[10px] uppercase font-mono font-semibold text-textMuted tracking-wider">
          Workspace Navigation
        </div>
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.name !== 'Overview' && pathname.startsWith(item.href));
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-2.5 px-3 py-2 rounded-md text-xs transition-all duration-150 font-sans',
                isActive
                  ? 'bg-accentSubtle/80 text-accentPrimary font-semibold border-l-2 border-accentPrimary shadow-xs'
                  : 'text-textSecondary hover:text-textPrimary hover:bg-bgSurfaceHover/80'
              )}
            >
              <Icon className={cn('w-4 h-4 shrink-0', isActive ? 'text-accentPrimary' : 'text-textMuted')} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Active Workspaces List */}
      <div className="px-3 pt-3 space-y-1 flex-1 flex flex-col min-h-0">
        <div className="flex items-center justify-between px-2.5 py-1 shrink-0">
          <span className="text-[10px] uppercase font-mono font-semibold text-textMuted tracking-wider">
            Active Workspace
          </span>
          <button
            onClick={() => window.dispatchEvent(new Event('tb_open_create_project_modal'))}
            className="text-accentPrimary hover:text-accentHover p-1 rounded hover:bg-accentSubtle transition-colors"
            title="Create New Project"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="space-y-1 flex-1 overflow-y-auto pr-1 min-h-0">
          {projects.map((p) => {
            const isSelected = p.id === currentProjectId || p.slug === currentProjectId;
            return (
              <Link
                key={p.id}
                href={`/projects/${p.slug || p.id}`}
                className={cn(
                  'flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs transition-all font-mono',
                  isSelected
                    ? 'bg-bgApp border border-borderColor font-bold text-textPrimary shadow-xs'
                    : 'text-textMuted hover:text-textSecondary hover:bg-bgSurfaceHover/50'
                )}
              >
                <div className="flex items-center gap-2 truncate">
                  <span className={cn('w-1.5 h-1.5 rounded-full shrink-0', isSelected ? 'bg-statusSuccess shadow-[0_0_8px_rgba(16,185,129,0.6)]' : 'bg-borderColor')} />
                  <span className="truncate">{p.name}</span>
                </div>
                <span className="text-[9px] text-textMuted font-sans shrink-0 uppercase tracking-tight">{p.environment}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Bottom Footer Section: Projects Directory Button */}
      <div className="p-3 border-t border-borderColor shrink-0">
        <Link
          href="/projects"
          className={cn(
            'flex items-center justify-between w-full px-3 py-2 rounded-lg text-xs font-mono transition-all border shadow-xs',
            pathname === '/projects'
              ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-500/20 font-bold'
              : 'bg-bgApp text-textSecondary border-borderColor hover:text-textPrimary hover:bg-bgSurfaceHover/80'
          )}
        >
          <div className="flex items-center gap-2">
            <FolderGit2 className="w-4 h-4 text-accentPrimary" />
            <span>Projects Directory</span>
          </div>
          <ArrowRight className="w-3.5 h-3.5 opacity-70" />
        </Link>
      </div>
    </aside>
  );
};
