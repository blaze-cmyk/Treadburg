"use client";

import { motion, Variants } from "framer-motion";
import { ReactNode } from "react";

interface StaggeredContainerProps {
  children: ReactNode;
  className?: string;
  staggerDelay?: number;
  itemDelay?: number;
}

/**
 * StaggeredContainer - Creates staggered enter animations for children
 *
 * @param staggerDelay - Delay between each child animation (default: 0.1)
 * @param itemDelay - Initial delay before first animation (default: 0)
 */
export default function StaggeredContainer({
  children,
  className = "",
  staggerDelay = 0.1,
  itemDelay = 0,
}: StaggeredContainerProps) {
  // Container animation variants
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: staggerDelay,
        delayChildren: itemDelay,
      },
    },
  };

  // Item animation variants
  const itemVariants: Variants = {
    hidden: {
      opacity: 0,
      y: 20,
      scale: 0.95,
    },
    show: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: [0.25, 0.46, 0.45, 0.94], // Custom easing for smooth animation
      },
    },
  };

  return (
    <motion.div
      className={className}
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {children}
    </motion.div>
  );
}
