import { createClient } from '@supabase/supabase-js'

// Use environment variables for Supabase configuration (Render deployment ready)
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://pcxscejarxztezfeucgs.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBjeHNjZWphcnh6dGV6ZmV1Y2dzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5NTMwOTcsImV4cCI6MjA3ODUyOTA5N30.tMERXgpNtF88ywJhH0t62SAudTk4iYu_Xv0xgGg-Ll0'

// Create the Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Get the app URL for redirects (works in both browser and server)
const getAppUrl = () => {
  if (typeof window !== 'undefined') {
    return window.location.origin
  }
  return process.env.NEXTAUTH_URL || process.env.NEXT_PUBLIC_APP_URL || 'https://tradeberg-frontend.onrender.com'
}

// Auth helper functions
export const auth = {
  // Sign up with email and password
  signUp: async (email: string, password: string) => {
    return supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: `${getAppUrl()}/auth/callback`
      }
    })
  },

  // Sign in with email and password
  signIn: async (email: string, password: string) => {
    return supabase.auth.signInWithPassword({
      email,
      password
    })
  },

  // Sign out
  signOut: async () => {
    return supabase.auth.signOut()
  },

  // Reset password
  resetPassword: async (email: string) => {
    return supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${getAppUrl()}/reset-password`,
    })
  },

  // Update password
  updatePassword: async (password: string) => {
    return supabase.auth.updateUser({
      password
    })
  },

  // Get current session
  getSession: async () => {
    return supabase.auth.getSession()
  },

  // Get current user
  getUser: async () => {
    const { data } = await supabase.auth.getUser()
    return data.user
  }
}
