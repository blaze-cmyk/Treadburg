"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
    const router = useRouter();

    useEffect(() => {
        // Create a new chat and redirect to it
        const createChat = async () => {
            try {
                const response = await fetch("/api/chat/create", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: "" }),
                });

                if (response.ok) {
                    const data = await response.json();
                    router.push(`/c/${data.chatId}`);
                } else {
                    console.error("Failed to create chat");
                }
            } catch (error) {
                console.error("Error creating chat:", error);
            }
        };

        createChat();
    }, [router]);

    return (
        <div className="flex items-center justify-center min-h-screen bg-[var(--tradeberg-bg)]">
            <div className="text-center">
                <h1 className="text-4xl font-bold text-white mb-4">TradeBerg</h1>
                <p className="text-gray-400">Creating your chat...</p>
            </div>
        </div>
    );
}
