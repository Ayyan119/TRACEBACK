'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  UserProfile,
  TECH_ROLES,
  getStoredUserProfile,
  saveStoredUserProfile,
  saveStoredUserId,
  getStoredUserId,
} from '@/lib/userProfile';
import { api } from '@/lib/api';
import { User, Key, ShieldCheck, Eye, EyeOff, X, Check, Users, RefreshCw } from 'lucide-react';

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
  const [name, setName] = useState('');
  const [role, setRole] = useState(TECH_ROLES[0]);
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [hasExistingKey, setHasExistingKey] = useState(false);
  const [isUpdatingKey, setIsUpdatingKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [allUsers, setAllUsers] = useState<any[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (isOpen) {
      const current = getStoredUserProfile();
      setName(current.name || '');
      setRole(current.role || TECH_ROLES[0]);
      setSelectedUserId(getStoredUserId());
      setIsUpdatingKey(false);
      setApiKey('');
      setErrorMsg('');

      // Sync user info from backend
      api.getUserMe()
        .then((userRes) => {
          if (userRes) {
            setName(userRes.name);
            setRole(userRes.role);
            setHasExistingKey(!!userRes.has_openai_api_key);
            saveStoredUserId(userRes.id);
            saveStoredUserProfile({
              id: userRes.id,
              name: userRes.name,
              role: userRes.role,
              hasOpenAiApiKey: userRes.has_openai_api_key,
              maskedApiKey: userRes.masked_api_key,
            });
          }
        })
        .catch(() => {});

      // Fetch all users for multi-user testing switcher
      api.getAllUsers()
        .then((users) => setAllUsers(users || []))
        .catch(() => setAllUsers([]));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !role.trim()) {
      setErrorMsg('Please provide a valid name and technical role.');
      return;
    }

    setIsSaving(true);
    setErrorMsg('');

    try {
      const payloadKey = isUpdatingKey || !hasExistingKey ? apiKey : undefined;
      const res = await api.saveUserProfile(name.trim(), role.trim(), payloadKey);

      if (res) {
        saveStoredUserId(res.id);
        saveStoredUserProfile({
          id: res.id,
          name: res.name,
          role: res.role,
          hasOpenAiApiKey: res.has_openai_api_key,
          maskedApiKey: res.masked_api_key,
        });
      }
      setIsSaving(false);
      onClose();
      // Reload page to re-fetch project listings scoped to updated identity
      window.location.reload();
    } catch (err: any) {
      console.error('Failed to save profile:', err);
      setErrorMsg(err?.message || 'Failed to save profile identity.');
      setIsSaving(false);
    }
  };

  const handleSwitchUser = (targetUser: any) => {
    saveStoredUserId(targetUser.id);
    saveStoredUserProfile({
      id: targetUser.id,
      name: targetUser.name,
      role: targetUser.role,
      hasOpenAiApiKey: targetUser.has_openai_api_key,
      maskedApiKey: targetUser.masked_api_key,
    });
    window.location.reload();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <Card className="w-full max-w-lg bg-surface border-borderColor shadow-2xl overflow-hidden flex flex-col font-mono text-xs">
        {/* Header */}
        <div className="p-4 border-b border-borderColor flex items-center justify-between bg-surfaceHighlight/30">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-accent/10 border border-accent/20 text-accent">
              <User className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-textPrimary font-mono">
                {isFirstTime ? 'Welcome to TRACEBACK' : 'User Profile & Identity'}
              </h2>
              <p className="text-[11px] text-textSecondary font-sans">
                {isFirstTime
                  ? 'Set up your engineer profile to isolate workspaces & key credentials.'
                  : 'Manage your active SRE identity and OpenAI API key settings.'}
              </p>
            </div>
          </div>
          {!isFirstTime && (
            <button
              onClick={onClose}
              className="p-1.5 text-textSecondary hover:text-textPrimary rounded-md hover:bg-surfaceHighlight transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <form onSubmit={handleSave} className="p-5 space-y-4">
          {errorMsg && (
            <div className="p-3 rounded-md bg-accentRed/10 border border-accentRed/30 text-accentRed text-xs font-sans">
              {errorMsg}
            </div>
          )}

          {/* Name Field */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-textPrimary">
              Engineer Name <span className="text-accentRed">*</span>
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Ayyan Shahid"
              className="w-full px-3 py-2 bg-background border border-borderColor rounded-md text-textPrimary placeholder:text-textSecondary/50 focus:outline-none focus:border-accent text-xs font-sans"
            />
          </div>

          {/* Role Field */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-textPrimary">
              Technical Role <span className="text-accentRed">*</span>
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-3 py-2 bg-background border border-borderColor rounded-md text-textPrimary focus:outline-none focus:border-accent text-xs font-sans"
            >
              {TECH_ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>

          {/* OpenAI API Key Field */}
          <div className="space-y-2 pt-2 border-t border-borderColor/60">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-1.5 text-xs font-semibold text-textPrimary">
                <Key className="w-3.5 h-3.5 text-accentYellow" />
                <span>OpenAI API Key</span>
              </label>
              {hasExistingKey && !isUpdatingKey && (
                <Badge variant="success" className="gap-1 font-mono text-[10px]">
                  <ShieldCheck className="w-3 h-3" />
                  <span>Encrypted at Rest</span>
                </Badge>
              )}
            </div>

            {hasExistingKey && !isUpdatingKey ? (
              <div className="flex items-center justify-between p-2.5 bg-background/80 border border-borderColor rounded-md">
                <div className="font-mono text-textSecondary text-xs">
                  ••••••••••••••••••••••••••••••••
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsUpdatingKey(true)}
                  className="h-7 px-2.5 text-[11px] font-mono text-accent"
                >
                  Update API Key
                </Button>
              </div>
            ) : (
              <div className="space-y-1.5">
                <div className="relative">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-proj-..."
                    className="w-full pl-3 pr-10 py-2 bg-background border border-borderColor rounded-md text-textPrimary placeholder:text-textSecondary/50 focus:outline-none focus:border-accent text-xs font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-textSecondary hover:text-textPrimary"
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-[10px] text-textSecondary font-sans">
                  Key is encrypted with server-side Fernet encryption and never exposed in browser storage or logs.
                </p>
              </div>
            )}
          </div>

          {/* Multi-User Identity Switcher (Dev Mode) */}
          {allUsers.length > 1 && (
            <div className="pt-3 border-t border-borderColor/60 space-y-2">
              <div className="flex items-center justify-between text-[11px] font-semibold text-textSecondary">
                <span className="flex items-center gap-1.5 font-mono">
                  <Users className="w-3.5 h-3.5 text-accent" />
                  <span>Switch User Identity (Dev Multi-Tenant Test)</span>
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {allUsers.map((u) => (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => handleSwitchUser(u)}
                    className={`p-2 rounded-md border text-left flex items-center justify-between transition-colors ${
                      u.id === selectedUserId
                        ? 'border-accent bg-accent/10 text-textPrimary font-bold'
                        : 'border-borderColor bg-background hover:bg-surfaceHighlight text-textSecondary'
                    }`}
                  >
                    <div className="truncate">
                      <div className="font-mono text-xs truncate">{u.name}</div>
                      <div className="text-[10px] text-textSecondary truncate">{u.role}</div>
                    </div>
                    {u.id === selectedUserId && <Check className="w-3.5 h-3.5 text-accent shrink-0" />}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Footer Actions */}
          <div className="pt-3 border-t border-borderColor flex items-center justify-end gap-2">
            {!isFirstTime && (
              <Button type="button" variant="outline" size="sm" onClick={onClose}>
                Cancel
              </Button>
            )}
            <Button type="submit" variant="primary" size="sm" disabled={isSaving} className="gap-1.5 font-semibold font-mono">
              {isSaving ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>{isFirstTime ? 'Save & Continue' : 'Save Changes'}</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
