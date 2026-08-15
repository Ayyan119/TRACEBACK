export interface UserProfile {
  name: string;
  role: string;
}

export const DEFAULT_USER_PROFILE: UserProfile = {
  name: 'Alex Chen',
  role: 'Senior SRE',
};

export const TECH_ROLES = [
  'Senior SRE',
  'DevOps Engineer',
  'Site Reliability Engineer',
  'Platform Engineer',
  'Backend Architect',
  'Fullstack Engineer',
  'Cloud Infrastructure Lead',
  'Security & Compliance Officer',
  'Software Engineer',
  'Systems Administrator',
];

export function getStoredUserProfile(): UserProfile {
  if (typeof window === 'undefined') return DEFAULT_USER_PROFILE;
  try {
    const raw = localStorage.getItem('tb_user_profile');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed && parsed.name && parsed.role) {
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
