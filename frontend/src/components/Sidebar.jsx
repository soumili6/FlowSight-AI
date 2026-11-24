import React from 'react';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Video, 
  BarChart3, 
  History, 
  Cpu, 
  ShieldCheck, 
  Activity 
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, systemHealth }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'upload', label: 'Video Upload', icon: UploadCloud },
    { id: 'monitoring', label: 'Live Monitoring', icon: Video },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'history', label: 'History', icon: History },
  ];

  return (
    <aside className="w-64 bg-[#070d18] border-r border-[#152449] flex flex-col justify-between shrink-0 h-screen sticky top-0 select-none">
      {/* Brand Header */}
      <div>
        <div className="p-6 border-b border-[#152449]/70 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Activity className="w-6 h-6 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              FlowSight <span className="text-cyan-400">AI</span>
            </h1>
            <p className="text-xs text-slate-400 font-medium tracking-wide">
              Traffic Vision System
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-1.5">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 py-2">
            Main Navigation
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600/20 text-cyan-400 border border-cyan-500/30 shadow-md shadow-blue-900/20'
                    : 'text-slate-300 hover:text-white hover:bg-[#0f1c3a]/70'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer System Status */}
      <div className="p-4 border-t border-[#152449]/70 bg-[#09101f]">
        <div className="bg-[#0f1c3a]/80 rounded-xl p-3 border border-[#1e3363]/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-semibold text-slate-300 flex items-center space-x-1.5">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span>Engine Status</span>
            </span>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>
          <div className="text-xs text-slate-300 font-mono flex items-center justify-between">
            <span>Model:</span>
            <span className="text-cyan-300 font-semibold">YOLOv8n + ByteTrack</span>
          </div>
          <div className="text-[10px] text-slate-400 mt-1 flex items-center justify-between">
            <span>Status:</span>
            <span className="text-emerald-400">Online & Ready</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
