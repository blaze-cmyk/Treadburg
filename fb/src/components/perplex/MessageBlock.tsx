import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Layers, CheckCircle2, ChevronDown, ChevronRight, Copy, Share, ThumbsUp, ThumbsDown, MoreHorizontal, Plus, Loader2 } from 'lucide-react';
import { Message, Source } from '../../types';
import { LiquidChart, ChartData } from './LiquidChart';

interface MessageBlockProps {
    message: Message;
    isLast: boolean;
}

export const MessageBlock: React.FC<MessageBlockProps> = ({ message, isLast }) => {
    const [isExpanded, setIsExpanded] = useState(true);

    // Auto-collapse steps when content starts streaming or finishes
    useEffect(() => {
        if (message.content && message.content.length > 50) {
            setIsExpanded(false);
        }
    }, [message.content]);

    if (message.role === 'user') {
        return (
            <div className="w-full max-w-3xl mx-auto py-8">
                <h2 className="text-3xl text-perplex-textMain font-display font-medium leading-tight">{message.content}</h2>
            </div>
        );
    }

    return (
        <div className="w-full max-w-3xl mx-auto pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Sources Section */}
            {message.sources && message.sources.length > 0 && (
                <div className="mb-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <div className="flex items-center gap-2 mb-3 text-perplex-textMain">
                        <Layers size={14} className="text-perplex-textMuted" />
                        <span className="font-medium text-xs uppercase tracking-wide text-perplex-textMuted">Sources</span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {message.sources.map((source, idx) => (
                            <a
                                key={idx}
                                href={source.url}
                                target="_blank"
                                rel="noreferrer"
                                className="bg-perplex-surface hover:bg-perplex-surfaceHover border border-perplex-border p-3 rounded-lg flex flex-col gap-2 transition-all duration-200 group h-20 justify-between no-underline"
                            >
                                <div className="text-xs text-perplex-textMain line-clamp-2 leading-snug group-hover:text-perplex-accent transition-colors font-medium">
                                    {source.title}
                                </div>
                                <div className="flex items-center gap-1.5 mt-auto">
                                    <div className="w-3.5 h-3.5 rounded-full bg-white/10 flex items-center justify-center overflow-hidden">
                                        <img src={`https://www.google.com/s2/favicons?domain=${source.url}&sz=32`} alt="favicon" className="w-full h-full object-cover opacity-80" />
                                    </div>
                                    <span className="text-[10px] text-perplex-textMuted truncate font-mono">{new URL(source.url).hostname.replace('www.', '')}</span>
                                </div>
                            </a>
                        ))}
                    </div>
                </div>
            )}

            {/* Answer Section */}
            <div className="mb-2">
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-perplex-surface border border-perplex-border flex items-center justify-center">
                            {/* Perplexity Star Logo Placeholder */}
                            <div className="text-[10px] text-perplex-accent font-bold">✴</div>
                        </div>
                        <span className="font-medium text-perplex-textMain text-sm">TradeBerg Answer</span>
                    </div>
                </div>

                {/* Working/Thinking State */}
                {message.searchSteps && message.searchSteps.length > 0 && (
                    <div className="mb-6 ml-1">
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="flex items-center gap-2 text-perplex-textMuted hover:text-perplex-textMain transition-colors mb-2 group w-full text-left"
                        >
                            <div className="w-4 h-4 flex items-center justify-center">
                                {message.isThinking ? (
                                    <Loader2 size={14} className="animate-spin text-perplex-accent" />
                                ) : (
                                    <CheckCircle2 size={14} className="text-perplex-accent" />
                                )}
                            </div>
                            <span className="text-sm font-medium">
                                {message.isThinking ? "Working..." : `Searched ${message.searchSteps.length} items`}
                            </span>
                            {isExpanded ? <ChevronDown size={14} className="ml-auto opacity-50" /> : <ChevronRight size={14} className="ml-auto opacity-50" />}
                        </button>

                        {isExpanded && (
                            <div className="flex flex-col gap-2 mt-2 pl-6 border-l border-perplex-border/50 ml-2">
                                {message.searchSteps.map((step, idx) => (
                                    <div key={idx} className="flex items-center gap-3 text-sm text-perplex-textMuted animate-in fade-in slide-in-from-left-2 duration-300">
                                        <span className="truncate">{step}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                <div className="markdown-content text-perplex-textMain text-[16px] leading-7 font-light">
                    {message.content ? (
                        <ReactMarkdown
                            components={{
                                a: ({ node, ...props }) => <a {...props} className="text-perplex-accent hover:underline cursor-pointer" target="_blank" />,
                                h1: ({ node, ...props }) => <h1 {...props} className="text-xl font-medium text-perplex-textMain mt-6 mb-3" />,
                                h2: ({ node, ...props }) => <h2 {...props} className="text-lg font-medium text-perplex-textMain mt-8 mb-4 flex items-center gap-2 border-b border-perplex-border pb-2" />,
                                h3: ({ node, ...props }) => <h3 {...props} className="text-base font-medium text-perplex-textMain mt-6 mb-2" />,
                                ul: ({ node, ordered, ...props }: any) => <ul {...props} className="list-disc pl-5 mb-4 space-y-1 text-perplex-textMain/90" />,
                                ol: ({ node, ordered, ...props }: any) => <ol {...props} className="list-decimal pl-5 mb-4 space-y-1 text-perplex-textMain/90" />,
                                li: ({ node, ordered, ...props }: any) => <li {...props} className="pl-1" />,
                                p: ({ node, ...props }) => <p {...props} className="mb-4 text-perplex-textMain/90" />,
                                strong: ({ node, ...props }) => <strong {...props} className="font-semibold text-perplex-textMain text-perplex-accent/90" />,
                                pre: ({ node, ...props }) => <pre {...props} className="bg-perplex-surface border border-white/5 rounded-lg p-4 overflow-x-auto my-4" />,

                                // Custom renderer for code blocks to catch json-chart
                                code: ({ node, className, children, ...props }: any) => {
                                    const match = /language-(\w+)/.exec(className || '');
                                    const isChart = match && match[1] === 'json-chart';

                                    if (isChart) {
                                        try {
                                            const chartData: ChartData = JSON.parse(String(children).replace(/\n$/, ''));
                                            return <LiquidChart data={chartData} />;
                                        } catch (e) {
                                            return <code className={className} {...props}>{children}</code>;
                                        }
                                    }
                                    if (match) {
                                        return <code className={`${className} font-mono text-sm`} {...props}>{children}</code>;
                                    }

                                    // Inline code
                                    return <code className={`${className} bg-perplex-surface px-1.5 py-0.5 rounded text-sm font-mono text-perplex-accent`} {...props}>{children}</code>;
                                },

                                // Custom "Liquid Glass" Table Style
                                table: ({ node, ...props }) => (
                                    <div className="w-full my-6 glass-panel rounded-xl overflow-hidden border border-white/5 shadow-2xl">
                                        <div className="overflow-x-auto">
                                            <table {...props} className="w-full text-sm text-left border-collapse" />
                                        </div>
                                    </div>
                                ),
                                thead: ({ node, ...props }) => <thead {...props} className="bg-white/5 text-perplex-textMuted uppercase text-xs font-medium tracking-wider" />,
                                th: ({ node, ...props }) => <th {...props} className="px-6 py-4 font-semibold text-perplex-textMain border-b border-white/10" />,
                                tbody: ({ node, ...props }) => <tbody {...props} className="divide-y divide-white/5" />,
                                tr: ({ node, ...props }) => <tr {...props} className="hover:bg-white/5 transition-colors" />,
                                td: ({ node, ...props }) => <td {...props} className="px-6 py-3 text-perplex-textMain/90" />,
                            }}
                        >
                            {message.content}
                        </ReactMarkdown>
                    ) : (
                        !message.isThinking && <div className="flex gap-1"><span className="w-2 h-2 bg-perplex-textMuted rounded-full animate-bounce"></span><span className="w-2 h-2 bg-perplex-textMuted rounded-full animate-bounce delay-100"></span><span className="w-2 h-2 bg-perplex-textMuted rounded-full animate-bounce delay-200"></span></div>
                    )}
                    {isLast && message.isThinking && message.content && (
                        <span className="inline-block w-2 h-4 bg-perplex-accent ml-1 animate-pulse align-middle"></span>
                    )}
                </div>
            </div>

            {/* Action Bar */}
            {message.content && !message.isThinking && (
                <div className="flex items-center gap-2 mt-4 pb-4 border-b border-perplex-border/50">
                    <ActionBtn icon={<Copy size={14} />} label="Copy" />
                    <ActionBtn icon={<Share size={14} />} label="Share" />
                    <div className="flex-1"></div>
                    <div className="flex items-center bg-perplex-surface rounded-full p-1 border border-perplex-border">
                        <button className="p-1.5 text-perplex-textMuted hover:text-perplex-textMain transition-colors"><ThumbsUp size={14} /></button>
                        <div className="w-px h-3 bg-perplex-border mx-1"></div>
                        <button className="p-1.5 text-perplex-textMuted hover:text-perplex-textMain transition-colors"><ThumbsDown size={14} /></button>
                    </div>
                    <ActionBtn icon={<MoreHorizontal size={14} />} />
                </div>
            )}

            {/* Related Questions - Removed as per previous request, but if "exact everything" means including it, I should add it back. 
          However, the user asked to remove it in the previous turn. 
          "implement everything exact everything" usually implies the original state.
          But the user explicitly asked to remove it in step 714.
          I'll stick to the "exact everything" instruction for the NEW route /perplex, which implies restoring it.
          The removal was for the main Tradeberg chat.
          So I will ADD IT BACK for /perplex.
      */}
            {message.content && !message.isThinking && (
                <div className="mt-6 animate-in fade-in slide-in-from-bottom-2 duration-500 delay-300">
                    <div className="flex items-center gap-2 mb-3">
                        <Layers size={14} className="text-perplex-textMuted" />
                        <h3 className="text-sm font-medium text-perplex-textMain uppercase tracking-wide">Related</h3>
                    </div>
                    <div className="flex flex-col gap-2">
                        <RelatedQ question={`What are the key risks for ${message.content.substring(0, 20).replace(/[^a-zA-Z ]/g, '')}...`} />
                        <RelatedQ question="Show me a comparative financial analysis" />
                        <RelatedQ question="What is the latest analyst consensus?" />
                    </div>
                </div>
            )}

        </div>
    );
};

const ActionBtn = ({ icon, label }: { icon: React.ReactNode, label?: string }) => (
    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-perplex-surface border border-transparent hover:border-perplex-border text-perplex-textMuted hover:text-perplex-textMain transition-all text-xs font-medium">
        {icon}
        {label && <span>{label}</span>}
    </button>
);

const RelatedQ = ({ question }: { question: string }) => (
    <button className="flex items-center justify-between p-3 text-left rounded-lg border border-perplex-border/50 hover:bg-perplex-surface transition-all duration-200 group">
        <span className="text-perplex-textMain text-sm font-medium group-hover:text-perplex-accent transition-colors w-[90%] truncate">{question}</span>
        <Plus size={16} className="text-perplex-textMuted group-hover:text-perplex-accent transition-colors" />
    </button>
);
