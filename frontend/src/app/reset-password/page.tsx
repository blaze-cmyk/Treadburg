"use client";

import { useState, useEffect } from "react";
import { TrendingUp, AlertCircle, Check } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase, auth } from "@/lib/supabase";

export default function ResetPassword() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    
    if (password.length < 6) {
      setError("Password must be at least 6 characters long");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const { error } = await auth.updatePassword(password);
      
      if (error) {
        setError(error.message);
      } else {
        setSuccess(true);
        setTimeout(() => {
          router.push('/login');
        }, 3000);
      }
    } catch (err) {
      console.error("Password reset error:", err);
      setError("An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block mb-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-[var(--tradeberg-accent-color)]" />
              <span className="text-[var(--tradeberg-text-primary)] font-semibold text-xl">TradeBerg</span>
            </div>
          </Link>
          <h1 className="text-2xl font-semibold text-[var(--tradeberg-text-primary)]">Reset your password</h1>
          <p className="text-[var(--tradeberg-text-secondary)] mt-2">Enter your new password below</p>
        </div>
        
        {success ? (
          <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg flex items-center gap-3 text-green-500 mb-6">
            <Check className="w-5 h-5" />
            <div>
              <p className="font-medium">Password updated successfully!</p>
              <p className="text-sm opacity-80">Redirecting you to login page...</p>
            </div>
          </div>
        ) : (
          <form onSubmit={handleResetPassword} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-500">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{error}</span>
              </div>
            )}
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-[var(--tradeberg-text-secondary)] mb-1">New Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full py-3 px-4 bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-primary)] rounded-lg border border-[var(--tradeberg-glass-border)] focus:border-[var(--tradeberg-accent-color)] focus:outline-none"
              />
            </div>
            
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-[var(--tradeberg-text-secondary)] mb-1">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={6}
                className="w-full py-3 px-4 bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-primary)] rounded-lg border border-[var(--tradeberg-glass-border)] focus:border-[var(--tradeberg-accent-color)] focus:outline-none"
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 mt-2 bg-[var(--tradeberg-accent-color)] hover:opacity-90 text-white rounded-lg font-medium transition-all ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Updating password...
                </span>
              ) : "Reset Password"}
            </button>
          </form>
        )}
        
        <div className="mt-8 text-center">
          <Link href="/login" className="text-[var(--tradeberg-text-secondary)] text-sm hover:text-[var(--tradeberg-text-primary)] transition-colors">
            Back to login
          </Link>
        </div>
      </div>
    </div>
  );
}
