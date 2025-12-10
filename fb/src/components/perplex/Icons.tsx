import React from 'react';
import { Compass, Library, Plus, ArrowRight, Paperclip, Globe, Search, MoreHorizontal, User, Layers, Share, Copy, ThumbsUp, ThumbsDown, StopCircle } from 'lucide-react';

export const Logo = () => (
    <div className="flex items-center gap-2 font-display font-medium text-2xl text-perplex-textMain">
        <span className="text-3xl">perplexity</span>
        <span className="text-xs bg-perplex-surface border border-perplex-border px-1.5 py-0.5 rounded text-perplex-accent font-mono uppercase tracking-wider">Pro</span>
    </div>
);

export { Compass, Library, Plus, ArrowRight, Paperclip, Globe, Search, MoreHorizontal, User, Layers, Share, Copy, ThumbsUp, ThumbsDown, StopCircle };
