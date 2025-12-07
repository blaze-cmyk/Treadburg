import React from 'react';
import { Compass, Library, Search, Plus, Zap } from 'lucide-react';

interface SidebarProps {
  onUpgradeClick: () => void;
  onNewThread: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onUpgradeClick, onNewThread }) => {
  return (
    <div className="fixed left-0 top-0 h-full w-[60px] md:w-[220px] bg-background border-r border-border flex flex-col justify-between py-4 z-50 transition-all duration-300">
      <div className="flex flex-col gap-2 px-3">
        <div className="md:hidden flex justify-center mb-6">
           <div className="w-8 h-8 bg-white rounded-full"></div>
        </div>
        <div className="hidden md:flex items-center gap-2 px-3 mb-6">
           <h1 className="text-2xl font-medium tracking-tight text-white font-display">TradeBerg</h1>
        </div>

        <button onClick={onNewThread} className="flex items-center gap-3 px-3 py-2 text-textMain bg-surface rounded-full border border-border shadow-sm hover:border-gray-500 transition-colors group">
          <Plus size={20} className="text-textMuted group-hover:text-textMain" />
          <span className="hidden md:block text-sm font-medium">New Thread</span>
          <span className="hidden md:block text-xs text-textMuted ml-auto border border-border px-1 rounded">Ctrl I</span>
        </button>

        <div className="mt-4 flex flex-col gap-1">
          <NavItem icon={<Search size={20} />} label="Home" active />
          <NavItem icon={<Compass size={20} />} label="Discover" />
          <NavItem icon={<Library size={20} />} label="Library" />
        </div>
        
      </div>

      <div className="px-3 flex flex-col gap-1">
         <NavItem icon={<Zap size={20} />} label="Upgrade" onClick={onUpgradeClick} />
      </div>
    </div>
  );
};

// FIX: Corrected a typo in the React type. `React.React.Node` is invalid and was changed to `React.ReactNode`.
const NavItem = ({ icon, label, active = false, onClick }: { icon: React.ReactNode, label: string, active?: boolean, onClick?: () => void }) => (
  <button onClick={onClick} className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${active ? 'bg-surface text-textMain' : 'text-textMuted hover:bg-surface/50 hover:text-textMain'}`}>
    {icon}
    <span className="hidden md:block text-sm font-medium">{label}</span>
  </button>
);