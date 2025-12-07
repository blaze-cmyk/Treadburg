import React from 'react';
import { motion } from 'framer-motion';
import { X, Check } from 'lucide-react';
import { Plan } from '../types';

interface PricingPageProps {
  onSelectPlan: (plan: Plan) => void;
  onClose: () => void;
}

const FeatureItem = ({ text }: { text: string }) => (
  <li className="flex items-start gap-3">
    <Check size={16} className="text-accent flex-shrink-0 mt-0.5" />
    <span className="text-textMuted">{text}</span>
  </li>
);

export const PricingPage: React.FC<PricingPageProps> = ({ onSelectPlan, onClose }) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-background text-textMain z-50 flex flex-col items-center justify-center p-4"
    >
      <button onClick={onClose} className="absolute top-6 right-6 text-textMuted hover:text-textMain transition-colors">
        <X size={24} />
      </button>

      <div className="w-full max-w-4xl animate-in fade-in zoom-in-95 duration-300">
        <h1 className="text-4xl font-bold text-center text-white mb-4">Upgrade to Pro</h1>
        
        <div className="flex justify-center mb-8">
          <div className="bg-surface p-1 rounded-lg flex items-center gap-1 text-sm">
            <button className="px-4 py-1.5 rounded-md bg-surfaceHover text-white font-semibold">Personal</button>
            <button className="px-4 py-1.5 rounded-md text-textMuted hover:text-white">Education</button>
            <button className="px-4 py-1.5 rounded-md text-textMuted hover:text-white">Business</button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Pro Plan */}
          <div className="bg-surface border border-border p-8 rounded-xl flex flex-col">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-2xl font-semibold text-white">Pro</h2>
              <span className="bg-accent/10 text-accent text-xs font-bold px-2 py-1 rounded-full">Popular</span>
            </div>
            <p className="text-4xl font-light text-white mb-2">$20.00 <span className="text-base text-textMuted">USD / month</span></p>
            <p className="text-sm text-textMuted mb-6">Upgrade productivity and learning with additional access.</p>
            <button onClick={() => onSelectPlan('pro')} className="w-full bg-accent text-white py-3 rounded-lg font-semibold hover:bg-accent/90 transition-colors">
              Get Pro
            </button>

            <ul className="mt-8 space-y-4 text-sm flex-1">
              <FeatureItem text="10x as many citations in answers" />
              <FeatureItem text="Access to Perplexity Labs" />
              <FeatureItem text="Unlimited file and photo uploads" />
              <FeatureItem text="Extended access to Perplexity Research" />
              <FeatureItem text="Extended access to image generation" />
              <FeatureItem text="One subscription to the latest AI models" />
            </ul>
            <p className="text-xs text-textMuted mt-8">Existing subscriber? See <a href="#" className="underline hover:text-white">billing help</a>.</p>
          </div>

          {/* Max Plan */}
          <div className="bg-surface border border-border p-8 rounded-xl flex flex-col">
            <h2 className="text-2xl font-semibold text-white mb-2">Max</h2>
            <p className="text-4xl font-light text-white mb-2">$200.00 <span className="text-base text-textMuted">USD / month</span></p>
            <p className="text-sm text-textMuted mb-6">Unlock TradeBerg's full capabilities with early access to new products.</p>
            <button onClick={() => onSelectPlan('max')} className="w-full bg-surfaceHover text-textMain py-3 rounded-lg font-semibold border border-border hover:bg-white hover:text-black transition-colors">
              Get Max
            </button>

            <ul className="mt-8 space-y-4 text-sm flex-1">
              <FeatureItem text="Everything in Pro" />
              <FeatureItem text="Early access to our newest products" />
              <FeatureItem text="Unlimited access to advanced AI models from OpenAI and Anthropic" />
              <FeatureItem text="Enhanced access to video generation" />
              <FeatureItem text="Priority support" />
            </ul>
            <p className="text-xs text-textMuted mt-8">For personal use only and subject to our <a href="#" className="underline hover:text-white">policies</a>.</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};