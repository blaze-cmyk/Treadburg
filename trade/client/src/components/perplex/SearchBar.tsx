import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Paperclip,
    Globe,
    Camera,
    History,
    Mic,
    ArrowUp,
    X,
} from "lucide-react";

// Types
type Attachment =
    | { type: "image"; data: string }
    | { type: "url"; data: string }
    | { type: "file"; data: string };

interface SearchBarProps {
    onSearch: (prompt: string, attachments: Attachment[]) => void;
    isLoading: boolean;
    isTyping?: boolean; // Optional to match usage
    isCompact?: boolean; // Added to match previous SearchBar interface if needed, though unused in new design
}

export function SearchBar({
    onSearch,
    isLoading,
    isTyping = false,
}: SearchBarProps) {
    const [prompt, setPrompt] = useState("");
    const [attachments, setAttachments] = useState<Attachment[]>([]);
    const [isWebpageModalOpen, setIsWebpageModalOpen] = useState(false);
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
        if (!prompt.trim() && attachments.length === 0) return;

        onSearch(prompt, attachments);
        setPrompt("");
        setAttachments([]);
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.overflowY = "hidden";
        }
    };

    const handleCaptureClick = async () => {
        if (isCapturing) return;
        setIsCapturing(true);
        try {
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

            const canvas = document.createElement("canvas");
            canvas.width = vw;
            canvas.height = vh;
            const ctx = canvas.getContext("2d");
            if (ctx) {
                ctx.drawImage(video, 0, 0, vw, vh);
                const dataUrl = canvas.toDataURL("image/png");
                if (dataUrl) setAttachments(prev => [...prev, { type: "image", data: dataUrl }]);
            }
            mediaStream.getTracks().forEach((t) => t.stop());
        } catch (error) {
            console.error("Error capturing screen", error);
        } finally {
            setIsCapturing(false);
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const result = e.target?.result as string;
                setAttachments(prev => [...prev, { type: "image", data: result }]);
            };
            reader.readAsDataURL(file);
        }
        event.target.value = "";
    };

    const removeAttachment = (index: number) => {
        setAttachments(prev => prev.filter((_, i) => i !== index));
    };

    return (
        <div className="w-full max-w-3xl mx-auto">
            <motion.form onSubmit={handleFormSubmit} className="relative">
                <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept="image/*" />

                <div className="flex flex-col p-4 bg-perplex-surface border border-perplex-border rounded-xl shadow-lg focus-within:ring-1 focus-within:ring-perplex-accent/30 transition-all duration-200">

                    {/* Attachments Preview */}
                    {attachments.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-3">
                            {attachments.map((att, idx) => (
                                <div key={idx} className="relative group">
                                    <div className="flex items-center gap-2 bg-perplex-surfaceHover rounded-lg p-2 pr-8 border border-perplex-border">
                                        {att.type === 'image' ? (
                                            <img src={att.data} alt="Attachment" className="w-8 h-8 object-cover rounded" />
                                        ) : (
                                            <Globe size={16} className="text-perplex-accent" />
                                        )}
                                        <span className="text-xs text-perplex-textMain max-w-[150px] truncate">
                                            {att.type === 'url' ? att.data : 'Image'}
                                        </span>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={() => removeAttachment(idx)}
                                        className="absolute top-1 right-1 p-1 bg-black/50 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        <X size={12} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <textarea
                        ref={textareaRef}
                        className="w-full bg-transparent text-lg text-perplex-textMain placeholder:text-perplex-textMuted resize-none focus:outline-none max-h-[300px] overflow-hidden"
                        placeholder="Ask anything..."
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
                            <IconButton onClick={() => setIsWebpageModalOpen(true)}>
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
                                {isLoading ? (
                                    <motion.div key="stop" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.5, opacity: 0 }}>
                                        <button type="button" className="flex items-center justify-center w-8 h-8 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors">
                                            <span className="w-3 h-3 bg-white rounded-[3px]" />
                                        </button>
                                    </motion.div>
                                ) : prompt.length === 0 && attachments.length === 0 ? (
                                    <motion.div key="mic" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.5, opacity: 0 }}>
                                        <button type="button" className="flex items-center justify-center w-8 h-8 rounded-full text-white bg-gradient-to-br from-perplex-accent to-teal-600 hover:opacity-90">
                                            <Mic size={18} />
                                        </button>
                                    </motion.div>
                                ) : (
                                    <motion.div key="send" initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.5, opacity: 0 }}>
                                        <button type="submit" disabled={isLoading} className="flex items-center justify-center w-8 h-8 rounded-full bg-perplex-accent text-white hover:opacity-90 transition-colors disabled:opacity-50">
                                            <ArrowUp size={18} />
                                        </button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </div>
            </motion.form>

            <AnimatePresence>
                {isWebpageModalOpen && (
                    <AttachWebpageModal
                        onClose={() => setIsWebpageModalOpen(false)}
                        onAdd={(url) => {
                            setAttachments(prev => [...prev, { type: "url", data: url }]);
                            setIsWebpageModalOpen(false);
                        }}
                    />
                )}
            </AnimatePresence>
        </div>
    );
}

function IconButton({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { children: React.ReactNode }) {
    return (
        <button
            type="button"
            className="flex items-center justify-center w-8 h-8 rounded-full text-perplex-textMuted hover:bg-perplex-surfaceHover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            {...props}
        >
            {children}
        </button>
    );
}

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
                className="bg-perplex-surface rounded-2xl shadow-2xl w-full max-w-md p-6 border border-perplex-border"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-perplex-textMain">
                        Attach Webpage
                    </h2>
                    <IconButton onClick={onClose}>
                        <X size={18} />
                    </IconButton>
                </div>

                <p className="text-sm text-perplex-textMuted mb-4">
                    Webpage URL
                </p>

                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="w-full p-3 rounded-lg bg-perplex-bg text-perplex-textMain placeholder-perplex-textMuted border border-perplex-border focus:outline-none focus:ring-2 focus:ring-perplex-accent"
                />

                <div className="flex justify-end gap-2 mt-6">
                    <button onClick={onClose} className="py-2 px-4 rounded-lg text-sm font-medium text-perplex-textMuted hover:bg-perplex-surfaceHover transition-colors">
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
