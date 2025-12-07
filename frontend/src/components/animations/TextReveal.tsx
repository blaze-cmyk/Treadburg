"use client";

import { useEffect, useRef, ReactNode } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register ScrollTrigger plugin
if (typeof window !== "undefined") {
  gsap.registerPlugin(ScrollTrigger);
}

interface TextRevealProps {
  children: ReactNode;
  delay?: number;
  animateOnScroll?: boolean;
  splitBy?: "words" | "chars";
  triggerPosition?: string; // e.g., "75%"
  className?: string;
}

export default function TextReveal({
  children,
  delay = 0,
  animateOnScroll = true,
  splitBy = "words",
  triggerPosition = "75%",
  className = "",
}: TextRevealProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const text = container.textContent || "";

    // Clear container
    container.innerHTML = "";

    // Split text into words or characters
    const elements: HTMLElement[] = [];

    if (splitBy === "words") {
      const words = text.split(/\s+/);
      words.forEach((word, index) => {
        const span = document.createElement("span");
        span.textContent = word;
        span.style.display = "inline-block";
        span.style.opacity = "0";
        span.style.transform = "translateY(20px)";
        span.style.marginRight = index < words.length - 1 ? "0.25em" : "0";
        container.appendChild(span);
        elements.push(span);
      });
    } else {
      // Split by characters
      const chars = text.split("");
      chars.forEach((char, index) => {
        const span = document.createElement("span");
        span.textContent = char === " " ? "\u00A0" : char;
        span.style.display = "inline-block";
        span.style.opacity = "0";
        span.style.transform = "translateY(20px)";
        container.appendChild(span);
        elements.push(span);
      });
    }

    // Animation function
    const animate = () => {
      if (hasAnimated.current && animateOnScroll) return;
      hasAnimated.current = true;

      elements.forEach((element, index) => {
        gsap.to(element, {
          opacity: 1,
          y: 0,
          duration: 0.6,
          delay: delay + index * 0.03,
          ease: "power2.out",
        });
      });
    };

    if (animateOnScroll) {
      // Scroll-triggered animation
      ScrollTrigger.create({
        trigger: container,
        start: `top ${triggerPosition}`,
        onEnter: animate,
        once: true,
      });
    } else {
      // Immediate animation
      animate();
    }

    // Cleanup
    return () => {
      if (animateOnScroll) {
        ScrollTrigger.getAll().forEach((trigger) => {
          if (trigger.vars.trigger === container) {
            trigger.kill();
          }
        });
      }
    };
  }, [children, delay, animateOnScroll, splitBy, triggerPosition]);

  return (
    <div ref={containerRef} className={className}>
      {children}
    </div>
  );
}
