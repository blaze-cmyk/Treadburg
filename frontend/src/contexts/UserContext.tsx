"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface UserProfile {
  name: string;
  email: string;
  joinDate: string;
  bio: string;
  location: string;
  website: string;
  subscriptionTier: "free" | "pro" | "max";
  creditsBalance: number;
  stripeCustomerId?: string;
}

interface UserContextType {
  profile: UserProfile;
  updateProfile: (updates: Partial<UserProfile>) => void;
  getInitials: () => string;
  refreshProfile: () => Promise<void>;
}

const defaultProfile: UserProfile = {
  name: "Guest User",
  email: "loading...",
  joinDate: "Recently",
  bio: "",
  location: "",
  website: "",
  subscriptionTier: "free",
  creditsBalance: 0,
};


const UserContext = createContext<UserContextType | undefined>(undefined);

const STORAGE_KEY = "tradeberg-user-profile";

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [profile, setProfile] = useState<UserProfile>(defaultProfile);

  // Load profile from localStorage on mount, then fetch from backend
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setProfile({ ...defaultProfile, ...parsed });
      }
    } catch (error) {
      console.error("Failed to load user profile from localStorage:", error);
    }

    // Fetch latest profile from backend
    refreshProfile();
  }, []);

  // Save profile to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
    } catch (error) {
      console.error("Failed to save user profile to localStorage:", error);
    }
  }, [profile]);

  const refreshProfile = async () => {
    try {
      // Get session from backend API (replaces Supabase client)
      const response = await fetch('/api/auth/session');
      const data = await response.json();

      if (!data.success || !data.user) {
        console.log('No active session from backend');
        return;
      }

      const backendUser = data.user;
      const userEmail = backendUser.email || 'user@example.com';
      const userName = backendUser.full_name || userEmail.split('@')[0];

      console.log('Loaded user from backend session:', {
        email: userEmail,
        name: userName
      });

      // Set profile with real backend data
      const updatedProfile: Partial<UserProfile> = {
        email: userEmail,
        name: userName,
        subscriptionTier: (backendUser.subscription_tier as "free" | "pro" | "max") || 'free',
        creditsBalance: backendUser.credits || 0,
        bio: backendUser.bio || '',
        location: backendUser.location || '',
        website: backendUser.website || '',
        joinDate: backendUser.created_at
          ? new Date(backendUser.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
          : 'Recently',
      };

      setProfile(prev => ({ ...prev, ...updatedProfile }));
      console.log('Profile loaded from backend:', updatedProfile);

    } catch (error) {
      console.error("Failed to refresh profile:", error);
    }
  };

  const updateProfile = async (updates: Partial<UserProfile>) => {
    setProfile((prev) => ({ ...prev, ...updates }));

    // Send updates to backend
    try {
      const response = await fetch('/api/users/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: updates.name,
          bio: updates.bio,
          location: updates.location,
          website: updates.website,
        }),
      });

      if (!response.ok) {
        console.warn('Failed to update profile on backend');
      } else {
        console.log('Profile updated successfully');
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
    }
  };

  const getInitials = () => {
    const names = profile.name.trim().split(" ");
    if (names.length === 0) return "U";
    if (names.length === 1) return names[0].charAt(0).toUpperCase();
    return (
      names[0].charAt(0) + names[names.length - 1].charAt(0)
    ).toUpperCase();
  };

  return (
    <UserContext.Provider value={{ profile, updateProfile, getInitials, refreshProfile }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}
