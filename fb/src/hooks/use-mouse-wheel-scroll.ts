"use client";

import { useEffect, useRef } from "react";

/**
 * Hook to enable mouse wheel scrolling on a specific element
 * Only scrolls when mouse is over the element
 * Prevents page scroll when scrolling within the element
 */
export function useMouseWheelScroll<T extends HTMLElement = HTMLDivElement>() {
  const scrollRef = useRef<T>(null);

  useEffect(() => {
    const element = scrollRef.current;
    if (!element) return;

    const handleWheel = (e: WheelEvent) => {
      // Check if mouse is over this element
      const rect = element.getBoundingClientRect();
      const isOverElement =
        e.clientX >= rect.left &&
        e.clientX <= rect.right &&
        e.clientY >= rect.top &&
        e.clientY <= rect.bottom;

      if (!isOverElement) return;

      // Check if element can scroll
      const canScrollVertical = element.scrollHeight > element.clientHeight;
      const canScrollHorizontal = element.scrollWidth > element.clientWidth;

      // Handle vertical scrolling
      if (canScrollVertical && Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        const isAtTop = element.scrollTop <= 0;
        const isAtBottom =
          element.scrollTop + element.clientHeight >= element.scrollHeight - 1;

        // If we can scroll in the direction requested, handle it
        if ((!isAtTop && e.deltaY < 0) || (!isAtBottom && e.deltaY > 0)) {
          e.preventDefault();
          e.stopPropagation();
          element.scrollBy({
            top: e.deltaY,
            behavior: "auto",
          });
        } else if ((isAtTop && e.deltaY < 0) || (isAtBottom && e.deltaY > 0)) {
          // At boundary, prevent default to stop page scroll
          e.preventDefault();
          e.stopPropagation();
        }
      }
      // Handle horizontal scrolling
      else if (canScrollHorizontal && Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
        const isAtLeft = element.scrollLeft <= 0;
        const isAtRight =
          element.scrollLeft + element.clientWidth >= element.scrollWidth - 1;

        if ((!isAtLeft && e.deltaX < 0) || (!isAtRight && e.deltaX > 0)) {
          e.preventDefault();
          e.stopPropagation();
          element.scrollBy({
            left: e.deltaX,
            behavior: "auto",
          });
        } else if ((isAtLeft && e.deltaX < 0) || (isAtRight && e.deltaX > 0)) {
          e.preventDefault();
          e.stopPropagation();
        }
      }
    };

    // Use passive: false to allow preventDefault
    element.addEventListener("wheel", handleWheel, { passive: false });

    return () => {
      element.removeEventListener("wheel", handleWheel);
    };
  }, []);

  return scrollRef;
}
