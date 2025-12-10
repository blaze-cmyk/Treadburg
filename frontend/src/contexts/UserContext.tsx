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
  name: "Harsh Agrawal",
  email: "harsh@example.com",
  joinDate: "January 2024",
  bio: "Active trader and market analyst",
  location: "Mumbai, India",
  website: "https://example.com",
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
      // Import supabase client
      const { supabase } = await import('@/lib/supabase');

      // Get current session
      const { data: { session } } = await supabase.auth.getSession();

      if (!session) {
        console.log('No active session, using default profile');
        return;
      }

      // Fetch profile from backend API
      const response = await fetch('/api/users/profile');

      if (response.ok) {
        const data = await response.json();

        if (data.success && data.user) {
          const backendUser = data.user;

          // Map backend data to frontend profile format
          const updatedProfile: Partial<UserProfile> = {
            email: backendUser.email || session.user.email,
            name: backendUser.full_name || session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'User',
            bio: backendUser.bio || '',
            location: backendUser.location || '',
            website: backendUser.website || '',
            subscriptionTier: (backendUser.subscription_tier as "free" | "pro" | "max") || 'free',
            creditsBalance: backendUser.credits_balance || backendUser.credits || 0,
            stripeCustomerId: backendUser.stripe_customer_id,
            joinDate: backendUser.created_at
              ? new Date(backendUser.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
              : 'Recently',
          };

          setProfile(prev => ({ ...prev, ...updatedProfile }));
          console.log('Profile refreshed from backend:', updatedProfile);
        }
      } else {
        console.warn('Failed to fetch profile from backend:', response.status);
      }
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
