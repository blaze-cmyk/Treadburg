/**
 * TextReveal Component Usage Examples
 *
 * This file shows how to use the TextReveal component in different scenarios
 */

import TextReveal from "./TextReveal";

// Example 1: Basic scroll-triggered animation (default)
export function Example1() {
  return (
    <TextReveal>
      <h1>This text will animate on scroll at 75% viewport</h1>
    </TextReveal>
  );
}

// Example 2: Immediate animation (no scroll trigger)
export function Example2() {
  return (
    <TextReveal animateOnScroll={false}>
      <p>This text animates immediately when component mounts</p>
    </TextReveal>
  );
}

// Example 3: Character-by-character animation
export function Example3() {
  return (
    <TextReveal splitBy="chars" delay={0.1}>
      <h2>Each character animates individually</h2>
    </TextReveal>
  );
}

// Example 4: Custom trigger position
export function Example4() {
  return (
    <TextReveal triggerPosition="50%">
      <p>This triggers when element reaches 50% of viewport</p>
    </TextReveal>
  );
}

// Example 5: With custom styling
export function Example5() {
  return (
    <TextReveal className="text-center mb-8" delay={0.2}>
      <h1 className="text-4xl font-bold">Styled Heading</h1>
    </TextReveal>
  );
}

// Example 6: Multiple text reveals with different delays
export function Example6() {
  return (
    <div>
      <TextReveal delay={0}>
        <h2>First heading</h2>
      </TextReveal>
      <TextReveal delay={0.3}>
        <p>Second paragraph with delay</p>
      </TextReveal>
      <TextReveal delay={0.6}>
        <p>Third paragraph with more delay</p>
      </TextReveal>
    </div>
  );
}
