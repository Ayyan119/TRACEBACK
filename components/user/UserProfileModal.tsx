'use client';

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  TECH_ROLES,
  getStoredUserProfile,
  saveStoredUserProfile,
  saveStoredUserId,
  getStoredUserId,
} from '@/lib/userProfile';
import { api } from '@/lib/api';
import { User, Key, ShieldCheck, Eye, EyeOff, X, Check, Users, RefreshCw, Sparkles, UserPlus, ShieldAlert } from 'lucide-react';

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
  const [mounted, setMounted] = useState(false);
  const [mode, setMode] = useState<'preset' | 'new_user'>('preset');
  
  // New / Edit Profile fields
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
    setMounted(true);
  }, []);

  useEffect(() => {
    if (isOpen) {
      const current = getStoredUserProfile();
      setName(current.name || '');
      setRole(current.role || 'AI Engineer');
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

      // Fetch all users for preset identity selection
      api.getAllUsers()
        .then((users) => {
          setAllUsers(users || []);
        })
        .catch(() => setAllUsers([]));
    }
  }, [isOpen]);

  if (!isOpen || !mounted) return null;

  const handleSaveNewUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim() || !role.trim()) {
      setErrorMsg('Please enter a valid engineer name and technical role.');
      return;
    }

    // MANDATORY API KEY CHECK FOR NEW USER REGISTRATION
    if (mode === 'new_user' && (!apiKey || !apiKey.trim())) {
      setErrorMsg('OpenAI API Key is mandatory for new user registration. Please enter your API key.');
      return;
    }

    setIsSaving(true);
    setErrorMsg('');

    try {
      const payloadKey = apiKey.trim() ? apiKey.trim() : undefined;
      // Passing empty target user ID so backend creates a brand new user in DB
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
      window.location.reload();
    } catch (err: any) {
      console.error('Failed to register new user:', err);
      setErrorMsg(err?.message || 'Failed to create new user profile.');
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
    onClose();
    window.location.reload();
  };

  const modalContent = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-[#0F172A] border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden flex flex-col font-sans text-xs text-slate-100 max-h-[85vh]">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/30">
              <User className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white font-mono tracking-tight">
                {isFirstTime ? 'Welcome to TRACEBACK' : 'Select User Identity & API Key'}
              </h2>
              <p className="text-[11px] text-slate-400 font-sans">
                Select preset user identity or enter as a new user with API Key.
              </p>
            </div>
          </div>
          {!isFirstTime && (
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Tab Selection: Preset Accounts vs New User */}
        <div className="p-2.5 bg-slate-950 border-b border-slate-800 flex gap-2 shrink-0">
          <button
            type="button"
            onClick={() => { setMode('preset'); setErrorMsg(''); }}
            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-mono font-semibold transition-all flex items-center justify-center gap-2 ${
              mode === 'preset'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Preset Accounts</span>
          </button>
          <button
            type="button"
            onClick={() => { setMode('new_user'); setErrorMsg(''); }}
            className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-mono font-semibold transition-all flex items-center justify-center gap-2 ${
              mode === 'new_user'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>+ Enter as New User</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 space-y-4 overflow-y-auto flex-1 min-h-0">
          {errorMsg && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-sans flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 shrink-0 text-red-400" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* MODE 1: PRESET ACCOUNTS (Ayyan AI Engineer vs Guest Tester) */}
          {mode === 'preset' && (
            <div className="space-y-3">
              <p className="text-[11px] text-slate-400 font-sans">
                Choose an available demo identity to enter the system using pre-configured ChatGPT API access:
              </p>

              <div className="space-y-2.5">
                {/* Preset 1: Ayyan Shahid (AI Engineer) */}
                <div
                  onClick={() => {
                    const ayyan = allUsers.find((u) => u.name === 'Ayyan Shahid') || {
                      id: 'usr_default_ayyan',
                      name: 'Ayyan Shahid',
                      role: 'AI Engineer',
                      has_openai_api_key: true,
                    };
                    handleSwitchUser(ayyan);
                  }}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between group ${
                    selectedUserId === 'usr_default_ayyan' || name === 'Ayyan Shahid'
                      ? 'border-blue-500 bg-blue-500/15 text-white shadow-md'
                      : 'border-slate-800 bg-slate-900/60 hover:bg-slate-900 hover:border-slate-700 text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center font-mono font-bold text-white shadow-md">
                      AS
                    </div>
                    <div>
                      <div className="font-mono text-xs font-bold text-white flex items-center gap-2">
                        <span>Ayyan Shahid</span>
                        <Badge variant="info" className="text-[9px] font-mono px-1.5 py-0">Preset</Badge>
                      </div>
                      <div className="text-[11px] text-blue-400 font-mono">AI Engineer</div>
                      <div className="text-[10px] text-slate-400 font-sans">Available API Key • Full Access</div>
                    </div>
                  </div>
                  <Button size="sm" variant="primary" className="h-7 text-xs font-mono">
                    Enter System
                  </Button>
                </div>

                {/* Preset 2: Guest Tester (QA / Guest Engineer) */}
                <div
                  onClick={() => {
                    const guest = allUsers.find((u) => u.name === 'Guest Tester') || {
                      id: 'usr_guest_tester',
                      name: 'Guest Tester',
                      role: 'Guest SRE / QA Tester',
                      has_openai_api_key: true,
                    };
                    handleSwitchUser(guest);
                  }}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all flex items-center justify-between group ${
                    name === 'Guest Tester'
                      ? 'border-blue-500 bg-blue-500/15 text-white shadow-md'
                      : 'border-slate-800 bg-slate-900/60 hover:bg-slate-900 hover:border-slate-700 text-slate-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-600 flex items-center justify-center font-mono font-bold text-white shadow-md">
                      GT
                    </div>
                    <div>
                      <div className="font-mono text-xs font-bold text-white flex items-center gap-2">
                        <span>Guest Tester</span>
                        <Badge variant="success" className="text-[9px] font-mono px-1.5 py-0">Guest</Badge>
                      </div>
                      <div className="text-[11px] text-teal-400 font-mono">Guest SRE / QA Tester</div>
                      <div className="text-[10px] text-slate-400 font-sans">Available API Key • Fast Testing</div>
                    </div>
                  </div>
                  <Button size="sm" variant="secondary" className="h-7 text-xs font-mono border-slate-700">
                    Enter System
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* MODE 2: REGISTER NEW USER (Requires mandatory OpenAI API Key) */}
          {mode === 'new_user' && (
            <form onSubmit={handleSaveNewUser} className="space-y-4">
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-[11px] font-sans flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                <div>
                  <span className="font-semibold font-mono block">New User Registration Requirement:</span>
                  To enter the system as a brand new user, you <strong>must provide your OpenAI API key</strong>.
                </div>
              </div>

              {/* Name Input */}
              <div className="space-y-1">
                <label className="block text-[11px] font-medium text-slate-300">
                  Engineer Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. John Doe"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 text-xs font-sans"
                />
              </div>

              {/* Role Dropdown */}
              <div className="space-y-1">
                <label className="block text-[11px] font-medium text-slate-300">
                  Technical Role <span className="text-red-400">*</span>
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700/80 rounded-lg text-white focus:outline-none focus:border-blue-500 text-xs font-sans cursor-pointer"
                >
                  {TECH_ROLES.map((r) => (
                    <option key={r} value={r} className="bg-slate-900 text-white">
                      {r}
                    </option>
                  ))}
                </select>
              </div>

              {/* Mandatory OpenAI API Key Field */}
              <div className="space-y-1.5 pt-2 border-t border-slate-800">
                <label className="flex items-center justify-between text-xs font-mono font-semibold text-amber-400">
                  <span className="flex items-center gap-1.5">
                    <Key className="w-3.5 h-3.5" />
                    <span>OpenAI API Key *</span>
                  </span>
                  <span className="text-[10px] text-red-400 font-sans">Mandatory for New Users</span>
                </label>

                <div className="relative">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    required
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-proj-..."
                    className="w-full pl-3 pr-10 py-2 bg-slate-950 border border-amber-500/50 focus:border-amber-400 rounded-lg text-white placeholder:text-slate-500 focus:outline-none text-xs font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <p className="text-[10px] text-slate-400 font-sans">
                  Key is encrypted with server-side Fernet encryption and saved securely in your user account.
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
                {!isFirstTime && (
                  <Button type="button" variant="outline" size="sm" onClick={onClose} className="border-slate-700 text-slate-300">
                    Cancel
                  </Button>
                )}
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={isSaving || !name.trim() || !apiKey.trim()}
                  className="gap-1.5 font-semibold font-mono bg-gradient-to-r from-blue-600 to-indigo-600 shadow-md shadow-blue-500/25"
                >
                  {isSaving ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Creating Profile...</span>
                    </>
                  ) : (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Save & Enter System</span>
                    </>
                  )}
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
