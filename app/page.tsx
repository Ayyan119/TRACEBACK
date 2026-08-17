'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  TECH_ROLES,
  saveStoredUserProfile,
  saveStoredUserId,
  isFirstTimeUser,
} from '@/lib/userProfile';
import { api } from '@/lib/api';
import { User, Key, Eye, EyeOff, Check, Users, RefreshCw, UserPlus, ShieldAlert, ArrowRight } from 'lucide-react';

export default function RootPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [mode, setMode] = useState<'preset' | 'new_user'>('preset');

  const [name, setName] = useState('');
  const [role, setRole] = useState(TECH_ROLES[0]);
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [allUsers, setAllUsers] = useState<any[]>([]);

  useEffect(() => {
    setMounted(true);
    // Always fetch preset users and display the entry gate on /
    api.getAllUsers()
      .then((users) => setAllUsers(users || []))
      .catch(() => setAllUsers([]));
  }, []);

  if (!mounted) return null;

  const handleSelectPreset = async (presetUser: any) => {
    saveStoredUserId(presetUser.id);
    saveStoredUserProfile({
      id: presetUser.id,
      name: presetUser.name,
      role: presetUser.role,
      hasOpenAiApiKey: presetUser.has_openai_api_key,
      maskedApiKey: presetUser.masked_api_key,
    });
    router.push('/projects');
  };

  const handleRegisterNewUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !role.trim()) {
      setErrorMsg('Please enter a valid engineer name and technical role.');
      return;
    }
    if (!apiKey || !apiKey.trim()) {
      setErrorMsg('OpenAI API Key is mandatory for new user registration.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg('');

    try {
      const res = await api.saveUserProfile(name.trim(), role.trim(), apiKey.trim());
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
      setIsSubmitting(false);
      router.push('/projects');
    } catch (err: any) {
      console.error('Failed to register user:', err);
      setErrorMsg(err?.message || 'Failed to create user profile.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] flex flex-col items-center justify-center p-4 text-slate-100 font-sans relative overflow-hidden">
      {/* Glow background decorations */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-lg bg-[#0F172A] border border-slate-800 rounded-2xl shadow-2xl overflow-hidden z-10 space-y-0">
        {/* Header */}
        <div className="p-6 border-b border-slate-800 bg-slate-900/80 text-center space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-mono font-extrabold text-xl mx-auto shadow-lg shadow-blue-500/30">
            T
          </div>
          <h1 className="text-xl font-bold font-mono tracking-tight text-white bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            TRACEBACK SRE AI Engine
          </h1>
          <p className="text-xs text-slate-400 max-w-xs mx-auto">
            Set up your engineer identity & OpenAI API credentials before entering the workspace.
          </p>
        </div>

        {/* Tab Selection */}
        <div className="p-3 bg-slate-950 border-b border-slate-800 flex gap-2">
          <button
            type="button"
            onClick={() => { setMode('preset'); setErrorMsg(''); }}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-mono font-semibold transition-all flex items-center justify-center gap-2 ${
              mode === 'preset'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Preset Accounts</span>
          </button>
          <button
            type="button"
            onClick={() => { setMode('new_user'); setErrorMsg(''); }}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-mono font-semibold transition-all flex items-center justify-center gap-2 ${
              mode === 'new_user'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            <UserPlus className="w-4 h-4" />
            <span>+ Enter as New User</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-sans flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 shrink-0 text-red-400" />
              <span>{errorMsg}</span>
            </div>
          )}

          {mode === 'preset' ? (
            <div className="space-y-3">
              <p className="text-xs text-slate-400">
                Choose a demo account to enter using pre-configured ChatGPT API access:
              </p>

              <div className="space-y-3">
                {/* Ayyan Shahid */}
                <div
                  onClick={() => {
                    const ayyan = allUsers.find((u) => u.name === 'Ayyan Shahid') || {
                      id: 'usr_default_ayyan',
                      name: 'Ayyan Shahid',
                      role: 'AI Engineer',
                      has_openai_api_key: true,
                    };
                    handleSelectPreset(ayyan);
                  }}
                  className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 hover:border-blue-500 hover:bg-slate-900 transition-all cursor-pointer flex items-center justify-between group shadow-sm"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center font-mono font-bold text-white shadow-md">
                      AS
                    </div>
                    <div>
                      <div className="font-mono text-sm font-bold text-white flex items-center gap-2">
                        <span>Ayyan Shahid</span>
                        <Badge variant="info" className="text-[9px] font-mono px-1.5 py-0">Preset</Badge>
                      </div>
                      <div className="text-xs text-blue-400 font-mono">AI Engineer</div>
                      <div className="text-[11px] text-slate-400 font-sans">Pre-populated Workspace Access</div>
                    </div>
                  </div>
                  <Button size="sm" variant="primary" className="h-8 text-xs font-mono gap-1 group-hover:translate-x-0.5 transition-transform">
                    <span>Enter Workspace</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </div>

                {/* Guest Tester */}
                <div
                  onClick={() => {
                    const guest = allUsers.find((u) => u.name === 'Guest Tester') || {
                      id: 'usr_guest_tester',
                      name: 'Guest Tester',
                      role: 'Guest SRE / QA Tester',
                      has_openai_api_key: true,
                    };
                    handleSelectPreset(guest);
                  }}
                  className="p-4 rounded-xl border border-slate-800 bg-slate-900/80 hover:border-teal-500 hover:bg-slate-900 transition-all cursor-pointer flex items-center justify-between group shadow-sm"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-teal-600 flex items-center justify-center font-mono font-bold text-white shadow-md">
                      GT
                    </div>
                    <div>
                      <div className="font-mono text-sm font-bold text-white flex items-center gap-2">
                        <span>Guest Tester</span>
                        <Badge variant="success" className="text-[9px] font-mono px-1.5 py-0">Guest</Badge>
                      </div>
                      <div className="text-xs text-teal-400 font-mono">Guest SRE / QA Tester</div>
                      <div className="text-[11px] text-slate-400 font-sans">Clean Empty Workspace</div>
                    </div>
                  </div>
                  <Button size="sm" variant="secondary" className="h-8 text-xs font-mono border-slate-700 gap-1 group-hover:translate-x-0.5 transition-transform">
                    <span>Enter Workspace</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <form onSubmit={handleRegisterNewUser} className="space-y-4">
              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-300 text-xs font-sans flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
                <div>
                  <span className="font-semibold font-mono block">New User Requirement:</span>
                  You must enter your <strong>Name, Technical Role, and OpenAI API Key</strong> to create your isolated workspace.
                </div>
              </div>

              {/* Name Input */}
              <div className="space-y-1">
                <label className="block text-xs font-medium text-slate-300">
                  Engineer Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. John Doe"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-500 text-xs font-sans"
                />
              </div>

              {/* Role Dropdown */}
              <div className="space-y-1">
                <label className="block text-xs font-medium text-slate-300">
                  Technical Role <span className="text-red-400">*</span>
                </label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500 text-xs font-sans cursor-pointer"
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
                  <span className="text-[10px] text-red-400 font-sans">Mandatory for New User</span>
                </label>

                <div className="relative">
                  <input
                    type={showApiKey ? 'text' : 'password'}
                    required
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-proj-..."
                    className="w-full pl-3 pr-10 py-2.5 bg-slate-950 border border-amber-500/50 focus:border-amber-400 rounded-lg text-white placeholder:text-slate-500 focus:outline-none text-xs font-mono"
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

              <Button
                type="submit"
                variant="primary"
                size="md"
                disabled={isSubmitting || !name.trim() || !apiKey.trim()}
                className="w-full gap-2 font-semibold font-mono bg-gradient-to-r from-blue-600 to-indigo-600 shadow-md shadow-blue-500/25 mt-2"
              >
                {isSubmitting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Creating Workspace Profile...</span>
                  </>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Save & Enter Workspace</span>
                  </>
                )}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
