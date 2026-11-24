import React from 'react';

export default function MetricCard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorStyles = {
    blue: 'from-blue-600/10 to-blue-500/5 border-blue-500/20 text-blue-400 icon-bg:bg-blue-500/10',
    cyan: 'from-cyan-600/10 to-cyan-500/5 border-cyan-500/20 text-cyan-400 icon-bg:bg-cyan-500/10',
    emerald: 'from-emerald-600/10 to-emerald-500/5 border-emerald-500/20 text-emerald-400 icon-bg:bg-emerald-500/10',
    amber: 'from-amber-600/10 to-amber-500/5 border-amber-500/20 text-amber-400 icon-bg:bg-amber-500/10',
    rose: 'from-rose-600/10 to-rose-500/5 border-rose-500/20 text-rose-400 icon-bg:bg-rose-500/10',
  };

  const selected = colorStyles[color] || colorStyles.blue;

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-br ${selected} border backdrop-blur-md transition-all hover:scale-[1.01] hover:shadow-xl hover:shadow-black/20`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <div className={`p-2 rounded-xl bg-[#0b1329]/60 border border-slate-700/30 ${selected.split(' ')[2]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-3xl font-extrabold text-white tracking-tight">
          {value}
        </span>
        {trend && (
          <span className="text-xs font-semibold text-cyan-400">
            {trend}
          </span>
        )}
      </div>
      {subtitle && (
        <p className="text-xs text-slate-400 mt-1.5 font-medium">
          {subtitle}
        </p>
      )}
    </div>
  );
}
