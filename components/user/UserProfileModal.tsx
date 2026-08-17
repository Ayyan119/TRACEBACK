'use client';

import React, { useState, useEffect } from 'react';
import {
  UserProfile,
  getStoredUserProfile,
  saveStoredUserProfile,
  TECH_ROLES,
  getInitials,
} from '@/lib/userProfile';
import { Button } from '@/components/ui/Button';
import { User, Briefcase, Sparkles, X, Check } from 'lucide-react';

interface UserProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
  isFirstTime?: boolean;
}

export const UserProfileModal: React.FC<UserProfileModalProps> = ({
  isOpen,
  onClose,
  isFirstTime = false,
}) => {
  const [name, setName] = useState('Ayyan Shahid');
  const [roleSelect, setRoleSelect] = useState('Senior Software Engineer');
  const [customRole, setCustomRole] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      const current = getStoredUserProfile();
      setName(current.name);
      if (TECH_ROLES.includes(current.role) && current.role !== 'Custom Role...') {
        setRoleSelect(current.role);
        setCustomRole('');
      } else {
        setRoleSelect('Custom Role...');
        setCustomRole(current.role);
      }
      setError(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Please enter your name.');
      return;
    }
    const finalRole = roleSelect === 'Custom Role...' ? customRole.trim() : roleSelect;
    if (!finalRole) {
      setError('Please select or specify your tech profession / role.');
      return;
    }
    saveStoredUserProfile({
      name: name.trim(),
      role: finalRole,
    });
    onClose();
  };

  const initials = getInitials(name);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-bgSurface border border-borderColor rounded-lg w-full max-w-md p-5 space-y-5 shadow-2xl animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-borderColor pb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accentPrimary" />
            <h3 className="text-sm font-bold text-textPrimary font-mono">
              {isFirstTime ? 'Welcome to TRACEBACK — Setup Profile' : 'Edit User Profile'}
            </h3>
          </div>
          <button
            onClick={() => {
              if (isFirstTime && typeof window !== 'undefined') {
                localStorage.setItem('tb_user_setup_completed', 'true');
              }
              onClose();
            }}
            className="text-textMuted hover:text-textPrimary p-1 rounded transition-colors"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {isFirstTime && (
          <p className="text-xs text-textSecondary leading-relaxed">
            Welcome to TRACEBACK AI SRE Engine. Please enter your name and select your tech profession to customize your workspace environment.
          </p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Avatar Preview & Name Input */}
          <div className="flex items-center gap-3 bg-bgApp p-3 rounded-lg border border-borderColor">
            <div className="w-10 h-10 rounded-full bg-accentPrimary/20 border border-accentPrimary/50 flex items-center justify-center text-accentPrimary font-mono font-bold text-sm shrink-0">
              {initials}
            </div>
            <div className="flex-1">
              <label className="block text-[11px] font-mono text-textMuted mb-1">
                Full Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Ayyan Shahid"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-bgSurface border border-borderColor rounded px-2.5 py-1.5 text-xs text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentPrimary font-mono"
              />
            </div>
          </div>

          {/* Profession Selection */}
          <div className="space-y-2">
            <label className="block text-[11px] font-mono text-textSecondary flex items-center gap-1.5">
              <Briefcase className="w-3.5 h-3.5 text-accentPrimary" />
              <span>Tech Profession / Role *</span>
            </label>
            <select
              value={roleSelect}
              onChange={(e) => {
                setRoleSelect(e.target.value);
                if (e.target.value !== 'Custom Role...') {
                  setCustomRole('');
                }
              }}
              className="w-full bg-bgApp border border-borderColor text-textPrimary text-xs rounded px-3 py-2 focus:outline-none focus:border-accentPrimary font-mono cursor-pointer"
            >
              {TECH_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>

            {roleSelect === 'Custom Role...' && (
              <input
                type="text"
                required
                placeholder="Write custom role (e.g. AI Engineer, Gen AI Engineer)"
                value={customRole}
                onChange={(e) => setCustomRole(e.target.value)}
                className="w-full bg-bgSurface border border-borderColor rounded px-3 py-2 text-xs text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-accentPrimary font-mono"
              />
            )}
          </div>

          {error && <p className="text-statusDanger text-xs font-mono">{error}</p>}

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2 border-t border-borderColor">
            {!isFirstTime && (
              <Button type="button" variant="ghost" onClick={onClose}>
                Cancel
              </Button>
            )}
            <Button type="submit" variant="primary" className="gap-1.5 font-mono text-xs">
              <Check className="w-3.5 h-3.5" />
              <span>{isFirstTime ? 'Complete Setup' : 'Save Changes'}</span>
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
