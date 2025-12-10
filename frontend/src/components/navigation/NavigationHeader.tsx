"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Home, DollarSign, User, Menu, X, LogOut } from "lucide-react";
import { useUser } from "@/contexts/UserContext";
import { useRouter } from "next/navigation";

export function NavigationHeader() {
    const pathname = usePathname();
    const { profile } = useUser();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const router = useRouter();

    const handleLogout = async () => {
        await fetch('/api/auth/logout', { method: 'POST' });
        router.push("/login");
    };

    const navItems = [
        { href: "/", label: "Home", icon: Home },
        { href: "/pricing", label: "Pricing", icon: DollarSign },
        { href: "/profile", label: "Profile", icon: User },
    ];

    return (
        <header className="sticky top-0 z-50 w-full border-b border-[var(--tradeberg-card-border)] bg-[var(--tradeberg-bg)]/80 backdrop-blur-sm">
            <nav className="container mx-auto flex h-16 items-center justify-between px-4">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                        <span className="text-white font-bold text-lg">T</span>
                    </div>
                    <span className="text-xl font-bold text-foreground hidden sm:inline">TradeBerg</span>
                </Link>

                {/* Desktop Navigation */}
                <div className="hidden md:flex items-center gap-6">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${isActive
                                    ? "bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-accent-color)]"
                                    : "text-muted-foreground hover:text-foreground hover:bg-[var(--tradeberg-card-bg)]"
                                    }`}
                            >
                                <Icon size={16} />
                                {item.label}
                            </Link>
                        );
                    })}
                </div>

                {/* User Info & Actions */}
                <div className="hidden md:flex items-center gap-4">
                    {/* Credits Badge */}
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)]">
                        <span className="text-xs text-muted-foreground">💳</span>
                        <span className="text-xs font-semibold text-foreground">
                            {profile.creditsBalance === 999999 ? "Unlimited" : profile.creditsBalance}
                        </span>
                    </div>

                    {/* Subscription Tier */}
                    <div
                        className={`px-3 py-1.5 rounded-full text-xs font-semibold ${profile.subscriptionTier === "free"
                            ? "bg-gray-500/10 text-gray-400"
                            : profile.subscriptionTier === "pro"
                                ? "bg-blue-500/10 text-blue-400"
                                : "bg-purple-500/10 text-purple-400"
                            }`}
                    >
                        {profile.subscriptionTier.charAt(0).toUpperCase() + profile.subscriptionTier.slice(1)}
                    </div>

                    {/* Logout */}
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-[var(--tradeberg-card-bg)] transition-colors"
                    >
                        <LogOut size={16} />
                        Logout
                    </button>
                </div>

                {/* Mobile Menu Button */}
                <button
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    className="md:hidden p-2 rounded-lg hover:bg-[var(--tradeberg-card-bg)]"
                >
                    {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                </button>
            </nav>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden border-t border-[var(--tradeberg-card-border)] bg-[var(--tradeberg-bg)]">
                    <div className="container mx-auto px-4 py-4 space-y-2">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${isActive
                                        ? "bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-accent-color)]"
                                        : "text-muted-foreground hover:text-foreground hover:bg-[var(--tradeberg-card-bg)]"
                                        }`}
                                >
                                    <Icon size={18} />
                                    {item.label}
                                </Link>
                            );
                        })}

                        {/* Mobile User Info */}
                        <div className="pt-4 mt-4 border-t border-[var(--tradeberg-card-border)] space-y-3">
                            <div className="flex items-center justify-between px-4">
                                <span className="text-sm text-muted-foreground">Credits</span>
                                <span className="text-sm font-semibold text-foreground">
                                    {profile.creditsBalance === 999999 ? "Unlimited" : profile.creditsBalance}
                                </span>
                            </div>
                            <div className="flex items-center justify-between px-4">
                                <span className="text-sm text-muted-foreground">Tier</span>
                                <span className="text-sm font-semibold text-foreground capitalize">
                                    {profile.subscriptionTier}
                                </span>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition-colors"
                            >
                                <LogOut size={18} />
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </header>
    );
}
