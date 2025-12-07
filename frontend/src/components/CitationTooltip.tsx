import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CitationTooltipProps {
    source: string;
    page?: string;
    children: React.ReactNode;
}

export default function CitationTooltip({ source, page, children }: CitationTooltipProps) {
    const [isVisible, setIsVisible] = useState(false);

    return (
        <span
            className="relative inline-block"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
        >
            <span className="cursor-pointer text-blue-400 hover:text-blue-300 font-medium bg-blue-900/30 px-1.5 py-0.5 rounded text-xs border border-blue-800/50 transition-colors">
                {children}
            </span>

            <AnimatePresence>
                {isVisible && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.15 }}
                        className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 w-64"
                    >
                        <div className="bg-slate-900 border border-slate-700 rounded-lg shadow-xl p-3 text-xs text-gray-200">
                            <div className="font-semibold text-blue-300 mb-1 flex items-center gap-2">
                                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                Source Document
                            </div>
                            <div className="text-white font-medium mb-1">{source}</div>
                            {page && (
                                <div className="text-gray-400">
                                    Referenced on <span className="text-gray-300">Page {page}</span>
                                </div>
                            )}
                            <div className="mt-2 text-[10px] text-gray-500 uppercase tracking-wider">
                                Verified by TradeBerg
                            </div>

                            {/* Arrow */}
                            <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
                                <div className="border-8 border-transparent border-t-slate-900"></div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </span>
    );
}
