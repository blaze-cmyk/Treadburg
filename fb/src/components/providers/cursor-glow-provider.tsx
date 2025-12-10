"use client";

import { useEffect } from "react";

/**
 * Cursor Glow Provider
 * Tracks mouse movement and updates CSS variables for the spotlight effect
 */
export default function CursorGlowProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    // Function to update mouse position CSS variables
    const handleMouseMove = (e: MouseEvent) => {
      document.documentElement.style.setProperty("--mouse-x", `${e.clientX}px`);
      document.documentElement.style.setProperty("--mouse-y", `${e.clientY}px`);
    };

    // Add event listener
    window.addEventListener("mousemove", handleMouseMove);

    // Initialize with off-screen position (hides glow before mouse enters)
    document.documentElement.style.setProperty("--mouse-x", "-1000px");
    document.documentElement.style.setProperty("--mouse-y", "-1000px");

    // Cleanup
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return <>{children}</>;
}
