"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Home,
    Sparkle,
    X,
    Paperclip,
    Globe,
    Camera,
    History,
    Mic,
    ArrowUp,
    Monitor,
    Sun,
    Moon,
    Search,
} from "lucide-react";
import { useTheme as useNextTheme } from "next-themes";
import { chatApi } from "@/lib/api/backend";
import Link from "next/link";
import { MessageBlock } from "./MessageBlock";
import { Message } from "../../types";
import { v4 as uuidv4 } from 'uuid';

// ---------------------------------------------------------------------------
// Main Chat Interface
// ---------------------------------------------------------------------------

type Attachment =
    | { type: "image"; data: string }
    | { type: "url"; data: string }
    | { type: "file"; data: string };

// ---------------------------------------------------------------------------
// Empty state + suggestions
// ---------------------------------------------------------------------------

function EmptyState({ onSearch, children }: { onSearch: (query: string) => void; children: React.ReactNode }) {
    return (
        <div className="flex-1 flex flex-col items-center justify-center -mt-20 animate-in fade-in zoom-in-95 duration-700 min-h-[60vh] w-full max-w-3xl mx-auto px-4">
            <h1 className="text-4xl md:text-5xl font-medium text-center tracking-tight text-[var(--tradeberg-text-primary)] mb-8">
                Where analysis begins
            </h1>

            {/* Prompt Tray (Centered) */}
            <div className="w-full mb-8">
                {children}
            </div>

            {/* Suggested Questions */}
            <div className="flex flex-wrap gap-3 justify-center max-w-2xl px-4 mb-8">
                <SuggestionPill label="NVDA earnings analysis" onClick={() => onSearch("NVDA earnings analysis")} />
                <SuggestionPill label="Is TSLA undervalued?" onClick={() => onSearch("Is TSLA undervalued?")} />
                <SuggestionPill label="Bitcoin price forecast" onClick={() => onSearch("Bitcoin price forecast")} />
                <SuggestionPill label="Macroeconomic outlook 2025" onClick={() => onSearch("Macroeconomic outlook 2025")} />
            </div>

            {/* Indicators */}
            <div className="flex gap-4 text-xs text-[var(--tradeberg-text-secondary)]">
                <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-[var(--tradeberg-accent-color)]"></span> Accurate</span>
                <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span> Real-time</span>
                <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span> Verified</span>
            </div>
        </div>
    );
}

const SuggestionPill = ({ label, onClick }: { label: string, onClick: () => void }) => (
    <button
        onClick={onClick}
        className="flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] text-[var(--tradeberg-text-secondary)] text-sm hover:bg-[var(--tradeberg-glass-bg)] hover:text-[var(--tradeberg-text-primary)] transition-all duration-200"
    >
        <Search size={14} />
        <span>{label}</span>
    </button>
);

function MessageList({
    messages,
    isLoading,
    scrollRef,
    onSearch,
}: {
    messages: Message[];
    isLoading: boolean;
    onImageClick: (url: string) => void;
    scrollRef: React.RefObject<HTMLDivElement | null>;
    onSearch: (query: string) => void;
}) {

    useEffect(() => {
        const node = scrollRef.current;
        if (node) {
            node.scrollTop = node.scrollHeight;
        }
    }, [messages, isLoading, scrollRef]);

    return (
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-6 scroll-smooth pb-32">
            <div className="w-full max-w-3xl mx-auto py-6 min-h-full flex flex-col">
                {messages.map((msg, idx) => (
                    <MessageBlock
                        key={msg.id}
                        message={msg}
                        isLast={idx === messages.length - 1}
                    />
                ))}
                <div className="h-4" />
            </div>
        </div>
    );
}

