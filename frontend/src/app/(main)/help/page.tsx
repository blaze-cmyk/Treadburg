"use client";

import { motion } from "framer-motion";
import {
  HelpCircle,
  MessageSquare,
  BookOpen,
  Mail,
  FileText,
} from "lucide-react";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";
import Link from "next/link";

export default function HelpPage() {
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  const helpSections = [
    {
      icon: BookOpen,
      title: "Getting Started",
      description: "Learn the basics of using TradeBerg for trading analysis",
      items: [
        "How to analyze stock prices",
        "Understanding technical indicators",
        "Creating your first trading strategy",
      ],
    },
    {
      icon: MessageSquare,
      title: "Chat Features",
      description: "Make the most of TradeBerg's AI chat assistant",
      items: [
        "Using @ mentions for ticker symbols",
        "Uploading files for analysis",
        "Referencing previous chats",
      ],
    },
    {
      icon: FileText,
      title: "Trading Strategies",
      description: "Explore advanced trading features",
      items: [
        "RSI and MACD indicators",
        "Portfolio management",
        "Market sentiment analysis",
      ],
    },
  ];

  return (
    <div
      ref={scrollRef}
      className="flex flex-col h-full bg-background overflow-y-auto show-scrollbar-on-hover"
    >
      <div className="flex-1 flex flex-col items-center justify-center min-h-[100vh] px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-4xl"
        >
          {/* Header */}
          <div className="text-center mb-12">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[var(--tradeberg-accent-color)]/10 mb-4"
            >
              <HelpCircle className="w-8 h-8 text-[var(--tradeberg-accent-color)]" />
            </motion.div>
            <h1 className="text-4xl font-bold text-foreground mb-4">
              Help & Support
            </h1>
            <p className="text-lg text-muted-foreground">
              Get help with TradeBerg and learn how to make the most of your
              trading assistant
            </p>
          </div>

          {/* Help Sections */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {helpSections.map((section, index) => {
              const Icon = section.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="glass-strong rounded-2xl p-6 hover:scale-105 transition-transform"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-lg bg-[var(--tradeberg-accent-color)]/10">
                      <Icon className="w-6 h-6 text-[var(--tradeberg-accent-color)]" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground">
                      {section.title}
                    </h3>
                  </div>
                  <p className="text-muted-foreground mb-4">
                    {section.description}
                  </p>
                  <ul className="space-y-2">
                    {section.items.map((item, itemIndex) => (
                      <li
                        key={itemIndex}
                        className="text-sm text-foreground flex items-start gap-2"
                      >
                        <span className="text-[var(--tradeberg-accent-color)] mt-1">
                          •
                        </span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              );
            })}
          </div>

          {/* Contact Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="glass-strong rounded-2xl p-8 text-center"
          >
            <Mail className="w-12 h-12 text-[var(--tradeberg-accent-color)] mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              Need More Help?
            </h2>
            <p className="text-muted-foreground mb-6">
              Contact our support team for personalized assistance
            </p>
            <div className="flex gap-4 justify-center">
              <Link
                href="mailto:support@tradeberg.com"
                className="px-6 py-3 bg-[var(--tradeberg-accent-color)] text-white rounded-lg hover:opacity-90 transition-opacity"
              >
                Email Support
              </Link>
              <Link
                href="/"
                className="px-6 py-3 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-glass-border)] text-foreground rounded-lg hover:opacity-80 transition-opacity"
              >
                Back to Dashboard
              </Link>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
