"use client";
import { SessionProvider } from "next-auth/react";
import { ThemeProvider as NextThemeProvider } from "next-themes";
import { useEffect } from "react";
import { initializeTheme } from "@/lib/theme";

export default function ThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    // Initialize TradeBerg theme system on mount
    initializeTheme();
  }, []);

  return (
    <SessionProvider>
      <NextThemeProvider
        attribute="class"
        defaultTheme="dark"
        enableSystem={false}
        storageKey="tradeberg-theme"
        forcedTheme={undefined}
      >
        {children}
      </NextThemeProvider>
    </SessionProvider>
  );
}