export function ChatInterface({
    initialChatId,
    showUpgrade,
    onCloseChat,
    mode,
}: {
    initialChatId?: string;
    showUpgrade?: boolean;
    onCloseChat?: () => void;
    mode?: "chat" | "trade";
}) {
    const [chatId, setChatId] = useState<string | null>(initialChatId ?? null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [attachments, setAttachments] = useState<any[]>([]);
    const [isWebpageModalOpen, setIsWebpageModalOpen] = useState(false);
    const [previewImage, setPreviewImage] = useState<string | null>(null);
    const messageScrollRef = useRef<HTMLDivElement | null>(null);
    const [abortController, setAbortController] = useState<AbortController | null>(null);

    // Load history when opening an existing chat
    useEffect(() => {
        if (!initialChatId) return;

        const loadHistory = async () => {
            const res = await chatApi.getMessages(initialChatId);
            if (res.error || !Array.isArray(res.data)) return;

            const history: Message[] =
                res.data.map((m: any) => ({
                    id: m.id || uuidv4(),
                    role: m.role === "assistant" ? "model" : "user",
                    content: m.content ?? "",
                })) ?? [];

            setMessages(history);
        };

        loadHistory();
    }, [initialChatId]);

    // Helper to add search steps to the latest AI message
    const addStep = (msgId: string, step: string) => {
        setMessages(prev => prev.map(msg =>
            msg.id === msgId
                ? { ...msg, searchSteps: [...(msg.searchSteps || []), step] }
                : msg
        ));
    };

    const handleSubmit = async (prompt: string) => {
        if (isLoading || (!prompt.trim() && attachments.length === 0)) return;

        const currentAttachments = attachments;
        const userMsgId = uuidv4();

        // 1. Add User Message
        const userMsg: Message = {
            id: userMsgId,
            role: "user",
            content: prompt,
            // attachments: currentAttachments // TODO map if needed
        };

        // 2. Add AI Placeholder (Thinking State)
        const aiMsgId = uuidv4();
        const aiMsg: Message = {
            id: aiMsgId,
            role: "model",
            content: "",
            isThinking: true,
            sources: [],
            searchSteps: ['Initializing TradeBerg agent...']
        };

        setMessages((prev) => [...prev, userMsg, aiMsg]);
        setAttachments([]);
        setIsLoading(true);

        let activeChatId = chatId;
        let fullContent = "";

        try {
            // Create chat on backend if it doesn't exist
            if (!activeChatId) {
                const res = await chatApi.createChat(prompt);
                if (res.error || !res.data?.chatId) {
                    setMessages(prev => prev.filter(m => m.id !== aiMsgId));
                    setIsLoading(false);
                    return;
                }
                activeChatId = String(res.data.chatId);
                setChatId(activeChatId);
            }

            // --- SIMULATE PERPLEXITY STEPS ---
            // This gives immediate visual feedback while the backend connects
            setTimeout(() => addStep(aiMsgId, `Searching for "${prompt}"...`), 600);
            setTimeout(() => addStep(aiMsgId, "Reading verified financial sources..."), 1400);
            setTimeout(() => addStep(aiMsgId, "Synthesizing analyst report..."), 2200);

            // --- STREAMING LOGIC ---
            if (abortController) abortController.abort();
            const controller = new AbortController();
            setAbortController(controller);

            const response = await chatApi.streamMessage(
                activeChatId as string,
                prompt,
                currentAttachments,
                controller.signal,
                mode
            );

            const reader = response.body?.getReader();
            if (!reader) throw new Error("No reader");

            const decoder = new TextDecoder();

            // Loop to read stream chunks
            // eslint-disable-next-line no-constant-condition
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });

                // CHECK FOR HIDDEN GROUNDING METADATA
                // The backend sends const sourceRegex = //;
                const sourceRegex = /<!-- GROUNDING_METADATA: (.*?) -->/;
                const match = chunk.match(sourceRegex);

                let cleanChunk = chunk;

                if (match) {
                    try {
                        const metadataJson = JSON.parse(match[1]);
                        // If metadata is { groundingChunks: [...] }
                        if (metadataJson.groundingChunks) {
                            const foundSources = metadataJson.groundingChunks.map((c: any) => ({
                                title: c.web?.title || "Source",
                                url: c.web?.uri || ""
                            })).filter((s: any) => s.url);

                            // Update state with sources
                            setMessages(prev => prev.map(msg =>
                                msg.id === aiMsgId
                                    ? { ...msg, sources: foundSources, searchSteps: [...(msg.searchSteps || []), `Found ${foundSources.length} verified sources`] }
                                    : msg
                            ));
                        }
                    } catch (e) {
                        console.error("Error parsing grounding metadata", e);
                    }
                    // Remove the hidden block from visible content
                    cleanChunk = chunk.replace(sourceRegex, '');
                }

                fullContent += cleanChunk;

                // Update content in real-time
                setMessages(prev => prev.map(msg =>
                    msg.id === aiMsgId
                        ? { ...msg, content: fullContent }
                        : msg
                ));
            }

            // Mark thinking as done
            setMessages(prev => prev.map(msg =>
                msg.id === aiMsgId
                    ? { ...msg, isThinking: false, searchSteps: [...(msg.searchSteps || []), "Analysis complete"] }
                    : msg
            ));

        } catch (err: any) {
            if (err.name === "AbortError") {
                console.log("Stream aborted");
            } else {
                console.error("Stream error", err);
                setMessages(prev => prev.map(msg =>
                    msg.id === aiMsgId
                        ? { ...msg, isThinking: false, content: "Error: Unable to retrieve financial data at this time." }
                        : msg
                ));
            }
        } finally {
            setIsLoading(false);
            setAbortController(null);
        }
    };

    const handleStopStreaming = () => {
        if (abortController) {
            abortController.abort();
            setAbortController(null);
            setIsLoading(false);
        }
    };

    const handleSetAttachment = (att: any | null) => {
        if (!att) return;
        setAttachments((prev) => [...prev, att]);
    };

    return (
        <div className="flex-1 flex flex-col overflow-hidden h-full">
            <ChatHeader showUpgrade={showUpgrade} onCloseChat={onCloseChat} />

            {messages.length === 0 && !isLoading ? (
                <EmptyState onSearch={handleSubmit}>
                    <PromptTray
                        onSubmit={handleSubmit}
                        isLoading={isLoading}
                        isTyping={isLoading}
                        onStop={isLoading ? handleStopStreaming : undefined}
                        onAttachment={handleSetAttachment}
                        onOpenWebModal={() => setIsWebpageModalOpen(true)}
                    />
                </EmptyState>
            ) : (
                <>
                    <MessageList
                        messages={messages}
                        isLoading={isLoading}
                        onImageClick={(url) => setPreviewImage(url)}
                        scrollRef={messageScrollRef}
                        onSearch={handleSubmit}
                    />

                    {/* Prompt Tray (Bottom Sticky) */}
                    <div className="p-4 md:p-6 w-full max-w-3xl mx-auto bg-transparent">
                        <PromptTray
                            onSubmit={handleSubmit}
                            isLoading={isLoading}
                            isTyping={isLoading}
                            onStop={isLoading ? handleStopStreaming : undefined}
                            onAttachment={handleSetAttachment}
                            onOpenWebModal={() => setIsWebpageModalOpen(true)}
                        />
                    </div>
                </>
            )}

            <AnimatePresence>
                {isWebpageModalOpen && (
                    <AttachWebpageModal
                        onClose={() => setIsWebpageModalOpen(false)}
                        onAdd={(url) => {
                            handleSetAttachment({ type: "url", data: url });
                            setIsWebpageModalOpen(false);
                        }}
                    />
                )}
            </AnimatePresence>
        </div>
    );
}

