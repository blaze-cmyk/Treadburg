import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Globe, Paperclip, ArrowUp, Search, X, Mic, Loader2, UploadCloud } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string, files: File[]) => void;
  isCompact?: boolean;
  isLoading?: boolean;
  droppedFiles?: File[];
  onDroppedFilesConsumed: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isCompact = false, isLoading = false, droppedFiles, onDroppedFilesConsumed }) => {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [query]);

  useEffect(() => {
    if (droppedFiles && droppedFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...droppedFiles]);
      onDroppedFilesConsumed(); // Signal that files have been consumed
    }
  }, [droppedFiles, onDroppedFilesConsumed]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };
  
  const handleSearch = () => {
     if (query.trim() || selectedFiles.length > 0) {
        onSearch(query, selectedFiles);
        setQuery('');
        setSelectedFiles([]);
      }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };
  
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  const renderFilePills = () => (
    <div className="flex flex-wrap gap-2 px-3 pt-3">
      {selectedFiles.map((file, index) => (
        <motion.div 
          layout
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          key={index}
          className="flex items-center gap-2 bg-surfaceHover p-2 rounded-lg"
        >
          <div className="w-10 h-10 rounded-md overflow-hidden flex-shrink-0 cursor-pointer" onClick={() => file.type.startsWith('image/') && setPreviewImage(URL.createObjectURL(file))}>
            {file.type.startsWith('image/') ? (
              <img src={URL.createObjectURL(file)} alt={file.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full bg-surface flex items-center justify-center text-textMuted">
                <Paperclip size={20} />
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-textMain truncate font-medium">{file.name}</p>
            <p className="text-xs text-textMuted">{formatFileSize(file.size)}</p>
          </div>
          <button onClick={() => removeFile(index)} className="p-1 text-textMuted hover:text-textMain transition-colors rounded-full">
            <X size={14} />
          </button>
        </motion.div>
      ))}
    </div>
  );

  const searchBarContent = (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-surface border-border border rounded-xl shadow-lg transition-all focus-within:border-accent/50 focus-within:ring-1 focus-within:ring-accent/20">
        {selectedFiles.length > 0 && renderFilePills()}
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={isCompact ? "Ask a follow-up..." : "Ask anything..."}
          rows={1}
          className="w-full bg-transparent text-textMain placeholder-textMuted/70 resize-none outline-none p-4 text-lg max-h-60"
        />
        <div className="flex items-center justify-between p-3 border-t border-border">
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium text-textMuted hover:bg-surfaceHover hover:text-textMain transition-colors">
              <Globe size={14} />
              <span>Search</span>
            </button>
            <button onClick={() => fileInputRef.current?.click()} className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium text-textMuted hover:bg-surfaceHover hover:text-textMain transition-colors">
              <Paperclip size={14} />
              <span>Attach</span>
            </button>
          </div>
          <button
            disabled={isLoading || (!query.trim() && selectedFiles.length === 0)}
            onClick={handleSearch}
            className="flex items-center justify-center w-8 h-8 rounded-full transition-all duration-200 disabled:bg-surfaceHover disabled:text-textMuted disabled:cursor-not-allowed bg-accent text-white hover:bg-accent/90"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUp size={16} />}
          </button>
        </div>
      </div>
      <input type="file" ref={fileInputRef} onChange={handleFileSelect} multiple className="hidden" accept="image/*,video/*,application/pdf" />
      <ImagePreviewModal imageUrl={previewImage} onClose={() => setPreviewImage(null)} />
       {!isCompact && (
         <div className="mt-6 flex flex-wrap gap-3 justify-center">
            <SuggestionPill label="NVDA earnings analysis" onClick={() => onSearch("NVDA earnings analysis", [])} />
            <SuggestionPill label="Is TSLA undervalued?" onClick={() => onSearch("Is TSLA undervalued?", [])} />
            <SuggestionPill label="Bitcoin price forecast" onClick={() => onSearch("Bitcoin price forecast", [])} />
            <SuggestionPill label="Macroeconomic outlook 2025" onClick={() => onSearch("Macroeconomic outlook 2025", [])} />
          </div>
        )}
    </div>
  );

  return isCompact ? (
    <div className="fixed bottom-0 left-0 right-0 z-40 bg-gradient-to-t from-background via-background/80 to-transparent">
       <div className="px-4 py-4 pl-[76px] md:pl-[240px]">
          {searchBarContent}
       </div>
    </div>
  ) : searchBarContent;
};

const SuggestionPill = ({ label, onClick }: { label: string, onClick: () => void }) => (
  <button
    onClick={onClick}
    className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface border border-border text-textMuted text-sm hover:bg-surfaceHover hover:text-textMain hover:border-textMuted/50 transition-all duration-200"
  >
    <Search size={14} />
    <span>{label}</span>
  </button>
);

const ImagePreviewModal = ({ imageUrl, onClose }: { imageUrl: string | null; onClose: () => void }) => (
  <AnimatePresence>
    {imageUrl && (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.img
          layoutId={`preview-${imageUrl}`}
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          exit={{ scale: 0.8 }}
          src={imageUrl}
          className="max-w-full max-h-full rounded-lg object-contain"
          onClick={(e) => e.stopPropagation()}
        />
        <button onClick={onClose} className="absolute top-4 right-4 text-white bg-black/50 rounded-full p-2">
          <X size={24} />
        </button>
      </motion.div>
    )}
  </AnimatePresence>
);
