import React, { useState, useRef, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { SearchBar } from './SearchBar';
import { MessageBlock } from './MessageBlock';
import { Message } from '../../types';
import { v4 as uuidv4 } from 'uuid';
import { chatApi } from '../../lib/api/backend';

export default function PerplexApp() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [hasStarted, setHasStarted] = useState(false);
    const [chatId, setChatId] = useState<string | null>(null);

    const bottomRef = useRef<HTMLDivElement>(null);

    const handleSearch = async (query: string, attachments: any[] = []) => {
        if (!query.trim() && attachments.length === 0) return;

        setHasStarted(true);
        setIsSearching(true);

        // Add User Message
        const userMsg: Message = {
            id: uuidv4(),
            role: 'user',
            content: query,
            attachments: attachments.length > 0 ? attachments : undefined
        };

        // Add Placeholder AI Message (Thinking)
        const aiMsgId = uuidv4();
        const aiMsg: Message = {
            id: aiMsgId,
            role: 'model',
            content: '',
            isThinking: true,
            sources: [],
            searchSteps: ['Initializing TradeBerg agent...']
        };

        setMessages(prev => [...prev, userMsg, aiMsg]);

        // Simulate stepping mechanism for UI "Working..." state
        const addStep = (step: string) => {
            setMessages(prev => prev.map(msg =>
                msg.id === aiMsgId
                    ? { ...msg, searchSteps: [...(msg.searchSteps || []), step] }
                    : msg
            ));
        };

        try {
            // Step 1: Search
            await new Promise(resolve => setTimeout(resolve, 800));
            addStep(`Searching for "${query}"...`);

            // Step 2: Read sources (simulated delay)
            await new Promise(resolve => setTimeout(resolve, 1200));
            addStep("Reading verified financial sources...");

            // Step 3: Synthesis
            await new Promise(resolve => setTimeout(resolve, 1000));
            addStep("Synthesizing analyst report...");

            // Backend Integration
            let currentChatId = chatId;
            if (!currentChatId) {
                // Create a new chat with an empty prompt to initialize the session
                const newChat = await chatApi.createChat("");

                if (newChat.data && newChat.data.chatId) {
                    currentChatId = newChat.data.chatId;
                    setChatId(currentChatId);
                } else {
                    console.error("Failed to create chat", newChat);
                    throw new Error("Failed to create chat session");
                }
            }

            const response = await chatApi.streamMessage(
                currentChatId!,
                query,
                attachments
            );

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });

                // Check for grounding metadata
                const metadataMatch = /<!-- GROUNDING_METADATA: ({.*}) -->/.exec(chunk);
                if (metadataMatch) {
                    try {
                        const metadata = JSON.parse(metadataMatch[1]);
                        if (metadata.groundingMetadata && metadata.groundingMetadata.groundingChunks) {
                            const sources = metadata.groundingMetadata.groundingChunks.map((c: any) => ({
                                title: c.web?.title || "Source",
                                url: c.web?.uri || ""
                            })).filter((s: any) => s.url);

                            setMessages(prev => prev.map(msg =>
                                msg.id === aiMsgId
                                    ? { ...msg, sources: sources, searchSteps: [...(msg.searchSteps || []), `Found ${sources.length} sources`] }
                                    : msg
                            ));
                        }
                    } catch (e) {
                        console.error("Error parsing metadata", e);
                    }
                }

                // Always append text content (stripping metadata block if present)
                const cleanChunk = chunk.replace(/<!-- GROUNDING_METADATA: .* -->/, '');
                if (cleanChunk) {
                    setMessages(prev => prev.map(msg =>
                        msg.id === aiMsgId
                            ? { ...msg, content: msg.content + cleanChunk }
                            : msg
                    ));
                }
            }

            // Mark as done thinking
            setMessages(prev => prev.map(msg =>
                msg.id === aiMsgId
                    ? { ...msg, isThinking: false }
                    : msg
            ));

        } catch (error) {
            console.error(error);
            setMessages(prev => prev.map(msg =>
                msg.id === aiMsgId
                    ? { ...msg, content: "Unable to retrieve financial data at this time. Please try again.", isThinking: false }
                    : msg
            ));
        } finally {
            setIsSearching(false);
        }
    };

    useEffect(() => {
        if (bottomRef.current) {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }
    }, [messages.length, messages[messages.length - 1]?.content]);

    return (
        <div className="min-h-screen bg-perplex-bg text-perplex-textMain font-sans selection:bg-perplex-accent/30">
            <Sidebar />

            <main className={`transition-all duration-500 ease-in-out pl-[60px] md:pl-[220px] ${hasStarted ? 'pt-8 pb-32' : 'h-screen flex items-center justify-center'}`}>

                {!hasStarted ? (
                    <div className="w-full max-w-2xl px-4 flex flex-col items-center gap-8 -mt-20 animate-in fade-in zoom-in-95 duration-700">
                        <h1 className="text-4xl md:text-5xl font-display font-medium text-center tracking-tight text-white/90">
                            Where knowledge begins
                        </h1>
                        <div className="w-full transform transition-all hover:scale-[1.01]">
                            <SearchBar
                                onSearch={handleSearch}
                                isLoading={isSearching}
                                isTyping={isSearching}
                            />
                        </div>

                        <div className="flex gap-4 text-xs text-perplex-textMuted mt-4">
                            <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-perplex-accent"></span> Accurate</span>
                            <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span> Real-time</span>
                            <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span> Verified</span>
                        </div>
                    </div>
                ) : (
                    <div className="w-full max-w-3xl mx-auto px-4">
                        {messages.map((msg, idx) => (
                            <MessageBlock key={msg.id} message={msg} isLast={idx === messages.length - 1} />
                        ))}
                        <div ref={bottomRef} className="h-4" />

                        {/* Sticky Search Bar for Thread */}
                        <div className="fixed bottom-0 right-0 left-[60px] md:left-[220px] p-4 bg-gradient-to-t from-perplex-bg via-perplex-bg to-transparent z-40">
                            <SearchBar
                                onSearch={handleSearch}
                                isLoading={isSearching}
                                isTyping={isSearching}
                            />
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
}
