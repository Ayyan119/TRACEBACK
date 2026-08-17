'use client';

import React, { useState, useEffect } from 'react';
import { ProjectSelector } from './ProjectSelector';
import { GlobalSearch } from './GlobalSearch';
import { ThemeToggle } from './ThemeToggle';
import { Search } from 'lucide-react';
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

        {/* User Identity Profile Button */}
        {mounted && (
          <button
            onClick={() => {
              setIsFirstTime(false);
              setIsProfileModalOpen(true);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-bgApp hover:bg-bgSurfaceHover border border-borderColor text-xs transition-colors"
            title="Manage User Identity & OpenAI API Key"
          >
            <div className="w-5 h-5 rounded-full bg-accentPrimary/20 text-accentPrimary font-bold text-[10px] flex items-center justify-center font-mono">
              {getInitials(userProfile.name)}
            </div>
            <div className="text-left hidden sm:block">
              <div className="font-mono text-xs text-textPrimary leading-tight font-semibold">
                {userProfile.name}
              </div>
              <div className="text-[10px] text-textMuted leading-tight font-sans">
                {userProfile.role}
              </div>
            </div>
          </button>
        )}

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
