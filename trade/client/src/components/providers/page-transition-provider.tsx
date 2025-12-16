"use client";

import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

interface PageTransitionProviderProps {
  children: ReactNode;
}

/**
 * PageTransitionProvider - Provides smooth page transitions using Framer Motion
 *
 * This component wraps page content and applies fade-in/fade-out animations
 * when navigating between routes in Next.js App Router.
 *
 * Uses AnimatePresence with mode="wait" to ensure the exit animation completes
 * before the new page enters, preventing jarring transitions.
 */
export default function PageTransitionProvider({
  children,
}: PageTransitionProviderProps) {
  const pathname = usePathname();

  // Page transition variants
  const pageVariants = {
    initial: {
      opacity: 0,
      y: 10, // Slight slide up for smoother effect
    },
    animate: {
      opacity: 1,
      y: 0,
    },
    exit: {
      opacity: 0,
      y: -10, // Slight slide down on exit
    },
  };

  const pageTransition = {
    duration: 0.3,
    ease: [0.25, 0.46, 0.45, 0.94], // Custom easing for smooth animation
  };

  return (
    <AnimatePresence mode="wait">
      {/* The key is CRITICAL - it tells AnimatePresence when the page changes */}
      <motion.div
        key={pathname}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={pageTransition}
        className="w-full h-full flex-1"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
