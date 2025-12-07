import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Layers, FileText, CheckCircle2, ChevronDown, ChevronRight, Copy, Share, ThumbsUp, ThumbsDown, MoreHorizontal, Plus, Loader2 } from 'lucide-react';
import { Message, Source, ChartConfig, TableConfig } from '../types';
import { ThinkingAnimation } from './ThinkingAnimation';
import { ChartWidget } from './ChartWidget';
import { TableWidget } from './TableWidget';

interface MessageBlockProps {
  message: Message;
  isLast: boolean;
}

export const MessageBlock: React.FC<MessageBlockProps> = ({ message, isLast }) => {
  const [showSources, setShowSources] = useState(false);

  if (message.role === 'user') {
    return (
      <div className="w-full max-w-3xl mx-auto py-8">
        <h2 className="text-3xl text-textMain font-display font-medium leading-tight">{message.content}</h2>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-surface border border-border flex items-center justify-center">
                  <div className="text-[10px] text-accent font-bold">✴</div>
              </div>
              <span className="font-medium text-textMain text-sm">TradeBerg Answer</span>
          </div>
      </div>
      
      {(message.isThinking || message.content) && (
        <div className="border-b border-border pb-4">
          {message.isThinking && <ThinkingAnimation message={message} />}

          <div className="markdown-content text-textMain text-[16px] leading-7 font-light">
            {message.content ? (
              <ReactMarkdown 
                components={{
                  a: ({node, ...props}) => <a {...props} className="text-accent hover:underline cursor-pointer" target="_blank" />,
                  h1: ({node, ...props}) => <h1 {...props} className="text-xl font-medium text-textMain mt-6 mb-3" />,
                  h2: ({node, ...props}) => <h2 {...props} className="text-lg font-medium text-textMain mt-8 mb-4 flex items-center gap-2 border-b border-border pb-2" />,
                  h3: ({node, ...props}) => <h3 {...props} className="text-base font-medium text-textMain mt-6 mb-2" />,
                  ul: ({node, ...props}) => <ul {...props} className="list-disc pl-5 mb-4 space-y-1 text-textMain/90" />,
                  ol: ({node, ...props}) => <ol {...props} className="list-decimal pl-5 mb-4 space-y-1 text-textMain/90" />,
                  li: ({node, ...props}) => <li {...props} className="pl-1" />,
                  p: ({node, ...props}) => <p {...props} className="mb-4 text-textMain/90" />,
                  strong: ({node, ...props}) => <strong {...props} className="font-semibold text-textMain text-accent/90" />,
                  pre: ({node, ...props}) => <pre {...props} className="bg-surface border border-white/5 rounded-lg p-4 overflow-x-auto my-4 font-mono text-sm" />,
                  code: ({node, className, children, ...props}: any) => {
                      const match = /language-(\w+)/.exec(className || '');
                      const lang = match ? match[1] : '';

                      if (lang === "chart") {
                        try {
                          const data: ChartConfig = JSON.parse(String(children).replace(/\n$/, ""));
                          return <ChartWidget data={data} />;
                        } catch (e) { return null; }
                      }
                      
                      if (lang === "table") {
                         try {
                           const data: TableConfig = JSON.parse(String(children).replace(/\n$/, ""));
                           return <TableWidget data={data} />;
                         } catch (e) { return null; }
                      }
                      
                      if (match) {
                          return <code className={`${className} font-mono text-sm`} {...props}>{children}</code>;
                      }
                      
                      return <code className={`${className} bg-surface px-1.5 py-0.5 rounded text-sm font-mono text-accent`} {...props}>{children}</code>;
                  },
                }}
              >
                {message.content}
              </ReactMarkdown>
            ) : null}
            {isLast && message.isThinking && message.content && (
                <span className="inline-block w-2 h-4 bg-accent ml-1 animate-pulse align-middle"></span>
            )}
          </div>
        </div>
      )}

      {/* Action Bar & Sources Toggle */}
      {!message.isThinking && message.content && (
        <>
          <div className="flex items-center gap-2 mt-4">
             {message.sources && message.sources.length > 0 && (
                <ActionBtn 
                  icon={<Layers size={14} />} 
                  label={`${message.sources.length} Sources`} 
                  onClick={() => setShowSources(!showSources)}
                />
             )}
             <ActionBtn icon={<Copy size={14} />} label="Copy" />
             <ActionBtn icon={<Share size={14} />} label="Share" />
             <div className="flex-1"></div>
             <div className="flex items-center bg-surface rounded-full p-1 border border-border">
                <button className="p-1.5 text-textMuted hover:text-textMain transition-colors"><ThumbsUp size={14} /></button>
                <div className="w-px h-3 bg-border mx-1"></div>
                <button className="p-1.5 text-textMuted hover:text-textMain transition-colors"><ThumbsDown size={14} /></button>
             </div>
             <ActionBtn icon={<MoreHorizontal size={14} />} />
          </div>

          {/* Collapsible Sources List */}
          {showSources && message.sources && (
            <div className="mt-4 animate-in fade-in border-t border-border pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {message.sources.map((source, idx) => (
                  <a 
                    key={idx} 
                    href={source.url} 
                    target="_blank" 
                    rel="noreferrer"
                    className="bg-surface hover:bg-surfaceHover border border-border p-3 rounded-lg flex items-center gap-3 transition-all duration-200 group no-underline"
                  >
                    <div className="text-xs font-semibold text-textMuted w-4 text-center">{idx + 1}</div>
                    <div className="flex-1">
                      <div className="text-sm text-textMain line-clamp-1 group-hover:text-accent transition-colors font-medium">
                        {source.title}
                      </div>
                      <div className="flex items-center gap-1.5 mt-1">
                        <img src={`https://www.google.com/s2/favicons?domain=${source.url}&sz=16`} alt="favicon" className="w-3 h-3 object-contain opacity-80" />
                        <span className="text-xs text-textMuted truncate font-mono">{new URL(source.url).hostname.replace('www.', '')}</span>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}
          
          {/* Related Questions */}
          <div className="mt-6 animate-in fade-in slide-in-from-bottom-2 duration-500 delay-300">
            <div className="flex items-center gap-2 mb-3">
               <Layers size={14} className="text-textMuted" />
               <h3 className="text-sm font-medium text-textMain uppercase tracking-wide">Related</h3>
            </div>
            <div className="flex flex-col gap-2">
               <RelatedQ question={`What are the key risks for ${message.query?.split(' ')[0] || 'this company'}?`} />
               <RelatedQ question="Show me a comparative financial analysis" />
               <RelatedQ question="What is the latest analyst consensus?" />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

const ActionBtn = ({ icon, label, onClick }: { icon: React.ReactNode, label?: string, onClick?: () => void }) => (
  <button onClick={onClick} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-surface border border-transparent hover:border-border text-textMuted hover:text-textMain transition-all text-xs font-medium">
    {icon}
    {label && <span>{label}</span>}
  </button>
);

const RelatedQ = ({ question }: { question: string }) => (
  <button className="flex items-center justify-between p-3 text-left rounded-lg border border-border/50 hover:bg-surface transition-all duration-200 group">
    <span className="text-textMain text-sm font-medium group-hover:text-accent transition-colors w-[90%] truncate">{question}</span>
    <Plus size={16} className="text-textMuted group-hover:text-accent transition-colors" />
  </button>
);
