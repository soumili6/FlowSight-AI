import React from 'react';
import { Sparkles, Shield, RefreshCw } from 'lucide-react';

export default function Navbar({ activeTab, onRefresh, isRefreshing }) {
  const titles = {
    overview: 'System Overview & Telemetry',
    upload: 'Video Ingestion & Analysis Configuration',
    monitoring: 'Real-Time Vision & Traffic Stream',
    analytics: 'Deep Traffic Analytics & Flow Trends',
    history: 'Video Analysis History & Archives',
  };

  return (
    <header className="h-16 bg-[#0b1329]/90 backdrop-blur-md border-b border-[#152449] px-8 flex items-center justify-between sticky top-0 z-30">
      <div>
        <h2 className="text-lg font-semibold text-white tracking-tight">
          {titles[activeTab] || 'FlowSight AI'}
        </h2>
        <p className="text-xs text-slate-400">
          Intelligent Multi-Class Vehicle Detection & Density Classification
        </p>
      </div>

      <div className="flex items-center space-x-4">
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#0f1c3a] hover:bg-[#152449] border border-[#1e3363] text-xs font-medium text-slate-300 hover:text-white transition-all disabled:opacity-50"
            title="Refresh dashboard data"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        )}

        <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-blue-950/40 border border-blue-500/20 text-xs text-blue-300">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>v1.0 CSE Portfolio Edition</span>
        </div>
      </div>
    </header>
  );
}
