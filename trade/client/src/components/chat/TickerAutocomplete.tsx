"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { TrendingUp, Coins, Search } from "lucide-react";
import clsx from "clsx";

export interface Ticker {
  symbol: string;
  name: string;
  type: "stock" | "crypto";
  exchange?: string;
}

// Mock ticker data - In production, this would come from an API
const TICKERS: Ticker[] = [
  // Major Stocks
  { symbol: "AAPL", name: "Apple Inc.", type: "stock", exchange: "NASDAQ" },
  { symbol: "GOOGL", name: "Alphabet Inc.", type: "stock", exchange: "NASDAQ" },
  {
    symbol: "MSFT",
    name: "Microsoft Corporation",
    type: "stock",
    exchange: "NASDAQ",
  },
  {
    symbol: "AMZN",
    name: "Amazon.com Inc.",
    type: "stock",
    exchange: "NASDAQ",
  },
  { symbol: "TSLA", name: "Tesla Inc.", type: "stock", exchange: "NASDAQ" },
  {
    symbol: "META",
    name: "Meta Platforms Inc.",
    type: "stock",
    exchange: "NASDAQ",
  },
  {
    symbol: "NVDA",
    name: "NVIDIA Corporation",
    type: "stock",
    exchange: "NASDAQ",
  },
  {
    symbol: "JPM",
    name: "JPMorgan Chase & Co.",
    type: "stock",
    exchange: "NYSE",
  },
  { symbol: "V", name: "Visa Inc.", type: "stock", exchange: "NYSE" },
  { symbol: "JNJ", name: "Johnson & Johnson", type: "stock", exchange: "NYSE" },
  { symbol: "WMT", name: "Walmart Inc.", type: "stock", exchange: "NYSE" },
  {
    symbol: "PG",
    name: "Procter & Gamble Co.",
    type: "stock",
    exchange: "NYSE",
  },
  { symbol: "MA", name: "Mastercard Inc.", type: "stock", exchange: "NYSE" },
  {
    symbol: "DIS",
    name: "The Walt Disney Company",
    type: "stock",
    exchange: "NYSE",
  },
  { symbol: "NFLX", name: "Netflix Inc.", type: "stock", exchange: "NASDAQ" },
  {
    symbol: "AMD",
    name: "Advanced Micro Devices",
    type: "stock",
    exchange: "NASDAQ",
  },
  {
    symbol: "INTC",
    name: "Intel Corporation",
    type: "stock",
    exchange: "NASDAQ",
  },
  {
    symbol: "BAC",
    name: "Bank of America Corp.",
    type: "stock",
    exchange: "NYSE",
  },
  {
    symbol: "XOM",
    name: "Exxon Mobil Corporation",
    type: "stock",
    exchange: "NYSE",
  },
  {
    symbol: "CSCO",
    name: "Cisco Systems Inc.",
    type: "stock",
    exchange: "NASDAQ",
  },

  // Major Cryptocurrencies
  { symbol: "BTC", name: "Bitcoin", type: "crypto" },
  { symbol: "ETH", name: "Ethereum", type: "crypto" },
  { symbol: "BNB", name: "Binance Coin", type: "crypto" },
  { symbol: "SOL", name: "Solana", type: "crypto" },
  { symbol: "XRP", name: "Ripple", type: "crypto" },
  { symbol: "ADA", name: "Cardano", type: "crypto" },
  { symbol: "DOGE", name: "Dogecoin", type: "crypto" },
  { symbol: "DOT", name: "Polkadot", type: "crypto" },
  { symbol: "MATIC", name: "Polygon", type: "crypto" },
  { symbol: "AVAX", name: "Avalanche", type: "crypto" },
  { symbol: "LINK", name: "Chainlink", type: "crypto" },
  { symbol: "UNI", name: "Uniswap", type: "crypto" },
  { symbol: "LTC", name: "Litecoin", type: "crypto" },
  { symbol: "ATOM", name: "Cosmos", type: "crypto" },
  { symbol: "ETC", name: "Ethereum Classic", type: "crypto" },
];

interface TickerAutocompleteProps {
  value: string;
  cursorPosition: number;
  onSelect: (ticker: Ticker) => void;
  onClose: () => void;
  inputRef: React.RefObject<HTMLInputElement>;
  showTickerAutocomplete?: boolean;
}

