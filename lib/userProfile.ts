export interface UserProfile {
  id?: string;
  name: string;
  role: string;
  hasOpenAiApiKey?: boolean;
  maskedApiKey?: string;
}

export const DEFAULT_USER_PROFILE: UserProfile = {
  id: 'usr_default_ayyan',
  name: 'Ayyan Shahid',
  role: 'Senior Software Engineer',
  hasOpenAiApiKey: false,
};

export const TECH_ROLES = [
  'Senior Software Engineer',
  'AI Engineer',
  'Gen AI Engineer',
  'MLOps Engineer',
  'AI/ML Research Engineer',
  'Senior SRE',
  'Site Reliability Engineer',
  'DevOps Engineer',
  'Platform Engineer',
  'Backend Architect',
  'Fullstack Engineer',
  'Frontend Engineer',
  'Cloud Infrastructure Lead',
  'Security & Compliance Officer',
  'Data Engineer',
  'Software Engineer',
  'Systems Administrator',
  'Custom Role...',
];

export function getStoredUserId(): string {
  if (typeof window === 'undefined') return 'usr_default_ayyan';
  return localStorage.getItem('tb_user_id') || 'usr_default_ayyan';
}

export function saveStoredUserId(id: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('tb_user_id', id);
}

export function getStoredUserProfile(): UserProfile {
  if (typeof window === 'undefined') return DEFAULT_USER_PROFILE;
  try {
    const raw = localStorage.getItem('tb_user_profile');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.name && parsed.role) {
        if (parsed.name === 'Alex Chen') {
          parsed.name = 'Ayyan Shahid';
          parsed.role = 'Senior Software Engineer';
          localStorage.setItem('tb_user_profile', JSON.stringify(parsed));
        }
        return parsed;
      }
    }
  } catch (e) {
    console.error('Failed to parse stored user profile', e);
  }
  return DEFAULT_USER_PROFILE;
}

export function saveStoredUserProfile(profile: UserProfile): void {
  if (typeof window === 'undefined') return;
  try {
    if (profile.id) {
      saveStoredUserId(profile.id);
    }
    localStorage.setItem('tb_user_profile', JSON.stringify(profile));
    localStorage.setItem('tb_user_setup_completed', 'true');
    window.dispatchEvent(new Event('tb_user_profile_updated'));
  } catch (e) {
    console.error('Failed to save user profile', e);
  }
}

export function isFirstTimeUser(): boolean {
  if (typeof window === 'undefined') return false;
  return !localStorage.getItem('tb_user_setup_completed');
}

export function getInitials(name: string): string {
  if (!name) return 'AC';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
