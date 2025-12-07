"use client";

import { motion } from "framer-motion";
import { BookOpen, FileText, Folder, Clock } from "lucide-react";
import Link from "next/link";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";

const mockLibraryItems = [
  {
    id: "1",
    title: "Technical Analysis Guide",
    type: "chat",
    lastAccessed: "2 days ago",
    preview: "Understanding RSI, MACD, and Bollinger Bands...",
  },
  {
    id: "2",
    title: "Portfolio Strategy 2024",
    type: "document",
    lastAccessed: "1 week ago",
    preview: "Long-term investment strategies and risk management...",
  },
  {
    id: "3",
    title: "Crypto Trading Strategies",
    type: "folder",
    lastAccessed: "3 days ago",
    preview: "Collection of cryptocurrency trading strategies...",
  },
];

export default function LibraryPage() {
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-6xl mx-auto px-4 py-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-2xl font-semibold text-foreground mb-2">
            Library
          </h1>
          <p className="text-muted-foreground">
            Access your saved trading strategies, analysis reports, and market
            research.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockLibraryItems.map((item, index) => {
            const Icon =
              item.type === "chat"
                ? BookOpen
                : item.type === "document"
                ? FileText
                : Folder;

            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="glass-strong rounded-2xl p-6 hover:scale-105 transition-transform cursor-pointer"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                    <Icon className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1">
                      {item.title}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>{item.lastAccessed}</span>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {item.preview}
                </p>
              </motion.div>
            );
          })}
        </div>

        {mockLibraryItems.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <BookOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
            <p className="text-muted-foreground mb-4">Your library is empty</p>
            <Link
              href="/"
              className="text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              Start a new chat
            </Link>
          </motion.div>
        )}
      </div>
    </div>
  );
}