// ---------------------------------------------------------------------------
// Chat Header (Preserved)
// ---------------------------------------------------------------------------

function ChatHeader({ showUpgrade, onCloseChat }: { showUpgrade?: boolean; onCloseChat?: () => void }) {
    return (
        <div className="flex-shrink-0">
            <div className="max-w-3xl mx-auto flex items-center px-4 py-4">
                <div className="flex items-center gap-2 md:hidden">
                    <Home size={20} />
                    <span className="text-lg font-semibold">Tradeberg</span>
                </div>
                <div className="flex-1 flex justify-center">
                    {showUpgrade && (
                        <Link
                            href="/pricing"
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] text-sm font-medium text-[var(--tradeberg-accent-color)] hover:bg-[var(--tradeberg-glass-bg)] transition-colors"
                        >
                            <Sparkle className="w-4 h-4" />
                            <span>Upgrade to Pro</span>
                        </Link>
                    )}
                </div>
                {onCloseChat && (
                    <button
                        type="button"
                        onClick={onCloseChat}
                        className="ml-2 p-1.5 rounded-full hover:bg-[var(--tradeberg-card-bg)] text-[var(--tradeberg-text-secondary)] border border-[var(--tradeberg-card-border)] bg-transparent"
                        aria-label="Close chat"
                    >
                        <X className="w-4 h-4" />
                    </button>
                )}
            </div>
        </div>
    );
}

// ---------------------------------------------------------------------------
// Prompt tray (input + attachments) -- PRESERVED EXACTLY AS REQUESTED
// ---------------------------------------------------------------------------

