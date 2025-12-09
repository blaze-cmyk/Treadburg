"use client";

import { useState, useEffect, Suspense } from "react";
import { TrendingUp, AlertCircle } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/lib/api-client";
import { supabase } from "@/lib/supabase";
import TradeBerg from "@/components/icons/TradeBerg";
import { motion } from "framer-motion";

const tradingPrompts = [
  "Analyze the current price of @AAPL",
  "What are the best stocks to buy today?",
  "Compare @BTC vs @ETH performance",
  "TradeBerg: Your AI-powered trading assistant for real-time market analysis",
  "What's the market sentiment for tech stocks?",
  "Show me portfolio diversification strategies",
];

// Wrap the main content in a component that uses useSearchParams
function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentPromptIndex, setCurrentPromptIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const [isLogin, setIsLogin] = useState(true);

  // Form state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Check if user is already logged in
  useEffect(() => {
    const checkSession = async () => {
      try {
        console.log('Checking for existing session...');
        const token = apiClient.getAuthToken();
        if (token) {
          console.log('User already has a token, redirecting to dashboard');
          router.push('/dashboard');
        }
      } catch (err) {
        console.error('Error checking session:', err);
      }
    };

    checkSession();

    // Check for auth success or error params
    const authSuccess = searchParams?.get('auth');
    const errorType = searchParams?.get('error');
    const accessToken = searchParams?.get('access_token');
    
    // Log auth parameters for debugging
    if (authSuccess || errorType || accessToken) {
      console.log('Auth URL parameters detected:', { 
        authSuccess, 
        errorType, 
        hasAccessToken: !!accessToken 
      });
    }
    
    // Handle successful authentication
    if (authSuccess === 'success' || accessToken) {
      console.log('Authentication successful, checking for redirect');
      
      // Check if we have a redirect cookie
      const cookies = document.cookie.split(';');
      let redirectPath = '/';
      
      for (const cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'redirect_after_login' && value) {
          // We have a redirect path
          redirectPath = decodeURIComponent(value);
          console.log('Redirecting to stored path:', redirectPath);
          // Clear the cookie
          document.cookie = 'redirect_after_login=; max-age=0; path=/';
          break;
        }
      }
      
      // Use replace to avoid back navigation issues
      router.replace(redirectPath);
      return;
    }
    
    // Handle authentication errors
    if (errorType === 'auth_callback_error') {
      const reason = searchParams?.get('reason');
      setError(`Authentication failed: ${reason || 'Please try again.'}`);
    } else if (errorType === 'unexpected') {
      const message = searchParams?.get('message');
      setError(`An unexpected error occurred: ${message || 'Please try again.'}`);
    } else if (errorType === 'no_code') {
      setError('Authentication process was interrupted. Please try again.');
    }
  }, [router, searchParams]);

  // Typing animation effect
  useEffect(() => {
    const currentPrompt = tradingPrompts[currentPromptIndex];
    let currentIndex = 0;
    setIsTyping(true);
    setDisplayedText("");

    const typingInterval = setInterval(() => {
      if (currentIndex < currentPrompt.length) {
        setDisplayedText(currentPrompt.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        setIsTyping(false);
        clearInterval(typingInterval);

        // Wait 2 seconds before moving to next prompt
        setTimeout(() => {
          setCurrentPromptIndex((prev) => (prev + 1) % tradingPrompts.length);
        }, 2000);
      }
    }, 50); // Typing speed (50ms per character)

    return () => clearInterval(typingInterval);
  }, [currentPromptIndex]);

  // Handle loading state with our own implementation

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Left Section - 2/3 width with gradient background */}
      <div className="hidden md:flex md:w-2/3 bg-gradient-to-br from-[#0f172a] via-[#1e1b4b] to-[#312e81] relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(99,102,241,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(139,92,246,0.1),transparent_50%)]" />

        <div className="relative z-10 flex flex-col justify-between w-full p-8">
          {/* Top Logo */}
          <div>
            <TradeBerg className="w-32 h-8 text-white" />
          </div>

          {/* Center Prompt */}
          <div className="flex-1 flex items-center justify-center px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-left w-full max-w-2xl"
            >
              <p className="text-[#c084fc] text-2xl md:text-3xl lg:text-4xl font-normal leading-relaxed tracking-normal">
                {displayedText}
                {isTyping && (
                  <motion.span
                    animate={{ opacity: [1, 0] }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      repeatType: "reverse",
                    }}
                    className="inline-block w-2 h-6 md:h-8 bg-[#c084fc] ml-1 align-middle"
                  />
                )}
              </p>
            </motion.div>
          </div>

          {/* Bottom - Empty for now */}
          <div></div>
        </div>
      </div>

      {/* Right Section - 1/3 width with dark background */}
      <div className="w-full md:w-1/3 bg-[#0a0a0a] flex flex-col">
        <div className="flex-1 flex flex-col justify-center px-8 py-12">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-semibold text-[var(--tradeberg-text-primary)] mb-2">
              Get started
            </h1>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mb-6">
            <button
              onClick={() => {
                setIsLogin(true);
                router.push("/");
              }}
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${isLogin
                ? "bg-[var(--tradeberg-accent-color)] text-white hover:opacity-90"
                : "bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-secondary)] hover:bg-opacity-80 border border-[var(--tradeberg-glass-border)]"
                }`}
            >
              Log in
            </button>
            <button
              onClick={() => {
                setIsLogin(false);
                router.push("/");
              }}
              className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${!isLogin
                ? "bg-[var(--tradeberg-accent-color)] text-white hover:opacity-90"
                : "bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-secondary)] hover:bg-opacity-80 border border-[var(--tradeberg-glass-border)]"
                }`}
            >
              Sign up for free
            </button>
          </div>

          {/* Try it first link */}
          <div className="text-center mb-8">
            <Link
              href="/"
              className="text-[var(--tradeberg-text-primary)] text-sm hover:underline"
            >
              Try it first
            </Link>
          </div>

          {/* Divider */}
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-px bg-[var(--tradeberg-glass-border)]"></div>
            <span className="text-[var(--tradeberg-text-secondary)] text-xs">
              OR
            </span>
            <div className="flex-1 h-px bg-[var(--tradeberg-glass-border)]"></div>
          </div>

          {/* Email/Password Form */}
          <form onSubmit={async (e) => {
            e.preventDefault();
            setLoading(true);
            setError("");

            try {
              if (isLogin) {
                // Login through backend API
                console.log('Attempting to sign in with email:', email);
                const response = await apiClient.login(email, password);

                console.log('Login successful, redirecting to dashboard');
                
                // Clear any error messages
                setError("");
                
                // Force a full page reload to dashboard to ensure clean state
                window.location.href = '/dashboard';
              } else {
                // Sign up through backend API
                console.log('Attempting to sign up with email:', email);
                const response = await apiClient.register(email, password);

                setError("");
                alert("Registration successful! Please check your email to confirm your account.");
                // Switch to login mode
                setIsLogin(true);
              }
            } catch (err: any) {
              console.error("Authentication error:", err);
              setError(err?.message || "An unexpected error occurred");
            } finally {
              setLoading(false);
            }
          }} className="space-y-4 mb-6">
            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-500">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{error}</span>
              </div>
            )}
            <div>
              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full py-3 px-4 bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-primary)] rounded-lg border border-[var(--tradeberg-glass-border)] focus:border-[var(--tradeberg-accent-color)] focus:outline-none transition-colors placeholder:text-[var(--tradeberg-text-secondary)]"
              />
            </div>
            <div>
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full py-3 px-4 bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-primary)] rounded-lg border border-[var(--tradeberg-glass-border)] focus:border-[var(--tradeberg-accent-color)] focus:outline-none transition-colors placeholder:text-[var(--tradeberg-text-secondary)]"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 bg-[var(--tradeberg-accent-color)] hover:opacity-90 text-white rounded-lg font-medium transition-all ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {isLogin ? "Logging in..." : "Signing up..."}
                </span>
              ) : (
                isLogin ? "Log in" : "Sign up"
              )}
            </button>
            {isLogin && (
              <div className="text-center">
                <button
                  type="button"
                  onClick={async () => {
                    if (!email) {
                      alert("Please enter your email address");
                      return;
                    }

                    setLoading(true);
                    try {
                      await apiClient.resetPassword(email);
                      alert("Password reset email sent. Please check your inbox.");
                    } catch (err: any) {
                      console.error("Password reset error:", err);
                      alert(err?.message || "An error occurred. Please try again.");
                    } finally {
                      setLoading(false);
                    }
                  }}
                  className="text-[var(--tradeberg-text-secondary)] text-sm hover:text-[var(--tradeberg-text-primary)] transition-colors"
                >
                  Forgot password?
                </button>
              </div>
            )}
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-px bg-[var(--tradeberg-glass-border)]"></div>
            <span className="text-[var(--tradeberg-text-secondary)] text-xs">
              OR CONTINUE WITH
            </span>
            <div className="flex-1 h-px bg-[var(--tradeberg-glass-border)]"></div>
          </div>

          {/* Google OAuth Only */}
          <div>
            <button
              className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-[var(--tradeberg-card-bg)] hover:bg-opacity-80 text-[var(--tradeberg-text-primary)] rounded-lg transition-colors border border-[var(--tradeberg-glass-border)]"
              onClick={async () => {
                try {
                  setLoading(true);
                  console.log('Starting Google OAuth...');
                  
                  // Import the helper functions
                  const { getOAuthRedirectUrl, getGoogleOAuthOptions } = await import('@/lib/auth-helpers');
                  
                  // Get the redirect URL and OAuth options
                  const redirectTo = getOAuthRedirectUrl();
                  console.log('Using OAuth redirect URL:', redirectTo);
                  
                  // Create a new Supabase session with explicit options
                  const { data, error } = await supabase.auth.signInWithOAuth({
                    provider: 'google',
                    options: {
                      // Use the helper function to get the redirect URL
                      redirectTo,
                      // Use the helper function to get the Google OAuth options
                      ...getGoogleOAuthOptions()
                    }
                  });
                  
                  // Log the redirect URL for debugging
                  if (data?.url) {
                    console.log('OAuth initiated - redirecting to:', data.url);
                  } else {
                    console.log('OAuth initiated but no URL returned');  
                  }

                  if (error) {
                    setError(error.message);
                  }
                  
                  // If there's a URL, the OAuth flow is continuing elsewhere, so we can reset loading
                  if (data?.url) {
                    // OAuth redirect happens automatically, we don't need to keep the loading state
                    setLoading(false);
                  }
                } catch (err: any) {
                  console.error('Google login error:', err);
                  setError(err?.message || 'Failed to sign in with Google');
                  setLoading(false);
                }
              }}
            >
              <Image
                src="https://auth-cdn.oaistatic.com/assets/google-logo-NePEveMl.svg"
                width={20}
                height={20}
                alt="Google Icon"
              />
              Continue with Google
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="px-8 py-6 border-t border-[var(--tradeberg-glass-border)]">
          <div className="flex items-center justify-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[var(--tradeberg-text-primary)]" />
              <span className="text-[var(--tradeberg-text-primary)] font-semibold">
                TradeBerg
              </span>
            </div>
            <div className="text-[var(--tradeberg-text-secondary)]">|</div>
            <Link
              href="/"
              className="text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"
            >
              Terms of use
            </Link>
            <div className="text-[var(--tradeberg-text-secondary)]">|</div>
            <Link
              href="/"
              className="text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"
            >
              Privacy policy
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

// Loading fallback for Suspense
function LoginLoading() {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-[#0a0a0a]">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-4"></div>
        <p className="text-gray-400">Loading...</p>
      </div>
    </div>
  );
}

// Default export with Suspense wrapper
export default function Login() {
  return (
    <Suspense fallback={<LoginLoading />}>
      <LoginContent />
    </Suspense>
  );
}
