'use client';

import React, { useState, useEffect } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';

export const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useState<'dark' | 'light' | 'system'>('dark');

  useEffect(() => {
    const saved = (localStorage.getItem('tb_theme') as 'dark' | 'light' | 'system') || 'dark';
    setTheme(saved);
    applyTheme(saved);
  }, []);

  const applyTheme = (mode: 'dark' | 'light' | 'system') => {
    let active = mode;
    if (mode === 'system') {
      active = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', active);
  };

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : theme === 'light' ? 'system' : 'dark';
    setTheme(next);
    localStorage.setItem('tb_theme', next);
    applyTheme(next);
  };

  const Icon = theme === 'dark' ? Moon : theme === 'light' ? Sun : Monitor;

  return (
    <button
      onClick={toggleTheme}
      title={`Theme: ${theme} (Click to toggle)`}
      aria-label="Toggle Theme"
      className="p-1.5 text-textSecondary hover:text-textPrimary hover:bg-bgSurfaceHover rounded-md transition-colors border border-borderColor flex items-center justify-center text-xs gap-1 font-mono"
    >
      <Icon className="w-3.5 h-3.5 text-accentPrimary" />
      <span className="capitalize hidden sm:inline text-[11px]">{theme}</span>
    </button>
  );
};