export default function TickerAutocomplete({
  value,
  cursorPosition,
  onSelect,
  onClose,
  inputRef,
  showTickerAutocomplete = true,
}: TickerAutocompleteProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const popupRef = useRef<HTMLDivElement>(null);

  // Extract query after @ symbol
  const query = useMemo(() => {
    const textBeforeCursor = value.substring(0, cursorPosition);
    const atIndex = textBeforeCursor.lastIndexOf("@");
    if (atIndex === -1) return "";
    return textBeforeCursor
      .substring(atIndex + 1)
      .toUpperCase()
      .trim();
  }, [value, cursorPosition]);

  // Filter tickers based on query
  const filteredTickers = useMemo(() => {
    if (!query) return TICKERS.slice(0, 10); // Show top 10 if no query

    return TICKERS.filter(
      (ticker) =>
        ticker.symbol.toUpperCase().startsWith(query) ||
        ticker.name.toUpperCase().includes(query.toUpperCase())
    ).slice(0, 10);
  }, [query]);

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (filteredTickers.length === 0) return;

      switch (e.key) {
        case "ArrowDown":
          e.preventDefault();
          setSelectedIndex((prev) =>
            prev < filteredTickers.length - 1 ? prev + 1 : prev
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setSelectedIndex((prev) => (prev > 0 ? prev - 1 : 0));
          break;
        case "Enter":
        case "Tab":
          e.preventDefault();
          if (filteredTickers[selectedIndex]) {
            onSelect(filteredTickers[selectedIndex]);
          }
          break;
        case "Escape":
          e.preventDefault();
          onClose();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [filteredTickers, selectedIndex, onSelect, onClose]);

  // Reset selected index when filtered results change
  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  // Calculate popup position
  const [position, setPosition] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (!inputRef.current || !showTickerAutocomplete) return;

    const input = inputRef.current;
    const rect = input.getBoundingClientRect();
    const textBeforeCursor = value.substring(0, cursorPosition);
    const atIndex = textBeforeCursor.lastIndexOf("@");

    if (atIndex === -1) {
      setPosition({ top: rect.bottom + 8, left: rect.left });
      return;
    }

    // Create a temporary span to measure text width
    const span = document.createElement("span");
    span.style.position = "absolute";
    span.style.visibility = "hidden";
    span.style.whiteSpace = "pre";
    span.style.font = window.getComputedStyle(input).font;
    span.style.padding = window.getComputedStyle(input).padding;
    span.textContent = textBeforeCursor.substring(0, atIndex + 1);
    document.body.appendChild(span);

    const textWidth = span.offsetWidth;
    document.body.removeChild(span);

    // Position popup below input, aligned with @ symbol
    setPosition({
      top: rect.bottom + 8,
      left: Math.min(rect.left + textWidth, window.innerWidth - 320), // Keep within viewport
    });
  }, [value, cursorPosition, inputRef, showTickerAutocomplete]);

  if (!showTickerAutocomplete || filteredTickers.length === 0) return null;

  return (
    <motion.div
      ref={popupRef}
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className="fixed z-50 min-w-[280px] max-w-[320px] max-h-[300px] overflow-y-auto show-scrollbar-on-hover glass-strong rounded-lg border border-[var(--tradeberg-glass-border)] shadow-lg"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
      onMouseDown={(e) => e.preventDefault()} // Prevent input blur on click
    >
      <div className="p-2">
        <div className="flex items-center gap-2 px-2 py-1.5 mb-1">
          <Search className="w-4 h-4 text-muted-foreground" />
          <span className="text-xs text-muted-foreground">
            {query ? `Searching for "${query}"` : "Popular tickers"}
          </span>
        </div>
        <div className="space-y-1">
          {filteredTickers.map((ticker, index) => (
            <motion.button
              key={`${ticker.type}-${ticker.symbol}`}
              onClick={() => onSelect(ticker)}
              className={clsx(
                "w-full flex items-center gap-3 px-3 py-2 rounded-md text-left transition-colors",
                index === selectedIndex
                  ? "bg-[var(--tradeberg-accent-color)]/20 text-foreground"
                  : "hover:bg-[var(--tradeberg-card-bg)] text-foreground"
              )}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {ticker.type === "crypto" ? (
                <Coins className="w-4 h-4 text-yellow-500 flex-shrink-0" />
              ) : (
                <TrendingUp className="w-4 h-4 text-green-500 flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm">{ticker.symbol}</span>
                  {ticker.exchange && (
                    <span className="text-xs text-muted-foreground">
                      {ticker.exchange}
                    </span>
                  )}
                </div>
                <div className="text-xs text-muted-foreground truncate">
                  {ticker.name}
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
