"use client";

import { TradeView } from "@/components/chat/TradebergChat";

export const dynamic = 'force-dynamic';

export default function TradePage() {
  return (
    <div className="flex-1 h-full bg-background flex flex-col">
      <TradeView />
    </div>
  );
}
