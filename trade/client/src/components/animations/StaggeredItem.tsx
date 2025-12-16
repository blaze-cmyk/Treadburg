"use client";

import { motion, Variants } from "framer-motion";
import { ReactNode } from "react";

interface StaggeredItemProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  customVariants?: Variants;
}

/**
 * StaggeredItem - Individual item for staggered animations
 * Use this when you need more control over individual items
 */
export default function StaggeredItem({
  children,
  className = "",
  delay = 0,
  customVariants,
}: StaggeredItemProps) {
  const defaultVariants: Variants = {
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
        delay: delay,
        ease: [0.25, 0.46, 0.45, 0.94],
      },
    },
  };

  const variants = customVariants || defaultVariants;

  return (
    <motion.div
      className={className}
      variants={variants}
      initial="hidden"
      animate="show"
    >
      {children}
    </motion.div>
  );
}
