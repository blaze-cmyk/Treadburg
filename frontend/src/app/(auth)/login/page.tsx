"use client";

import { useState, useEffect } from "react";
import { Phone, TrendingUp, AlertCircle } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import TradeBerg from "@/components/icons/TradeBerg";
import { motion } from "framer-motion";
import { backendAuth } from "@/lib/backend-auth";

const tradingPrompts = [
  "Analyze the current price of @AAPL",
  "What are the best stocks to buy today?",
  "Compare @BTC vs @ETH performance",
  "TradeBerg: Your AI-powered trading assistant for real-time market analysis",
  "What's the market sentiment for tech stocks?",
  "Show me portfolio diversification strategies",
];

export default function Login() {
  const router = useRouter();
  const [currentPromptIndex, setCurrentPromptIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Form fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [showEmailForm, setShowEmailForm] = useState(false);

  // Check if already logged in
  useEffect(() => {
    const checkSession = async () => {
      const response = await backendAuth.getSession();
      if (response.success && response.user) {
        router.push("/");
      }
    };
    checkSession();
  }, [router]);

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

        setTimeout(() => {
          setCurrentPromptIndex((prev) => (prev + 1) % tradingPrompts.length);
        }, 2000);
      }
    }, 50);

    return () => clearInterval(typingInterval);
  }, [currentPromptIndex]);

  // Handle Google sign in
  const handleGoogleSignIn = async () => {
    try {
      setLoading(true);
      setError("");
      const response = await backendAuth.googleInit();
      if (response.auth_url) {
        window.location.href = response.auth_url;
      } else {
        setError("Failed to initialize Google sign-in");
        setLoading(false);
      }
    } catch (err: any) {
      setError("Failed to sign in with Google");
      setLoading(false);
    }
  };

  // Handle email auth
  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let response;

      if (isLogin) {
        response = await backendAuth.login(email, password);
      } else {
        response = await backendAuth.signup(email, password, fullName);
      }

      if (response.success) {
        router.push("/");
        router.refresh();
      } else {
        setError(response.message || "Authentication failed");
      }
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

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

          {!showEmailForm ? (
            <>
              {/* Action Buttons */}
              <div className="flex gap-3 mb-6">
                <button
                  onClick={() => setIsLogin(true)}
                  className={`flex-1 py-3 px-6 rounded-lg font-medium transition-all ${isLogin
                      ? "bg-[var(--tradeberg-accent-color)] text-white hover:opacity-90"
                      : "bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-secondary)] hover:bg-opacity-80 border border-[var(--tradeberg-glass-border)]"
                    }`}
                >
                  Log in
                </button>
                <button
                  onClick={() => setIsLogin(false)}
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

              {/* Social Auth Buttons */}
              <div className="space-y-3">
                <button
                  className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-[var(--tradeberg-card-bg)] hover:bg-opacity-80 text-[var(--tradeberg-text-primary)] rounded-lg transition-colors border border-[var(--tradeberg-glass-border)]"
                  onClick={handleGoogleSignIn}
                  disabled={loading}
                >
                  <Image
                    src="https://auth-cdn.oaistatic.com/assets/google-logo-NePEveMl.svg"
                    width={20}
                    height={20}
                    alt="Google Icon"
                  />
                  Continue with Google
                </button>

                <button
                  className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-[var(--tradeberg-card-bg)] hover:bg-opacity-80 text-[var(--tradeberg-text-primary)] rounded-lg transition-colors border border-[var(--tradeberg-glass-border)]"
                  onClick={() => setShowEmailForm(true)}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Continue with Email
                </button>

                <button className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-[var(--tradeberg-card-bg)] hover:bg-opacity-80 text-[var(--tradeberg-text-primary)] rounded-lg transition-colors border border-[var(--tradeberg-glass-border)]">
                  <Image
                    src="https://auth-cdn.oaistatic.com/assets/microsoft-logo-BUXxQnXH.svg"
                    width={20}
                    height={20}
                    alt="Microsoft Icon"
                  />
                  Continue with Microsoft
                </button>
                <button className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-[var(--tradeberg-card-bg)] hover:bg-opacity-80 text-[var(--tradeberg-text-primary)] rounded-lg transition-colors border border-[var(--tradeberg-glass-border)]">
                  <Image
                    src="https://auth-cdn.oaistatic.com/assets/apple-logo-vertically-balanced-rwLdlt8P.svg"
                    width={20}
                    height={20}
                    alt="Apple Icon"
                  />
                  Continue with Apple
                </button>
                <button className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-[var(--tradeberg-card-bg)] hover:bg-opacity-80 text-[var(--tradeberg-text-primary)] rounded-lg transition-colors border border-[var(--tradeberg-glass-border)]">
                  <Phone width={20} height={20} />
                  Continue with phone
                </button>
              </div>
            </>
          ) : (
            /* Email/Password Form */
            <form onSubmit={handleEmailAuth} className="space-y-4">
              <button
                type="button"
                onClick={() => {
                  setShowEmailForm(false);
                  setError("");
                }}
                className="text-[var(--tradeberg-accent-color)] text-sm mb-4 hover:underline"
              >
                ← Back to options
              </button>

              {error && (
                <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2 text-red-400">
                  <AlertCircle size={16} />
                  <span className="text-sm">{error}</span>
                </div>
              )}

              {!isLogin && (
                <input
                  type="text"
                  placeholder="Full name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full py-3 px-4 bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-primary)] rounded-lg border border-[var(--tradeberg-glass-border)] focus:border-[var(--tradeberg-accent-color)] focus:outline-none transition-colors placeholder:text-[var(--tradeberg-text-secondary)]"
                />
              )}

              <input
                type="email"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full py-3 px-4 bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-primary)] rounded-lg border border-[var(--tradeberg-glass-border)] focus:border-[var(--tradeberg-accent-color)] focus:outline-none transition-colors placeholder:text-[var(--tradeberg-text-secondary)]"
              />

              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full py-3 px-4 bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-primary)] rounded-lg border border-[var(--tradeberg-glass-border)] focus:border-[var(--tradeberg-accent-color)] focus:outline-none transition-colors placeholder:text-[var(--tradeberg-text-secondary)]"
              />

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-[var(--tradeberg-accent-color)] hover:opacity-90 text-white rounded-lg font-medium transition-all disabled:opacity-70"
              >
                {loading ? (isLogin ? "Logging in..." : "Signing up...") : (isLogin ? "Log in" : "Sign up")}
              </button>
            </form>
          )}
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
