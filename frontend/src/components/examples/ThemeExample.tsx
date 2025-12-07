/**
 * Example component showing how to use TradeBerg CSS Variables
 *
 * This demonstrates how components can use CSS variables for instant theme changes
 */

"use client";

export default function ThemeExample() {
  return (
    <div className="p-6 space-y-4">
      {/* Using TradeBerg variables directly */}
      <div
        style={{
          backgroundColor: "var(--tradeberg-card-bg)",
          color: "var(--tradeberg-text-primary)",
          border: "1px solid var(--tradeberg-card-border)",
          padding: "1rem",
          borderRadius: "0.5rem",
        }}
      >
        <h3 style={{ color: "var(--tradeberg-text-primary)" }}>
          Card using TradeBerg Variables
        </h3>
        <p style={{ color: "var(--tradeberg-text-secondary)" }}>
          This text uses secondary color variable
        </p>
        <button
          style={{
            backgroundColor: "var(--tradeberg-accent-color)",
            color: "white",
            padding: "0.5rem 1rem",
            borderRadius: "0.25rem",
            border: "none",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor =
              "var(--tradeberg-accent-hover)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor =
              "var(--tradeberg-accent-color)";
          }}
        >
          Accent Button
        </button>
      </div>

      {/* Using Tailwind classes that reference the variables */}
      <div className="bg-card text-card-foreground border border-border p-4 rounded-lg">
        <h3 className="text-foreground">Card using Tailwind Variables</h3>
        <p className="text-muted-foreground">
          These Tailwind classes automatically use the CSS variables
        </p>
      </div>
    </div>
  );
}
