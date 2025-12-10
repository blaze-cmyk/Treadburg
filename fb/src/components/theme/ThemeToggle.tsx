"use client";

import { useTheme } from "next-themes";
import {
  useThemeAnimation,
  ThemeAnimationType,
} from "@space-man/react-theme-animation";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  toggleTheme as toggleTradebergTheme,
  getCurrentTheme,
} from "@/lib/theme";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Use theme animation hook with blur circle effect, integrated with next-themes
  const { ref, toggleTheme: toggleAnimation } = useThemeAnimation({
    theme: (theme as "light" | "dark") || "dark",
    onThemeChange: (newTheme) => {
      setTheme(newTheme);
    },
    animationType: ThemeAnimationType.BLUR_CIRCLE,
    blurAmount: 8,
    duration: 600,
    defaultTheme: "dark",
  });

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <button className="rounded-[100%] hover:bg-gray-100 dark:hover:bg-gray-800 p-2 cursor-pointer">
        <Sun
          height={20}
          width={20}
          className="text-gray-700 dark:text-gray-300"
        />
      </button>
    );
  }

  const handleToggle = async () => {
    // Toggle theme using TradeBerg theme system (CSS variables + body class)
    toggleTradebergTheme();

    // Also update next-themes for compatibility
    const newTheme = getCurrentTheme();
    setTheme(newTheme);

    // Trigger animation hook's toggle for smooth transition
    if (toggleAnimation) {
      await toggleAnimation();
    }
  };

  const currentTheme = getCurrentTheme();

  return (
    <motion.button
      ref={ref as React.RefObject<HTMLButtonElement>}
      onClick={handleToggle}
      className="rounded-[100%] hover:bg-gray-100 dark:hover:bg-gray-800 p-2 cursor-pointer transition-colors"
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      aria-label="Toggle theme"
    >
      {currentTheme === "dark" ? (
        <Sun height={20} width={20} className="text-gray-300" />
      ) : (
        <Moon height={20} width={20} className="text-gray-700" />
      )}
    </motion.button>
  );
}
