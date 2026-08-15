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
  Edit2,
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const params = useParams();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile>(DEFAULT_USER_PROFILE);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
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
    const data = await api.getProjects().catch(() => []);
    setProjects(data);
  };

  const syncProfile = () => {
    setUserProfile(getStoredUserProfile());
  };

  useEffect(() => {
    setMounted(true);
    fetchProjects();
    syncProfile();

    const handleProfileUpdate = () => syncProfile();
    window.addEventListener('tb_user_profile_updated', handleProfileUpdate);
    return () => window.removeEventListener('tb_user_profile_updated', handleProfileUpdate);
  }, [currentProjectId]);

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
    <aside className="w-60 bg-bgSurface border-r border-borderColor flex flex-col h-screen sticky top-0 z-40 select-none">
      {/* Brand Header */}
      <div className="h-14 px-4 flex items-center justify-between border-b border-borderColor">
        <Link href={`/projects/${currentProjectId}`} className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded bg-accentPrimary flex items-center justify-center text-white font-mono font-bold text-sm shadow-md group-hover:scale-105 transition-transform">
            T
          </div>
          <div>
            <span className="font-bold text-textPrimary font-mono tracking-tight text-sm">TRACEBACK</span>
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
                'flex items-center gap-2.5 px-2.5 py-2 rounded text-xs transition-colors font-sans',
                isActive
                  ? 'bg-accentSubtle text-accentPrimary font-semibold'
                  : 'text-textSecondary hover:text-textPrimary hover:bg-bgSurfaceHover'
              )}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Active Workspaces List */}
      <div className="px-3 pt-3 space-y-1">
        <div className="flex items-center justify-between px-2.5 py-1">
          <span className="text-[10px] uppercase font-mono font-semibold text-textMuted tracking-wider">
            Active Workspace
          </span>
          <button
            onClick={() => window.dispatchEvent(new Event('tb_open_create_project_modal'))}
            className="text-accentPrimary hover:text-accentPrimary/80 p-0.5"
            title="Create New Project"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="space-y-0.5 max-h-40 overflow-y-auto pr-1">
          {projects.map((p) => {
            const isSelected = p.id === currentProjectId || p.slug === currentProjectId;
            return (
              <Link
                key={p.id}
                href={`/projects/${p.slug || p.id}`}
                className={cn(
                  'flex items-center justify-between px-2.5 py-1.5 rounded text-xs transition-colors font-mono',
                  isSelected
                    ? 'bg-bgSurface border border-borderColor font-bold text-textPrimary'
                    : 'text-textMuted hover:text-textSecondary hover:bg-bgSurfaceHover/40'
                )}
              >
                <div className="flex items-center gap-2 truncate">
                  <span className={cn('w-2 h-2 rounded-full shrink-0', isSelected ? 'bg-statusSuccess' : 'bg-borderColor')} />
                  <span className="truncate">{p.name}</span>
                </div>
                <span className="text-[10px] text-textMuted font-sans shrink-0">{p.environment}</span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Bottom Profile Footer (Click to edit profile) */}
      <div className="mt-auto p-3 border-t border-borderColor">
        <button
          onClick={() => window.dispatchEvent(new Event('tb_open_profile_modal'))}
          title="Click to edit engineer profile"
          className="w-full text-left flex items-center justify-between p-2 rounded-lg bg-bgApp hover:bg-bgSurfaceHover border border-borderColor hover:border-accentPrimary/50 transition-all cursor-pointer group"
        >
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="relative shrink-0">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accentPrimary/30 to-accentPrimary/10 border border-accentPrimary/40 flex items-center justify-center font-mono font-bold text-xs text-accentPrimary group-hover:scale-105 transition-transform shadow-xs">
                {initials}
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 border border-bgSurface" />
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold text-textPrimary leading-none flex items-center gap-1 truncate group-hover:text-accentPrimary transition-colors">
                <span className="truncate">{userProfile.name}</span>
                <Edit2 className="w-2.5 h-2.5 text-textMuted opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
              </p>
              <p className="text-[10px] text-textMuted font-mono leading-none mt-1 truncate">{userProfile.role}</p>
            </div>
          </div>
        </button>
      </div>
    </aside>
  );
};
