import React, { useState, useEffect, useMemo } from 'react';
import { Message } from '../types';
import { Search, Loader2, FileText, CheckCircle2, BrainCircuit, Globe } from 'lucide-react';

interface ThinkingAnimationProps {
  message: Message;
}

type AnimationStep = {
  key: string;
  title: string;
  icon: React.ElementType;
  duration: number;
  content?: (props: any) => React.ReactNode;
};

const StepIcon = ({ icon: Icon, active, done }: { icon: React.ElementType; active: boolean; done: boolean }) => {
  if (done) return <CheckCircle2 size={14} className="text-accent" />;
  if (active) return <Loader2 size={14} className="animate-spin text-accent" />;
  return <Icon size={14} className="text-textMuted/60" />;
};

const SearchQueries = ({ queries, active }: { queries: string[], active: boolean }) => {
  const [displayedCount, setDisplayedCount] = useState(0);
  useEffect(() => {
    if (active) {
      setDisplayedCount(0);
      const interval = setInterval(() => {
        setDisplayedCount(prev => {
          if (prev < queries.length) return prev + 1;
          clearInterval(interval);
          return prev;
        });
      }, 300);
      return () => clearInterval(interval);
    }
  }, [active, queries.length]);

  return (
    <div className="flex flex-col gap-1.5 pl-6 text-textMain/90">
      {queries.slice(0, displayedCount).map((q, i) => (
        <div key={i} className="animate-in fade-in slide-in-from-left-2 duration-300">{q}</div>
      ))}
    </div>
  );
};

const ReviewingSources = ({ sources, active }: { sources: Message['sources'], active: boolean }) => {
  const [reviewedIndex, setReviewedIndex] = useState(-1);

  useEffect(() => {
    if (active && sources && sources.length > 0) {
      setReviewedIndex(-1);
      const interval = setInterval(() => {
        setReviewedIndex(prev => {
          if (prev < sources.length -1) return prev + 1;
          clearInterval(interval);
          return prev;
        });
      }, 200);
      return () => clearInterval(interval);
    }
  }, [active, sources]);
  
  if (!sources || sources.length === 0) return null;

  return (
    <div className="bg-surface/50 border border-border rounded-lg p-2 flex flex-col gap-1 my-2">
      {sources.map((source, index) => (
        <div 
          key={index} 
          className={`flex items-center gap-3 p-1.5 rounded-md transition-all duration-200 ${reviewedIndex === index ? 'bg-surface' : ''}`}
        >
          <div className="w-4 h-4 flex-shrink-0 flex items-center justify-center">
            {index < reviewedIndex ? (
              <CheckCircle2 size={14} className="text-accent animate-in zoom-in duration-300" />
            ) : index === reviewedIndex ? (
              <Loader2 size={14} className="animate-spin text-accent" />
            ) : (
               <img src={`https://www.google.com/s2/favicons?domain=${source.url}&sz=16`} alt="favicon" className="w-3.5 h-3.5 object-contain opacity-50" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-textMain/80 text-xs truncate">{source.title}</div>
          </div>
          <div className="text-textMuted/60 text-xs truncate font-mono ml-auto pl-4">
            {new URL(source.url).hostname.replace('www.', '')}
          </div>
        </div>
      ))}
    </div>
  );
};


export const ThinkingAnimation: React.FC<ThinkingAnimationProps> = ({ message }) => {
  const [activeStep, setActiveStep] = useState(0);

  const searchQueries = useMemo(() => [
    `${message.query}`,
    `${message.query} latest financial data`,
    `analyst ratings for ${message.query?.split(' ')[0]}`,
    `recent news for ${message.query?.split(' ')[0]}`,
  ], [message.query]);

  const steps: AnimationStep[] = useMemo(() => [
    { key: 'assess', title: `Assessing how to answer...`, icon: BrainCircuit, duration: 800 },
    { 
      key: 'search', 
      title: 'Searching', 
      icon: Search, 
      duration: searchQueries.length * 300 + 500,
      content: ({active}) => <SearchQueries queries={searchQueries} active={active} />
    },
    { 
      key: 'review', 
      title: `Reviewing ${message.sources?.length || 0} sources`, 
      icon: FileText, 
      duration: (message.sources?.length || 0) * 200 + 500,
      content: ({active}) => <ReviewingSources sources={message.sources} active={active} />
    },
    { key: 'finish', title: 'Finished', icon: CheckCircle2, duration: 999999 }, // Stays on finished
  ], [message.sources, searchQueries]);

  useEffect(() => {
    if (activeStep < steps.length - 1) {
      const timer = setTimeout(() => {
        setActiveStep(prev => prev + 1);
      }, steps[activeStep].duration);
      return () => clearTimeout(timer);
    }
  }, [activeStep, steps]);

  return (
    <div className="flex flex-col gap-4 text-sm">
      {steps.slice(0, activeStep + 1).map((step, index) => {
        const isStepActive = index === activeStep;
        const isStepDone = index < activeStep;
        return (
          <div key={step.key} className="animate-in fade-in duration-500">
            <div className="flex items-center gap-2.5 text-textMuted mb-2">
              <StepIcon icon={step.icon} active={isStepActive} done={isStepDone} />
              <span className={`font-medium ${isStepDone ? 'text-textMuted/70' : 'text-textMain'}`}>{step.title}</span>
            </div>
            {step.content && (
              <div className="pl-1">
                {step.content({ active: isStepActive })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
