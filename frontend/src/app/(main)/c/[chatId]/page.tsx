"use client";

import { use } from "react";
import { ChatInterface } from "@/components/chat/TradebergChat";

export default function ChatPage({
  params,
}: {
  params: Promise<{ chatId: string }>;
}) {
  const { chatId } = use(params);

  return (
    <div className="flex-1 h-full bg-background flex flex-col">
      <ChatInterface initialChatId={chatId} mode="chat" />
    </div>
  );
}
