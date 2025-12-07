"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
    const router = useRouter();
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Create a new chat and redirect to it
        const createChat = async () => {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

                const response = await fetch("/api/chat/create", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: "" }),
                    signal: controller.signal,
                });

                clearTimeout(timeoutId);

                if (response.ok) {
                    const data = await response.json();
                    console.log("Chat created:", data);
                    
                    // Check if we have a chatId (even if there's an error message)
                    if (data.chatId) {
                        router.push(`/c/${data.chatId}`);
                    } else {
                        setError("No chat ID received. Redirecting...");
                        setTimeout(() => router.push("/pricing"), 2000);
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    console.error("Failed to create chat:", errorData);
                    setError("Failed to create chat. Please try again.");
                    // Redirect to pricing page as fallback
                    setTimeout(() => router.push("/pricing"), 2000);
                }
            } catch (error) {
                console.error("Error creating chat:", error);
                setError("Connection error. Redirecting...");
                // Redirect to pricing page as fallback
                setTimeout(() => router.push("/pricing"), 2000);
            }
        };

        createChat();
    }, [router]);

    return (
        <div className="flex items-center justify-center min-h-screen bg-[var(--tradeberg-bg)]">
            <div className="text-center">
                <h1 className="text-4xl font-bold text-white mb-4">TradeBerg</h1>
                {error ? (
                    <p className="text-red-400">{error}</p>
                ) : (
                    <p className="text-gray-400">Creating your chat...</p>
                )}
            </div>
        </div>
    );
}
