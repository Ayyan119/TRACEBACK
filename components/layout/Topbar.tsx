'use client';

import React, { useState, useEffect } from 'react';
import { ProjectSelector } from './ProjectSelector';
import { GlobalSearch } from './GlobalSearch';
import { ThemeToggle } from './ThemeToggle';
import { Search, Edit2 } from 'lucide-react';
import {
  UserProfile,
  DEFAULT_USER_PROFILE,
  getStoredUserProfile,
  isFirstTimeUser,
  getInitials,
} from '@/lib/userProfile';
import { UserProfileModal } from '@/components/user/UserProfileModal';
import { CreateProjectModal } from '@/components/projects/CreateProjectModal';
import { useRouter } from 'next/navigation';

export const Topbar: React.FC = () => {
  const router = useRouter();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile>(DEFAULT_USER_PROFILE);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isCreateProjectModalOpen, setIsCreateProjectModalOpen] = useState(false);
  const [isFirstTime, setIsFirstTime] = useState(false);
  const [mounted, setMounted] = useState(false);

  const syncProfile = () => {
    setUserProfile(getStoredUserProfile());
  };

  useEffect(() => {
    setMounted(true);
    syncProfile();

    if (isFirstTimeUser()) {
      setIsFirstTime(true);
      setIsProfileModalOpen(true);
    }

    const handleProfileUpdate = () => syncProfile();
    const handleOpenProfileModal = () => {
      setIsFirstTime(false);
      setIsProfileModalOpen(true);
    };
    const handleOpenCreateProjectModal = () => {
      setIsCreateProjectModalOpen(true);
    };

    window.addEventListener('tb_user_profile_updated', handleProfileUpdate);
    window.addEventListener('tb_open_profile_modal', handleOpenProfileModal);
    window.addEventListener('tb_open_create_project_modal', handleOpenCreateProjectModal);

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('tb_user_profile_updated', handleProfileUpdate);
      window.removeEventListener('tb_open_profile_modal', handleOpenProfileModal);
      window.removeEventListener('tb_open_create_project_modal', handleOpenCreateProjectModal);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const initials = getInitials(userProfile.name);

  return (
    <header className="h-14 bg-bgSurface border-b border-borderColor px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-4">
        <ProjectSelector />

        {/* Global Search Bar trigger button */}
        <button
          onClick={() => setIsSearchOpen(true)}
          className="flex items-center gap-3 px-3 py-1.5 rounded-md bg-bgApp hover:bg-bgSurfaceHover border border-borderColor text-xs text-textMuted transition-colors w-64 justify-between"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-accentPrimary" />
            <span className="font-sans text-[11px]">Search workspace...</span>
          </div>
          <kbd className="px-1.5 py-0.5 rounded bg-bgSurface border border-borderColor text-[10px] font-mono text-textMuted">
            ⌘K
          </kbd>
        </button>

        <GlobalSearch isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />

        <div className="h-4 w-px bg-borderColor mx-0.5" />

        {/* Profile Button (Click to edit) */}
        <button
          onClick={() => {
            setIsFirstTime(false);
            setIsProfileModalOpen(true);
          }}
          title="Click to edit engineer profile"
          className="flex items-center gap-2.5 px-2.5 py-1 rounded-lg bg-bgApp hover:bg-bgSurfaceHover border border-borderColor hover:border-accentPrimary/50 transition-all cursor-pointer group shadow-2xs"
        >
          <div className="relative">
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-accentPrimary/30 to-accentPrimary/10 border border-accentPrimary/40 flex items-center justify-center text-accentPrimary font-mono text-xs font-bold shadow-xs group-hover:scale-105 transition-transform">
              {initials}
            </div>
            <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-emerald-400 border border-bgSurface" />
          </div>

          <div className="text-left hidden lg:block">
            <div className="flex items-center gap-1.5 leading-none">
              <span className="font-semibold text-textPrimary text-xs group-hover:text-accentPrimary transition-colors">
                {userProfile.name}
              </span>
              <Edit2 className="w-2.5 h-2.5 text-textMuted opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <p className="text-[10px] text-textMuted font-mono leading-none mt-1 tracking-tight">
              {userProfile.role}
            </p>
          </div>
        </button>

        {/* Profile & Create Project Modals */}
        {mounted && (
          <>
            <UserProfileModal
              isOpen={isProfileModalOpen}
              isFirstTime={isFirstTime}
              onClose={() => {
                setIsProfileModalOpen(false);
                setIsFirstTime(false);
              }}
            />
            <CreateProjectModal
              isOpen={isCreateProjectModalOpen}
              onClose={() => setIsCreateProjectModalOpen(false)}
              onSuccess={(newId) => {
                setIsCreateProjectModalOpen(false);
                router.push(`/projects/${newId}`);
              }}
            />
          </>
        )}
      </div>
    </header>
  );
};
