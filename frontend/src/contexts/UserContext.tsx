"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { apiClient } from "@/lib/api-client";

interface UserProfile {
  id: string;
  auth_user_id: string;
  email: string;
  full_name: string;
  bio?: string;
  country?: string;
  phone?: string;
  avatar_url?: string;
  timezone?: string;
  language?: string;
  preferred_assets?: string[];
  risk_tolerance?: string;
  trading_experience?: string;
  subscription_tier?: string;
  credits_balance?: number;
  total_credits_purchased?: number;
  created_at?: string;
  updated_at?: string;
  last_login_at?: string;
  is_active?: boolean;
  is_verified?: boolean;
}

interface User {
  id: string;
  email: string;
  email_confirmed_at?: string;
}

interface UserContextType {
  user: User | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;
  getInitials: () => string;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}


const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      setIsLoading(true);
      const token = apiClient.getAuthToken();
      
      if (!token) {
        setUser(null);
        setProfile(null);
        setIsLoading(false);
        return;
      }

      // Get current user from backend
      const response = await apiClient.getCurrentUser();
      setUser(response.user);
      setProfile(response.profile);
    } catch (error) {
      console.error("Auth check failed:", error);
      // Clear invalid token
      apiClient.setAuthToken(null);
      setUser(null);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };


  // Update profile through backend
  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!user || !profile) return;
    
    try {
      // Update profile through backend API
      const response = await apiClient.updateUserProfile(updates);
      
      // Update local state with response
      if (response.profile) {
        setProfile(response.profile);
      } else {
        // Fallback: update local state
        setProfile(prev => prev ? { ...prev, ...updates } : null);
      }
    } catch (error) {
      console.error("Error updating profile:", error);
      throw error;
    }
  };

  const refreshProfile = async () => {
    await checkAuth();
  };

  const signOut = async () => {
    try {
      console.log("Signing out user...");
      await apiClient.logout();
      
      // Clear local state
      setUser(null);
      setProfile(null);
      
      console.log("User signed out successfully");
      
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    } catch (error) {
      console.error("Error during sign out:", error);
    }
  };

  const getInitials = () => {
    if (!profile || !profile.full_name) return "U";
    
    const names = profile.full_name.trim().split(" ");
    if (names.length === 0) return "U";
    if (names.length === 1) return names[0].charAt(0).toUpperCase();
    return (
      names[0].charAt(0) + names[names.length - 1].charAt(0)
    ).toUpperCase();
  };

  return (
    <UserContext.Provider value={{
      user,
      profile,
      isLoading,
      isAuthenticated: !!user,
      updateProfile,
      getInitials,
      signOut,
      refreshProfile
    }}>
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
