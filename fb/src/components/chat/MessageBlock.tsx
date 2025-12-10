import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Layers, CheckCircle2, ChevronDown, ChevronRight, Copy, Share, ThumbsUp, ThumbsDown, MoreHorizontal, Plus, Loader2 } from 'lucide-react';
import { Message } from '../../types';
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
                <h2 className="text-3xl text-[var(--tradeberg-text-primary)] font-display font-medium leading-tight">{message.content}</h2>
            </div>
        );
    }

    return (
        <div className="w-full max-w-3xl mx-auto pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Sources Section */}
            {message.sources && message.sources.length > 0 && (
                <div className="mb-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <div className="flex items-center gap-2 mb-3 text-[var(--tradeberg-text-primary)]">
                        <Layers size={14} className="text-[var(--tradeberg-text-secondary)]" />
                        <span className="font-medium text-xs uppercase tracking-wide text-[var(--tradeberg-text-secondary)]">Sources</span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        {message.sources.map((source, idx) => (
                            <a
                                key={idx}
                                href={source.url}
                                target="_blank"
                                rel="noreferrer"
                                className="bg-[var(--tradeberg-card-bg)] hover:bg-[var(--tradeberg-card-border)]/50 border border-[var(--tradeberg-card-border)] p-3 rounded-lg flex flex-col gap-2 transition-all duration-200 group h-20 justify-between no-underline"
                            >
                                <div className="text-xs text-[var(--tradeberg-text-primary)] line-clamp-2 leading-snug group-hover:text-[var(--tradeberg-accent-color)] transition-colors font-medium">
                                    {source.title}
                                </div>
                                <div className="flex items-center gap-1.5 mt-auto">
                                    <div className="w-3.5 h-3.5 rounded-full bg-white/10 flex items-center justify-center overflow-hidden">
                                        <img src={`https://www.google.com/s2/favicons?domain=${source.url}&sz=32`} alt="favicon" className="w-full h-full object-cover opacity-80" />
                                    </div>
                                    <span className="text-[10px] text-[var(--tradeberg-text-secondary)] truncate font-mono">{new URL(source.url).hostname.replace('www.', '')}</span>
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
                        <div className="w-6 h-6 rounded-full bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] flex items-center justify-center">
                            <div className="text-[10px] text-[var(--tradeberg-accent-color)] font-bold">✦</div>
                        </div>
                        <span className="font-medium text-[var(--tradeberg-text-primary)] text-sm">TradeBerg Analysis</span>
                    </div>
                </div>

                {/* Working/Thinking State */}
                {message.searchSteps && message.searchSteps.length > 0 && (
                    <div className="mb-6 ml-1">
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="flex items-center gap-2 text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors mb-2 group w-full text-left"
                        >
                            <div className="w-4 h-4 flex items-center justify-center">
                                {message.isThinking ? (
                                    <Loader2 size={14} className="animate-spin text-[var(--tradeberg-accent-color)]" />
                                ) : (
                                    <CheckCircle2 size={14} className="text-[var(--tradeberg-accent-color)]" />
                                )}
                            </div>
                            <span className="text-sm font-medium">
                                {message.isThinking ? "Analyzing market data..." : `Processed ${message.searchSteps.length} steps`}
                            </span>
                            {isExpanded ? <ChevronDown size={14} className="ml-auto opacity-50" /> : <ChevronRight size={14} className="ml-auto opacity-50" />}
                        </button>

                        {isExpanded && (
                            <div className="flex flex-col gap-2 mt-2 pl-6 border-l border-[var(--tradeberg-card-border)] ml-2">
                                {message.searchSteps.map((step, idx) => (
                                    <div key={idx} className="flex items-center gap-3 text-sm text-[var(--tradeberg-text-secondary)] animate-in fade-in slide-in-from-left-2 duration-300">
                                        <span className="truncate">{step}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                <div className="markdown-content text-[var(--tradeberg-text-primary)] text-[16px] leading-7 font-light">
                    {message.content ? (
                        <ReactMarkdown
                            components={{
                                a: ({ node, ...props }) => <a {...props} className="text-[var(--tradeberg-accent-color)] hover:underline cursor-pointer" target="_blank" />,
                                h1: ({ node, ...props }) => <h1 {...props} className="text-xl font-medium text-[var(--tradeberg-text-primary)] mt-6 mb-3" />,
                                h2: ({ node, ...props }) => <h2 {...props} className="text-lg font-medium text-[var(--tradeberg-text-primary)] mt-8 mb-4 flex items-center gap-2 border-b border-[var(--tradeberg-card-border)] pb-2" />,
                                h3: ({ node, ...props }) => <h3 {...props} className="text-base font-medium text-[var(--tradeberg-text-primary)] mt-6 mb-2" />,
                                ul: ({ node, ...props }) => <ul {...props} className="list-disc pl-5 mb-4 space-y-1 text-[var(--tradeberg-text-primary)]/90" />,
                                ol: ({ node, ...props }) => <ol {...props} className="list-decimal pl-5 mb-4 space-y-1 text-[var(--tradeberg-text-primary)]/90" />,
                                li: ({ node, ordered, ...props }: any) => <li {...props} className="pl-1" />,
                                p: ({ node, ...props }) => <p {...props} className="mb-4 text-[var(--tradeberg-text-primary)]/90" />,
                                strong: ({ node, ...props }) => <strong {...props} className="font-semibold text-[var(--tradeberg-text-primary)] text-[var(--tradeberg-accent-color)]/90" />,
                                pre: ({ node, ...props }) => <pre {...props} className="bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] rounded-lg p-4 overflow-x-auto my-4" />,

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
                                    return <code className={`${className} bg-[var(--tradeberg-card-bg)] px-1.5 py-0.5 rounded text-sm font-mono text-[var(--tradeberg-accent-color)]`} {...props}>{children}</code>;
                                },

                                // Custom "Liquid Glass" Table Style
                                table: ({ node, ...props }) => (
                                    <div className="w-full my-6 glass-panel rounded-xl overflow-hidden border border-white/5 shadow-2xl">
                                        <div className="overflow-x-auto">
                                            <table {...props} className="w-full text-sm text-left border-collapse" />
                                        </div>
                                    </div>
                                ),
                                thead: ({ node, ...props }) => <thead {...props} className="bg-white/5 text-[var(--tradeberg-text-secondary)] uppercase text-xs font-medium tracking-wider" />,
                                th: ({ node, ...props }) => <th {...props} className="px-6 py-4 font-semibold text-[var(--tradeberg-text-primary)] border-b border-white/10" />,
                                tbody: ({ node, ...props }) => <tbody {...props} className="divide-y divide-white/5" />,
                                tr: ({ node, ...props }) => <tr {...props} className="hover:bg-white/5 transition-colors" />,
                                td: ({ node, ...props }) => <td {...props} className="px-6 py-3 text-[var(--tradeberg-text-primary)]/90" />,
                            }}
                        >
                            {message.content}
                        </ReactMarkdown>
                    ) : (
                        !message.isThinking && <div className="flex gap-1"><span className="w-2 h-2 bg-[var(--tradeberg-text-secondary)] rounded-full animate-bounce"></span><span className="w-2 h-2 bg-[var(--tradeberg-text-secondary)] rounded-full animate-bounce delay-100"></span><span className="w-2 h-2 bg-[var(--tradeberg-text-secondary)] rounded-full animate-bounce delay-200"></span></div>
                    )}
                    {isLast && message.isThinking && message.content && (
                        <span className="inline-block w-2 h-4 bg-[var(--tradeberg-accent-color)] ml-1 animate-pulse align-middle"></span>
                    )}
                </div>
            </div>

            {/* Action Bar */}
            {message.content && !message.isThinking && (
                <div className="flex items-center gap-2 mt-4 pb-4 border-b border-[var(--tradeberg-card-border)]/50">
                    <ActionBtn icon={<Copy size={14} />} label="Copy" />
                    <ActionBtn icon={<Share size={14} />} label="Share" />
                    <div className="flex-1"></div>
                    <div className="flex items-center bg-[var(--tradeberg-card-bg)] rounded-full p-1 border border-[var(--tradeberg-card-border)]">
                        <button className="p-1.5 text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"><ThumbsUp size={14} /></button>
                        <div className="w-px h-3 bg-[var(--tradeberg-card-border)] mx-1"></div>
                        <button className="p-1.5 text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-colors"><ThumbsDown size={14} /></button>
                    </div>
                    <ActionBtn icon={<MoreHorizontal size={14} />} />
                </div>
            )}


        </div>
    );
};

const ActionBtn = ({ icon, label }: { icon: React.ReactNode, label?: string }) => (
    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-[var(--tradeberg-card-bg)] border border-transparent hover:border-[var(--tradeberg-card-border)] text-[var(--tradeberg-text-secondary)] hover:text-[var(--tradeberg-text-primary)] transition-all text-xs font-medium">
        {icon}
        {label && <span>{label}</span>}
    </button>
);


