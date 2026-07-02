/**
 * SPARK — User & Auth Types
 */

export interface User {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
  onboardingComplete: boolean;
  createdAt: string;
  lastActiveAt: string;
  settings: UserSettings;
}

export interface UserSettings {
  timezone: string;
  workingHoursStart: string;  // "09:00"
  workingHoursEnd: string;    // "17:00"
  workingDays: number[];      // [1,2,3,4,5]
  notificationsEnabled: boolean;
  calendarConnected: boolean;
  gmailConnected: boolean;
}

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
}

export type AuthState =
  | { status: "loading" }
  | { status: "unauthenticated" }
  | { status: "authenticated"; user: AuthUser };