/**
 * TradeBerg Theme Management
 * Handles live theming with CSS variables and localStorage
 */

const THEME_STORAGE_KEY = "tradeberg-theme";

export type ThemeMode = "light" | "dark";

/**
 * Enable dark mode by adding class to body
 */
export function enableDarkMode(): void {
  if (typeof window === "undefined") return;

  document.body.classList.add("dark-theme");
  document.documentElement.classList.add("dark");
  localStorage.setItem(THEME_STORAGE_KEY, "dark");
}

/**
 * Enable light mode by removing class from body
 */
export function enableLightMode(): void {
  if (typeof window === "undefined") return;

  document.body.classList.remove("dark-theme");
  document.documentElement.classList.remove("dark");
  localStorage.setItem(THEME_STORAGE_KEY, "light");
}

/**
 * Toggle between light and dark mode
 */
export function toggleTheme(): void {
  if (typeof window === "undefined") return;

  const isDark = document.body.classList.contains("dark-theme");
  if (isDark) {
    enableLightMode();
  } else {
    enableDarkMode();
  }
}

/**
 * Get current theme from localStorage or system preference
 */
export function getStoredTheme(): ThemeMode | null {
  if (typeof window === "undefined") return null;

  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  return stored === "dark" || stored === "light" ? (stored as ThemeMode) : null;
}

/**
 * Initialize theme on page load
 * Checks localStorage first, then applies theme
 */
export function initializeTheme(): void {
  if (typeof window === "undefined") return;

  const storedTheme = getStoredTheme();

  if (storedTheme === "dark") {
    enableDarkMode();
  } else if (storedTheme === "light") {
    enableLightMode();
  } else {
    // Default to dark mode if no preference stored
    enableDarkMode();
  }
}

/**
 * Get current theme state
 */
export function getCurrentTheme(): ThemeMode {
  if (typeof window === "undefined") return "dark";

  return document.body.classList.contains("dark-theme") ? "dark" : "light";
}