function PromptTray({
    onSubmit,
    isLoading,
    isTyping,
    onAttachment,
    onOpenWebModal,
    onStop,
}: {
    onSubmit: (prompt: string) => void;
    isLoading: boolean;
    isTyping: boolean;
    onAttachment: (att: Attachment | null) => void;
    onOpenWebModal: () => void;
    onStop?: () => void;
}) {
    const [prompt, setPrompt] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement | null>(null);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [isCapturing, setIsCapturing] = useState(false);

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = "auto";
            const nextHeight = textarea.scrollHeight;
            textarea.style.height = `${nextHeight}px`;
            if (nextHeight > 300) {
                textarea.style.overflowY = "auto";
            } else {
                textarea.style.overflowY = "hidden";
            }
        }
    }, [prompt]);

    const handleFormSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(prompt);
        setPrompt("");
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.overflowY = "hidden";
        }
    };

    const handleCaptureClick = async () => {
        if (isCapturing) return;
        setIsCapturing(true);
        try {
            const chartEl = document.getElementById("tradingview-widget-container-trade");
            const mediaStream: MediaStream = await (navigator.mediaDevices as any).getDisplayMedia({
                video: { cursor: "never" },
                audio: false,
                preferCurrentTab: true,
            });

            const video = document.createElement("video");
            video.srcObject = mediaStream;
            await video.play();

            const vw = video.videoWidth || window.innerWidth;
            const vh = video.videoHeight || window.innerHeight;

            let srcX = 0; let srcY = 0; let srcW = vw; let srcH = vh;

            if (chartEl) {
                const rect = chartEl.getBoundingClientRect();
                const scaleX = vw / window.innerWidth;
                const scaleY = vh / window.innerHeight;
                srcX = Math.max(0, Math.floor(rect.left * scaleX));
                srcY = Math.max(0, Math.floor(rect.top * scaleY));
                srcW = Math.min(vw - srcX, Math.floor(rect.width * scaleX));
                srcH = Math.min(vh - srcY, Math.floor(rect.height * scaleY));
            }

            const canvas = document.createElement("canvas");
            canvas.width = Math.max(1, srcW);
            canvas.height = Math.max(1, srcH);
            const ctx = canvas.getContext("2d");
            if (ctx) {
                ctx.drawImage(video, srcX, srcY, srcW, srcH, 0, 0, canvas.width, canvas.height);
                const dataUrl = canvas.toDataURL("image/png");
                if (dataUrl) onAttachment({ type: "image", data: dataUrl });
            }
            mediaStream.getTracks().forEach((t) => t.stop());
        } catch (error) {
            console.error("Error capturing chart", error);
        } finally {
            setIsCapturing(false);
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            onAttachment({ type: "file", data: file.name });
        }
        event.target.value = "";
    };

    return (
        <motion.form onSubmit={handleFormSubmit} className="relative">
            <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" />

            <div className="flex flex-col p-4 bg-[var(--tradeberg-card-bg)] dark:bg-[#181818] border border-[var(--tradeberg-card-border)] rounded-xl shadow-lg focus-within:ring-1 focus-within:ring-[var(--tradeberg-accent-color)]/30 transition-all duration-200">
                <textarea
                    ref={textareaRef}
                    className="w-full bg-transparent text-lg text-[var(--tradeberg-text-primary)] placeholder:text-[var(--tradeberg-text-secondary)] resize-none focus:outline-none max-h-[300px] overflow-hidden"
                    placeholder="Ask anything about stocks, financials, or analysis..."
                    value={prompt}
                    onWheel={(e) => e.stopPropagation()}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                            e.preventDefault();
                            handleFormSubmit(e);
                        }
                    }}
                    rows={1}
                    disabled={isLoading}
                />

                <div className="h-4" />

                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <IconButton onClick={() => fileInputRef.current?.click()}>
                            <Paperclip size={18} />
                        </IconButton>
                        <IconButton onClick={onOpenWebModal}>
                            <Globe size={18} />
                        </IconButton>
                        <IconButton onClick={handleCaptureClick} disabled={isCapturing}>
                            {isCapturing ? <div className="w-4 h-4 border-2 border-t-purple-500 rounded-full animate-spin" /> : <Camera size={18} />}
                        </IconButton>
                        <IconButton>
                            <History size={18} />
                        </IconButton>
                    </div>

                    <div className="flex items-center gap-2">
                        <AnimatePresence mode="popLayout">
                            {(isLoading || isTyping) && onStop ? (
                                <motion.div key="stop" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.5, opacity: 0 }}>
                                    <button type="button" onClick={onStop} className="flex items-center justify-center w-8 h-8 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors">
                                        <span className="w-3 h-3 bg-white rounded-[3px]" />
                                    </button>
                                </motion.div>
                            ) : prompt.length === 0 ? (
                                <motion.div key="mic" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.5, opacity: 0 }}>
                                    <button type="button" className="flex items-center justify-center w-8 h-8 rounded-full text-white bg-gradient-to-br from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700">
                                        <Mic size={18} />
                                    </button>
                                </motion.div>
                            ) : (
                                <motion.div key="send" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.5, opacity: 0 }}>
                                    <button type="submit" disabled={isLoading} className="flex items-center justify-center w-8 h-8 rounded-full bg-purple-600 text-white hover:bg-purple-700 transition-colors disabled:bg-[var(--tradeberg-card-border)]">
                                        <ArrowUp size={18} />
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </motion.form>
    );
}

