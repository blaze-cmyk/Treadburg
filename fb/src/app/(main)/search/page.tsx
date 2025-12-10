"use client";

import { motion } from "framer-motion";
import { Search as SearchIcon } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-4xl mx-auto px-4 py-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-8"
        >
          <h1 className="text-2xl font-semibold text-foreground mb-4">
            Search Your Trading Chats
          </h1>
          <p className="text-muted-foreground">
            Find stock analyses, trading strategies, and market insights across
            all your conversations.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-strong rounded-2xl p-6 mb-6"
        >
          <div className="relative">
            <SearchIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search for stocks, tickers, trading strategies, or market analysis..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-12 py-6 text-lg bg-transparent border-border"
            />
          </div>
        </motion.div>

        {searchQuery && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-strong rounded-2xl p-6"
          >
            <p className="text-muted-foreground text-center">
              Search results for "{searchQuery}" will appear here.
            </p>
          </motion.div>
        )}

        {!searchQuery && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-center py-12"
          >
            <SearchIcon className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
            <p className="text-muted-foreground">
              Start typing to search through your chat history
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
