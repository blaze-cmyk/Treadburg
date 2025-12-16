"use client";

import React from "react";
import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import FinancialChart from "../chart/FinancialChart";
import CitationTooltip from "../CitationTooltip";

interface AnimatedMessageBubbleProps {
  message: {
    id: number | string;
    role: string;
    content: string;
  };
  index: number;
}

export default function AnimatedMessageBubble({
  message,
  index,
}: AnimatedMessageBubbleProps) {
  const isUser = message.role === "user";

  // Simple fade-in-up animation for new messages
  // Matches the CSS keyframe animation from Step 6
  const bubbleVariants: any = {
    hidden: {
      opacity: 0,
      y: 10,
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        ease: "easeOut",
      },
    },
  };

  // Subtle floating animation for assistant messages only
  const floatingVariants: any = {
    float: {
      y: [0, -4, 0],
      transition: {
        duration: 4,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  // Staggered list animation variants
  const listContainerVariants: any = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1, // Stagger list items
      },
    },
  };

  const listItemVariants: any = {
    hidden: { opacity: 0, y: 5 },
    show: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut",
      },
    },
  };

  // Extract hidden metadata from content
  const metadataMatch = message.content.match(/<!-- GROUNDING_METADATA: (.*?) -->/);
  let groundingMetadata: any = null;
  let displayContent = message.content;

  if (metadataMatch) {
    try {
      groundingMetadata = JSON.parse(metadataMatch[1]);
      // Remove the hidden block from display
      displayContent = message.content.replace(metadataMatch[0], "").trim();
    } catch (e) {
      console.error("Failed to parse grounding metadata", e);
    }
  }

  return (
    <motion.div
      className={`w-3xl py-4 px-5 rounded-xl transition-all duration-300 chat-message ${isUser
        ? "max-w-2xl w-auto self-end bg-slate-700/50 backdrop-blur-sm text-white border border-slate-600/30"
        : "self-start bg-slate-800/40 backdrop-blur-sm text-gray-100 border border-slate-700/30 max-w-4xl"
        }`}
      initial="hidden"
      animate="visible"
      variants={bubbleVariants}
      whileHover={{
        scale: 1.02,
        transition: { duration: 0.2 },
      }}
    >
      <motion.div
        variants={floatingVariants}
        animate={!isUser ? "float" : undefined}
      >
        <ReactMarkdown
          children={displayContent}
          rehypePlugins={[rehypeHighlight]}
          className="prose prose-sm max-w-none break-words prose-invert dark:prose-invert 
            prose-headings:text-white prose-h1:text-2xl prose-h2:text-xl prose-h2:mt-6 prose-h2:mb-3
            prose-p:text-gray-100 prose-p:leading-relaxed
            prose-strong:text-white prose-strong:font-semibold
            prose-code:text-blue-300 prose-code:bg-slate-700/50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded
            prose-pre:bg-slate-900/50 prose-pre:border prose-pre:border-slate-700
            prose-table:border-collapse prose-table:w-full
            prose-th:bg-slate-700/50 prose-th:text-white prose-th:font-semibold prose-th:p-3 prose-th:border prose-th:border-slate-600
            prose-td:text-gray-100 prose-td:p-3 prose-td:border prose-td:border-slate-700
            prose-tr:border-slate-700
            prose-ul:text-gray-100 prose-ol:text-gray-100
            prose-li:text-gray-100 prose-li:marker:text-blue-400
            prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline"
          components={{
            // Custom renderer for text nodes to catch [Source: ...] tags
            p({ node, children, ...props }) {
              // We need to process the children to find citation patterns
              const processChildren = (child: React.ReactNode): React.ReactNode => {
                if (typeof child === 'string') {
                  // Regex to match [Source: DocName, Page X] or just [Source: DocName]
                  const parts = child.split(/(\[Source: .*?\])/g);

                  return parts.map((part, i) => {
                    const match = part.match(/\[Source: (.*?)\]/);
                    if (match) {
                      const content = match[1]; // "DocName, Page X"
                      // Split into Source and Page
                      const [source, pagePart] = content.split(', Page');
                      const page = pagePart ? pagePart.trim() : undefined;

                      return (
                        <CitationTooltip key={i} source={source} page={page}>
                          {part}
                        </CitationTooltip>
                      );
                    }
                    return part;
                  });
                }

                // Recursively process arrays or other elements
                if (Array.isArray(child)) {
                  return child.map((c, i) => <React.Fragment key={i}>{processChildren(c)}</React.Fragment>);
                }

                // If it's a React element with children, we might want to process them too, 
                // but usually citations are in plain text paragraphs.
                return child;
              };

              return (
                <p className="mb-4 leading-relaxed text-gray-100" {...props}>
                  {React.Children.map(children, processChildren)}
                </p>
              );
            },
            // Staggered list items
            ul({ node, children, ...props }) {
              return (
                <motion.ul
                  variants={listContainerVariants}
                  initial="hidden"
                  animate="show"
                  {...(props as any)}
                >
                  {children}
                </motion.ul>
              );
            },
            ol({ node, children, ...props }) {
              return (
                <motion.ol
                  variants={listContainerVariants}
                  initial="hidden"
                  animate="show"
                  {...(props as any)}
                >
                  {children}
                </motion.ol>
              );
            },
            li({ node, children, ...props }) {
              return (
                <motion.li variants={listItemVariants} {...(props as any)}>
                  {children}
                </motion.li>
              );
            },
            code({ node, inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || '');
              const language = match ? match[1] : '';
              const contentString = String(children).replace(/\n$/, '');

              // Check for json-chart blocks
              const isJsonChart = language === 'json-chart';
              const looksLikeChartData = language === 'json' &&
                contentString.includes('"series"') &&
                contentString.includes('"data"') &&
                contentString.includes('"values"');

              if (!inline && (isJsonChart || looksLikeChartData)) {
                try {
                  const data = JSON.parse(contentString);
                  return (
                    <div className="not-prose my-4">
                      <FinancialChart data={data} />
                    </div>
                  );
                } catch (e) {
                  console.error("Failed to parse chart JSON", e);
                  return <code className={className} {...props}>{children}</code>;
                }
              }

              if (inline) {
                return (
                  <code className="bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-1 rounded">
                    {children}
                  </code>
                );
              }

              return (
                <pre className="py-4 rounded-lg overflow-x-auto bg-gray-900 dark:bg-[var(--tradeberg-bg)]">
                  <code
                    className={`${className} font-mono`}
                    {...props}
                    style={{ background: "#111827", color: "#e5e7eb" }}
                  >
                    {children}
                  </code>
                </pre>
              );
            },
          }}
        />

        {/* Grounding Sources UI - Exact Port from Old Project */}
        {groundingMetadata && groundingMetadata.groundingChunks && groundingMetadata.groundingChunks.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-700/50">
            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Sources</h4>
            <div className="flex flex-wrap gap-2">
              {groundingMetadata.groundingChunks.map((chunk: any, idx: number) => {
                if (chunk.web) {
                  return (
                    <a
                      key={idx}
                      href={chunk.web.uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/50 hover:bg-slate-700/50 rounded-lg text-xs font-medium text-blue-400 hover:text-blue-300 transition-colors border border-slate-700/50"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-globe"><circle cx="12" cy="12" r="10" /><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" /><path d="M2 12h20" /></svg>
                      <span className="truncate max-w-[180px]">{chunk.web.title}</span>
                    </a>
                  );
                }
                return null;
              })}
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
