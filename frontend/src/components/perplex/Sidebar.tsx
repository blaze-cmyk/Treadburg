import React from 'react';
import { Compass, Library, User, Search, Plus, Layers } from 'lucide-react';

export const Sidebar = () => {
    return (
        <div className="fixed left-0 top-0 h-full w-[60px] md:w-[220px] bg-perplex-bg border-r border-perplex-border flex flex-col justify-between py-4 z-50 transition-all duration-300">
            <div className="flex flex-col gap-2 px-3">
                <div className="md:hidden flex justify-center mb-6">
                    <div className="w-8 h-8 bg-white rounded-full"></div>
                </div>
                <div className="hidden md:flex items-center gap-2 px-3 mb-6">
                    <h1 className="text-2xl font-medium tracking-tight text-white font-display">tradeberg</h1>
                </div>

                <button className="flex items-center gap-3 px-3 py-2 text-perplex-textMain bg-perplex-surface rounded-full border border-perplex-border shadow-sm hover:border-gray-500 transition-colors group">
                    <Plus size={20} className="text-perplex-textMuted group-hover:text-perplex-textMain" />
                    <span className="hidden md:block text-sm font-medium">New Thread</span>
                    <span className="hidden md:block text-xs text-perplex-textMuted ml-auto border border-perplex-border px-1 rounded">Ctrl I</span>
                </button>

                <div className="mt-4 flex flex-col gap-1">
                    <NavItem icon={<Search size={20} />} label="Home" active />
                    <NavItem icon={<Compass size={20} />} label="Discover" />
                    <NavItem icon={<Library size={20} />} label="Library" />
                </div>

                {/* Auth section usually here but simplified for UI clone */}
            </div>

            <div className="px-3 flex flex-col gap-1">
                <NavItem icon={<User size={20} />} label="Profile" />
            </div>
        </div>
    );
};

const NavItem = ({ icon, label, active = false }: { icon: React.ReactNode, label: string, active?: boolean }) => (
    <button className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${active ? 'bg-perplex-surface text-perplex-textMain' : 'text-perplex-textMuted hover:bg-perplex-surface/50 hover:text-perplex-textMain'}`}>
        {icon}
        <span className="hidden md:block text-sm font-medium">{label}</span>
    </button>
);
