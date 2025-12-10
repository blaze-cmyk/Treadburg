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
      // TODO: Get user ID from auth session
      // For now, we'll skip the backend call if not authenticated
      // In production, this should fetch from /api/users/profile

      // Example:
      // const response = await fetch('/api/users/profile');
      // if (response.ok) {
      //   const data = await response.json();
      //   setProfile(prev => ({ ...prev, ...data }));
      // }
    } catch (error) {
      console.error("Failed to refresh profile:", error);
    }
  };

  const updateProfile = (updates: Partial<UserProfile>) => {
    setProfile((prev) => ({ ...prev, ...updates }));

    // TODO: Send updates to backend
    // fetch('/api/users/profile', {
    //   method: 'PUT',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(updates),
    // });
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