function IconButton({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { children: React.ReactNode }) {
    return (
        <button
            type="button"
            className="flex items-center justify-center w-8 h-8 rounded-full text-[var(--tradeberg-text-secondary)] hover:bg-[var(--tradeberg-card-border)]/40 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            {...props}
        >
            {children}
        </button>
    );
}

// ---------------------------------------------------------------------------
// Attach webpage modal
// ---------------------------------------------------------------------------

function AttachWebpageModal({
    onClose,
    onAdd,
}: {
    onClose: () => void;
    onAdd: (url: string) => void;
}) {
    const [url, setUrl] = useState("");

    const handleAdd = () => {
        if (url.trim()) onAdd(url.trim());
    };

    return (
        <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
        >
            <motion.div
                className="bg-[var(--tradeberg-card-bg)] rounded-2xl shadow-2xl w-full max-w-md p-6 border border-[var(--tradeberg-card-border)]"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-[var(--tradeberg-text-primary)]">
                        Attach Webpage
                    </h2>
                    <IconButton onClick={onClose}>
                        <X size={18} className="text-gray-400" />
                    </IconButton>
                </div>

                <p className="text-sm text-[var(--tradeberg-text-secondary)] mb-4">
                    Webpage URL
                </p>

                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="w-full p-3 rounded-lg bg-[var(--tradeberg-bg)] text-[var(--tradeberg-text-primary)] placeholder-[var(--tradeberg-text-secondary)] border border-[var(--tradeberg-card-border)] focus:outline-none focus:ring-2 focus:ring-[var(--tradeberg-accent-color)]"
                />

                <div className="flex justify-end gap-2 mt-6">
                    <button onClick={onClose} className="py-2 px-4 rounded-lg text-sm font-medium text-[var(--tradeberg-text-secondary)] hover:bg-[var(--tradeberg-card-border)]/40 transition-colors">
                        Cancel
                    </button>
                    <button onClick={handleAdd} className="py-2 px-4 rounded-lg text-sm font-medium text-black bg-white hover:bg-gray-200 transition-colors">
                        Add
                    </button>
                </div>
            </motion.div>
        </motion.div>
    );
}

// ---------------------------------------------------------------------------
// Trade View (Preserved Layout)
// ---------------------------------------------------------------------------

export function TradeView() {
    const [chatFraction, setChatFraction] = useState(0.32);
    const [isDragging, setIsDragging] = useState(false);
    const [isChatOpen, setIsChatOpen] = useState(true);
    const containerRef = useRef<HTMLDivElement | null>(null);

    // Global drag listeners
    useEffect(() => {
        const handleDragMove = (e: MouseEvent) => {
            if (!isDragging || !isChatOpen) return;
            const container = containerRef.current;
            if (!container) return;

            const rect = container.getBoundingClientRect();
            const totalWidth = rect.width;
            const x = e.clientX - rect.left;

            let nextFraction = 1 - x / totalWidth;
            const minFraction = 0.2;
            const maxFraction = 0.6;
            nextFraction = Math.min(Math.max(minFraction, nextFraction), maxFraction);

            setChatFraction(nextFraction);
        };

        const handleDragEnd = () => {
            if (!isDragging) return;
            setIsDragging(false);
            if (typeof document !== 'undefined') document.body.style.cursor = 'default';
        };

        if (isDragging) {
            window.addEventListener('mousemove', handleDragMove);
            window.addEventListener('mouseup', handleDragEnd);
        }

        return () => {
            window.removeEventListener('mousemove', handleDragMove);
            window.removeEventListener('mouseup', handleDragEnd);
        };
    }, [isDragging, isChatOpen]);

    const startDragging = (e: React.MouseEvent) => {
        if (!isChatOpen) return;
        e.preventDefault();
        setIsDragging(true);
        if (typeof document !== 'undefined') document.body.style.cursor = 'col-resize';
    };

    const handleCloseChat = () => setIsChatOpen(false);
    const handleOpenChat = () => setIsChatOpen(true);

    const chartWidth = isChatOpen ? `${(1 - chatFraction) * 100}%` : '100%';
    const chatWidth = isChatOpen ? `${chatFraction * 100}%` : '0%';

    return (
        <div ref={containerRef} className="flex h-full overflow-hidden relative">
            {/* LEFT: CHART */}
            <motion.div
                className="h-full overflow-hidden"
                animate={{ width: chartWidth }}
                transition={isDragging ? { duration: 0 } : { type: 'spring', stiffness: 260, damping: 24 }}
                style={{ pointerEvents: isDragging ? 'none' : 'auto' }}
            >
                <TradingViewWidget />
            </motion.div>

            {/* DIVIDER */}
            {isChatOpen ? (
                <div
                    className={`w-px z-50 flex-shrink-0 border-l transition-colors ${isDragging
                        ? 'border-l-[var(--tradeberg-accent-color)]'
                        : 'border-l-[var(--sidebar-border)] hover:border-l-[var(--tradeberg-accent-color)]'
                        }`}
                    style={{ cursor: 'col-resize', backgroundColor: 'transparent' }}
                    onMouseDown={startDragging}
                />
            ) : (
                <button
                    type="button"
                    onClick={handleOpenChat}
                    className="z-50 flex-shrink-0 px-1.5 py-3 bg-transparent border border-[var(--tradeberg-card-border)] rounded-r-lg flex items-center justify-center self-start mt-4"
                >
                    <img src="/arrow-black.png" alt="Open chat" className="block dark:hidden w-3.5 h-3.5 rotate-180" />
                    <img src="/arrow-white.png" alt="Open chat" className="hidden dark:block w-3.5 h-3.5 rotate-180" />
                </button>
            )}

            {/* RIGHT: CHAT */}
            <motion.div
                className="flex flex-col h-full bg-white dark:bg-[var(--tradeberg-bg)] overflow-hidden flex-shrink-0"
                animate={{ width: chatWidth }}
                transition={isDragging ? { duration: 0 } : { type: 'spring', stiffness: 260, damping: 24 }}
                style={{ pointerEvents: isDragging || !isChatOpen ? 'none' : 'auto' }}
            >
                {isChatOpen && (
                    <div className="h-full overflow-hidden w-full">
                        <ChatInterface showUpgrade onCloseChat={handleCloseChat} mode="trade" />
                    </div>
                )}
            </motion.div>
        </div>
    );
}

function TradingViewWidget() {
    const container = useRef<HTMLDivElement | null>(null);
    const widgetInstance = useRef<any>(null);
    const { resolvedTheme } = useNextTheme();

    useEffect(() => {
        let tvWidget: any;

        function createWidget() {
            if (container.current && (window as any).TradingView) {
                container.current.innerHTML = "";
                const theme = resolvedTheme === "dark" ? "dark" : "light";
                const widgetOptions = {
                    width: "100%", height: "100%", symbol: "BINANCE:BTCUSDT", interval: "D", timezone: "Etc/UTC", theme, style: "1", locale: "en", toolbar_bg: theme === "dark" ? "#131722" : "#f1f3f6", enable_publishing: false, allow_symbol_change: true, container_id: "tradingview-widget-container-trade",
                    onChartReady: () => { widgetInstance.current = tvWidget; },
                };
                tvWidget = new (window as any).TradingView.widget(widgetOptions);
            }
        }

        if (document.getElementById("tradingview-widget-script")) {
            if ((window as any).TradingView) createWidget();
        } else {
            const script = document.createElement("script");
            script.id = "tradingview-widget-script";
            script.src = "https://s3.tradingview.com/tv.js";
            script.type = "text/javascript";
            script.async = true;
            script.onload = createWidget;
            document.head.appendChild(script);
        }

        return () => {
            if (container.current) {
                try { widgetInstance.current?.remove(); } catch (e) { console.error(e); }
                container.current.innerHTML = "";
            }
            widgetInstance.current = null;
        };
    }, [resolvedTheme]);

    return <div id="tradingview-widget-container-trade" ref={container} style={{ height: "100%", width: "100%" }} />;
}
