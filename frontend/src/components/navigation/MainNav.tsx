"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useUser } from "@/contexts/UserContext";
import {
  UserCircle,
  Menu,
  X,
  LogOut,
  Settings,
  User,
  BarChart3,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

interface MainNavProps {
  className?: string;
}

export function MainNav({ className }: MainNavProps) {
  const pathname = usePathname();
  const { user, profile, isAuthenticated, signOut, getInitials } = useUser();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const routes = [
    {
      href: "/",
      label: "Home",
      active: pathname === "/",
      public: true,
    },
    {
      href: "/market",
      label: "Markets",
      active: pathname === "/market",
      public: true,
    },
    {
      href: "/dashboard",
      label: "Dashboard",
      active: pathname === "/dashboard",
      public: false,
    },
    {
      href: "/portfolio",
      label: "Portfolio",
      active: pathname === "/portfolio",
      public: false,
    },
  ];

  return (
    <nav
      className={cn(
        "flex items-center justify-between w-full px-4 py-4 md:px-8 lg:px-12",
        className
      )}
    >
      {/* Logo */}
      <Link href="/" className="flex items-center gap-2">
        <Image
          src="/assets/logo.svg"
          alt="TradeBerg Logo"
          width={40}
          height={40}
          className="w-10 h-10"
        />
        <span className="text-xl font-bold">TradeBerg</span>
      </Link>

      {/* Desktop Menu */}
      <div className="hidden md:flex items-center gap-6">
        {routes
          .filter((route) => route.public || isAuthenticated)
          .map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                route.active ? "text-primary" : "text-muted-foreground"
              )}
            >
              {route.label}
            </Link>
          ))}
      </div>

      {/* Auth Buttons / User Menu */}
      <div className="hidden md:flex items-center gap-2">
        {isAuthenticated ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative p-1 rounded-full">
                {profile?.avatar_url ? (
                  <Image
                    src={profile.avatar_url}
                    alt={profile.full_name || "User"}
                    width={36}
                    height={36}
                    className="rounded-full"
                  />
                ) : (
                  <div className="flex items-center justify-center w-9 h-9 rounded-full bg-primary/10 text-primary">
                    {getInitials()}
                  </div>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <div className="px-2 py-1.5 text-sm font-medium">
                {profile?.full_name || "User"}
              </div>
              <DropdownMenuItem asChild>
                <Link href="/profile" className="cursor-pointer">
                  <User className="mr-2 size-4" />
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/dashboard" className="cursor-pointer">
                  <BarChart3 className="mr-2 size-4" />
                  Dashboard
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href="/settings" className="cursor-pointer">
                  <Settings className="mr-2 size-4" />
                  Settings
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={signOut}
                className="text-destructive focus:bg-destructive/10 focus:text-destructive"
              >
                <LogOut className="mr-2 size-4" />
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <>
            <Button asChild variant="outline">
              <Link href="/login">Log In</Link>
            </Button>
            <Button asChild>
              <Link href="/signup">Sign Up</Link>
            </Button>
          </>
        )}
      </div>

      {/* Mobile Menu Button */}
      <button
        className="md:hidden p-2 text-foreground"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
      >
        {mobileMenuOpen ? (
          <X className="size-6" />
        ) : (
          <Menu className="size-6" />
        )}
      </button>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-50 bg-background pt-16 px-4">
          <button
            className="absolute top-4 right-4 p-2 text-foreground"
            onClick={() => setMobileMenuOpen(false)}
          >
            <X className="size-6" />
          </button>

          <div className="flex flex-col gap-6">
            {routes
              .filter((route) => route.public || isAuthenticated)
              .map((route) => (
                <Link
                  key={route.href}
                  href={route.href}
                  className={cn(
                    "text-lg font-medium transition-colors hover:text-primary py-2",
                    route.active ? "text-primary" : "text-foreground"
                  )}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {route.label}
                </Link>
              ))}

            <div className="border-t border-border mt-4 pt-4 space-y-4">
              {isAuthenticated ? (
                <>
                  <div className="flex items-center gap-3 py-2">
                    {profile?.avatar_url ? (
                      <Image
                        src={profile.avatar_url}
                        alt={profile.full_name || "User"}
                        width={40}
                        height={40}
                        className="rounded-full"
                      />
                    ) : (
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary">
                        {getInitials()}
                      </div>
                    )}
                    <div>
                      <div className="font-medium">
                        {profile?.full_name || "User"}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {profile?.email || ""}
                      </div>
                    </div>
                  </div>

                  <Link
                    href="/profile"
                    className="flex items-center gap-2 py-2 text-foreground hover:text-primary"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <User className="size-5" />
                    Profile
                  </Link>

                  <Link
                    href="/settings"
                    className="flex items-center gap-2 py-2 text-foreground hover:text-primary"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Settings className="size-5" />
                    Settings
                  </Link>

                  <button
                    onClick={() => {
                      signOut();
                      setMobileMenuOpen(false);
                    }}
                    className="flex items-center gap-2 py-2 text-destructive w-full text-left"
                  >
                    <LogOut className="size-5" />
                    Sign Out
                  </button>
                </>
              ) : (
                <div className="space-y-3">
                  <Button asChild className="w-full">
                    <Link
                      href="/login"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Log In
                    </Link>
                  </Button>
                  <Button asChild variant="outline" className="w-full">
                    <Link
                      href="/signup"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      Sign Up
                    </Link>
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
