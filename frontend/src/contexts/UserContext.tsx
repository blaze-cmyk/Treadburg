"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { supabase } from "@/lib/supabase";
import { User } from "@supabase/supabase-js";

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

// Default profile is only used when creating a new profile
const defaultProfile = (user: User): Partial<UserProfile> => ({
  auth_user_id: user.id,
  full_name: user.user_metadata?.full_name || user.email?.split("@")[0] || "User",
  email: user.email || "",
  avatar_url: user.user_metadata?.avatar_url,
  is_active: true,
  is_verified: user.email_confirmed_at ? true : false,
  subscription_tier: "free",
  credits_balance: 0,
  total_credits_purchased: 0,
  created_at: new Date().toISOString(),
  last_login_at: new Date().toISOString()
});

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Listen for auth state changes
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      setIsLoading(true);
      console.log("Auth state changed:", event);
      
      if (session?.user) {
        setUser(session.user);
        await fetchOrCreateProfile(session.user);
      } else {
        setUser(null);
        setProfile(null);
      }
      
      setIsLoading(false);
    });

    // Initial session check
    const checkSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        setUser(session.user);
        await fetchOrCreateProfile(session.user);
      }
      setIsLoading(false);
    };
    
    checkSession();
    
    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Fetch user profile from database or create one if it doesn't exist
  const fetchOrCreateProfile = async (user: User) => {
    try {
      console.log("Fetching profile for user:", user.id, user.email);
      
      // Try to get the existing profile
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('auth_user_id', user.id)
        .single();

      console.log("Profile fetch result:", { data, error });

      if (error || !data) {
        console.log("No profile found, creating new profile for user:", user.email);
        
        // Profile doesn't exist, create one
        const newProfileData = defaultProfile(user);
        console.log("Generated new profile data:", newProfileData);
        
        const { data: insertData, error: insertError } = await supabase
          .from('profiles')
          .insert([newProfileData])
          .select();

        if (insertError) {
          console.error("Error creating profile:", insertError);
          
          // Create a temporary local profile if insertion fails
          const tempProfile: UserProfile = {
            id: crypto.randomUUID(),
            auth_user_id: user.id,
            full_name: user.email?.split("@")[0] || "New User",
            email: user.email || "",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            last_login_at: new Date().toISOString(),
            is_active: true,
            is_verified: false
          } as UserProfile;
          
          setProfile(tempProfile);
          console.log("Using temporary profile due to database error", tempProfile);
          return;
        }
        
        if (insertData && insertData.length > 0) {
          console.log("Successfully created profile:", insertData[0]);
          setProfile(insertData[0] as UserProfile);
        } else {
          console.error("No profile data returned after insert");
        }
      } else {
        // Profile exists
        console.log("Found existing profile:", data);
        setProfile(data as UserProfile);
        
        // Update last login time
        await supabase
          .from('profiles')
          .update({ last_login_at: new Date().toISOString() })
          .eq('auth_user_id', user.id);
      }
    } catch (error) {
      console.error("Error fetching user profile:", error);
      
      // Fallback to a clean temporary profile
      const tempProfile: UserProfile = {
        id: crypto.randomUUID(),
        auth_user_id: user.id,
        full_name: user.email?.split("@")[0] || "New User",
        email: user.email || "",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_login_at: new Date().toISOString(),
        is_active: true,
        is_verified: false
      } as UserProfile;
      
      setProfile(tempProfile);
      console.log("Using fallback profile due to error", tempProfile);
    }
  };

  // Update profile in Supabase
  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!user || !profile) return;
    
    try {
      // Add updated_at timestamp
      const updatedData = {
        ...updates,
        updated_at: new Date().toISOString()
      };
      
      const { error } = await supabase
        .from('profiles')
        .update(updatedData)
        .eq('auth_user_id', user.id);

      if (error) {
        console.error("Error updating profile:", error);
        return;
      }

      // Update local state
      setProfile(prev => prev ? { ...prev, ...updatedData } : null);
    } catch (error) {
      console.error("Error updating profile:", error);
    }
  };

  const refreshProfile = async () => {
    if (!user) return;
    await fetchOrCreateProfile(user);
  };

  const signOut = async () => {
    try {
      console.log("Signing out user...");
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        console.error("Error signing out:", error);
        return;
      }
      
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
