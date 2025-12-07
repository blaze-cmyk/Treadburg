import React from 'react';

interface UpgradeBannerProps {
  onUpgradeClick: () => void;
}

export const UpgradeBanner: React.FC<UpgradeBannerProps> = ({ onUpgradeClick }) => {
  return (
    <div className="fixed bottom-6 right-6 bg-surface border border-border p-4 rounded-lg shadow-lg max-w-xs animate-in fade-in slide-in-from-bottom-4 duration-500">
      <h4 className="font-semibold text-sm text-textMain">Upgrade to Pro</h4>
      <p className="text-xs text-textMuted mt-1 mb-3">Unlock Pro models like Claude Sonnet and GPT-4, unlimited file uploads, and more.</p>
      <button 
        onClick={onUpgradeClick}
        className="w-full bg-accent text-white text-sm font-semibold py-2 rounded-md hover:bg-accent/90 transition-colors"
      >
        Upgrade
      </button>
    </div>
  );
};
