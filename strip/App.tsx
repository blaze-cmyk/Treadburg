import React, { useState, useRef, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { SearchBar } from './components/SearchBar';
import { MessageBlock } from './components/MessageBlock';
import { generateResponseStream, clearChatSession } from './services/gemini';
import { Message, Plan } from './types';
import { v4 as uuidv4 } from 'uuid';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud } from 'lucide-react';
import { PricingPage } from './components/PricingPage';
import { CheckoutPage } from './components/CheckoutPage';
import { UpgradeBanner } from './components/UpgradeBanner';

export type View = 'chat' | 'pricing' | 'checkout';

export default function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [currentView, setCurrentView] = useState<View>('chat');
  const [selectedPlan, setSelectedPlan] = useState<Plan>('pro');
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const [droppedFiles, setDroppedFiles] = useState<File[]>([]);

  const bottomRef = useRef<HTMLDivElement>(null);

  const handleNewThread = () => {
    setMessages([]);
    setHasStarted(false);
    clearChatSession();
  };
  
  const onDroppedFilesConsumed = () => {
    setDroppedFiles([]);
  };

  const handleSelectPlan = (plan: Plan) => {
    setSelectedPlan(plan);
    setCurrentView('checkout');
  };

  const handleSearch = async (query: string, files: File[]) => {
    if (!query.trim() && files.length === 0) return;

    if (!hasStarted) {
      setHasStarted(true);
    }
    setIsSearching(true);

    const attachments = await Promise.all(
      files.map(file => new Promise<{ mimeType: string; data: string; file: File }>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64Data = reader.result as string;
          const base64Content = base64Data.split(',')[1];
          resolve({
            mimeType: file.type,
            data: base64Content,
            file: file,
          });
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
      }))
    );

    const userMsg: Message = {
      id: uuidv4(),
      role: 'user',
      content: query,
      attachments
    };
    
    const aiMsgId = uuidv4();
    const aiMsg: Message = {
      id: aiMsgId,
      role: 'model',
      content: '',
      isThinking: true,
      sources: [],
      query: query
    };

    setMessages(prev => [...prev, userMsg, aiMsg]);

    try {
      await generateResponseStream(
        query,
        (text) => {
          setMessages(prev => prev.map(msg =>
            msg.id === aiMsgId ? { ...msg, content: text, isThinking: true } : msg // Keep thinking while streaming
          ));
        },
        (sources) => {
           setMessages(prev => prev.map(msg =>
            msg.id === aiMsgId ? { ...msg, sources: sources } : msg
          ));
        },
        attachments.map(({file, ...rest}) => rest) // Don't send the file object to the API
      );

      setMessages(prev => prev.map(msg =>
        msg.id === aiMsgId ? { ...msg, isThinking: false } : msg
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

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      setDroppedFiles(files);
      if (!hasStarted) {
        setHasStarted(true);
      }
    }
  };

  if (currentView === 'pricing') {
    return <PricingPage onSelectPlan={handleSelectPlan} onClose={() => setCurrentView('chat')} />;
  }

  if (currentView === 'checkout') {
    return <CheckoutPage plan={selectedPlan} onBack={() => setCurrentView('pricing')} onClose={() => setCurrentView('chat')} />;
  }

  return (
    <div className="min-h-screen bg-background text-textMain font-sans selection:bg-accent/30">
      <Sidebar onUpgradeClick={() => setCurrentView('pricing')} onNewThread={handleNewThread} />

      <main 
        className={`relative min-h-screen transition-all duration-500 ease-in-out pl-[60px] md:pl-[220px] ${hasStarted ? 'pt-8 pb-32' : 'h-screen flex items-center justify-center'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <AnimatePresence>
          {isDraggingOver && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/50 backdrop-blur-sm z-50 flex flex-col items-center justify-center pointer-events-none"
            >
              <UploadCloud size={48} className="text-white mb-4" />
              <p className="text-white text-lg font-medium">Drop files to attach</p>
            </motion.div>
          )}
        </AnimatePresence>

        {!hasStarted ? (
          <div className="w-full max-w-2xl px-4 flex flex-col items-center gap-8 -mt-20 animate-in fade-in zoom-in-95 duration-700">
            <h1 className="text-4xl md:text-5xl font-display font-medium text-center tracking-tight text-white/90">
              Where knowledge begins
            </h1>
            <div className="w-full transform transition-all hover:scale-[1.01]">
              <SearchBar onSearch={handleSearch} droppedFiles={droppedFiles} onDroppedFilesConsumed={onDroppedFilesConsumed} />
            </div>

            <div className="flex gap-4 text-xs text-textMuted mt-4">
              <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-accent"></span> Accurate</span>
              <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span> Real-time</span>
              <span className="flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span> Verified</span>
            </div>
            <UpgradeBanner onUpgradeClick={() => setCurrentView('pricing')} />
          </div>
        ) : (
          <div className="w-full max-w-3xl mx-auto px-4">
            {messages.map((msg, idx) => (
              <MessageBlock key={msg.id} message={msg} isLast={idx === messages.length - 1} />
            ))}
            <div ref={bottomRef} className="h-4" />

            <SearchBar onSearch={handleSearch} isCompact isLoading={isSearching} droppedFiles={droppedFiles} onDroppedFilesConsumed={onDroppedFilesConsumed} />
          </div>
        )}
      </main>
    </div>
  );
}
