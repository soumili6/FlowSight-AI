import React from 'react';
import { 
  Video, 
  Car, 
  Bike, 
  Bus, 
  Truck, 
  Gauge, 
  AlertTriangle, 
  TrendingUp, 
  ArrowRight, 
  Play, 
  Upload, 
  Sparkles 
} from 'lucide-react';
import MetricCard from '../components/MetricCard';

export default function OverviewPage({ 
  stats, 
  onSelectVideo, 
  setActiveTab, 
  onLoadSample, 
  loadingSample 
}) {
  const breakdown = stats?.vehicle_breakdown || { cars: 0, motorcycles: 0, buses: 0, trucks: 0 };
  const totalVehicles = stats?.total_vehicles_counted || 0;
  const recent = stats?.recent_analyses || [];

  const getPercent = (count) => {
    if (!totalVehicles) return 0;
    return Math.round((count / totalVehicles) * 100);
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-900/60 via-indigo-900/40 to-slate-900/80 p-8 border border-blue-500/30 backdrop-blur-md">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 text-cyan-300 text-xs font-semibold mb-3 border border-cyan-400/30">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Computer Vision Telemetry</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight sm:text-4xl">
            Intelligent Traffic Monitoring & Density Analytics
          </h1>
          <p className="mt-3 text-slate-300 text-sm leading-relaxed">
            FlowSight AI processes high-definition road footage using deep neural network YOLO vehicle detection and ByteTrack multi-object tracking. Calculate vehicle densities, detect congestion bottlenecks, and visualize traffic telemetry across vehicle classes.
          </p>

          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => setActiveTab('upload')}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium text-sm shadow-lg shadow-blue-600/30 transition-all hover:scale-[1.02]"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Video</span>
            </button>
            <button
              onClick={onLoadSample}
              disabled={loadingSample}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-[#0f1c3a] hover:bg-[#152449] border border-cyan-500/30 text-cyan-300 font-medium text-sm transition-all hover:scale-[1.02] disabled:opacity-50"
            >
              <Play className="w-4 h-4 text-cyan-400" />
              <span>{loadingSample ? 'Loading Demo Video...' : 'Load Demo Highway Video'}</span>
            </button>
          </div>
        </div>

        {/* Ambient glow decoration */}
        <div className="absolute right-0 top-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />
        <div className="absolute right-32 bottom-0 -mb-16 w-64 h-64 rounded-full bg-blue-600/15 blur-2xl pointer-events-none" />
      </div>

      {/* High-level Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Total Videos Analyzed"
          value={stats?.total_videos_analyzed || 0}
          subtitle="Processed traffic sessions"
          icon={Video}
          color="blue"
        />
        <MetricCard
          title="Vehicles Counted"
          value={totalVehicles}
          subtitle="Unique tracked vehicles"
          icon={TrendingUp}
          color="emerald"
        />
        <MetricCard
          title="Avg Traffic Density"
          value={`${stats?.average_system_density || 0}`}
          subtitle="Vehicles per camera frame"
          icon={Gauge}
          color="cyan"
        />
        <MetricCard
          title="Congestion Incidents"
          value={stats?.high_congestion_incidents || 0}
          subtitle="High density bottlenecks"
          icon={AlertTriangle}
          color="amber"
        />
      </div>

      {/* Vehicle Category Breakdown */}
      <div>
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center space-x-2">
          <span>Vehicle Category Breakdown</span>
          <span className="text-xs text-slate-500 font-normal">({totalVehicles} total vehicles)</span>
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Cars */}
          <div className="p-5 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Car className="w-4 h-4" />
                <span>Cars</span>
              </span>
              <span className="text-xs text-slate-400 font-mono">{getPercent(breakdown.cars)}%</span>
            </div>
            <div className="text-2xl font-bold text-white">{breakdown.cars}</div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
              <div 
                className="bg-emerald-500 h-full rounded-full transition-all duration-500" 
                style={{ width: `${getPercent(breakdown.cars)}%` }}
              />
            </div>
          </div>

          {/* Motorcycles */}
          <div className="p-5 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Bike className="w-4 h-4" />
                <span>Motorcycles</span>
              </span>
              <span className="text-xs text-slate-400 font-mono">{getPercent(breakdown.motorcycles)}%</span>
            </div>
            <div className="text-2xl font-bold text-white">{breakdown.motorcycles}</div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
              <div 
                className="bg-amber-500 h-full rounded-full transition-all duration-500" 
                style={{ width: `${getPercent(breakdown.motorcycles)}%` }}
              />
            </div>
          </div>

          {/* Buses */}
          <div className="p-5 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Bus className="w-4 h-4" />
                <span>Buses</span>
              </span>
              <span className="text-xs text-slate-400 font-mono">{getPercent(breakdown.buses)}%</span>
            </div>
            <div className="text-2xl font-bold text-white">{breakdown.buses}</div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
              <div 
                className="bg-cyan-500 h-full rounded-full transition-all duration-500" 
                style={{ width: `${getPercent(breakdown.buses)}%` }}
              />
            </div>
          </div>

          {/* Trucks */}
          <div className="p-5 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider flex items-center space-x-1.5">
                <Truck className="w-4 h-4" />
                <span>Heavy Trucks</span>
              </span>
              <span className="text-xs text-slate-400 font-mono">{getPercent(breakdown.trucks)}%</span>
            </div>
            <div className="text-2xl font-bold text-white">{breakdown.trucks}</div>
            <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
              <div 
                className="bg-purple-500 h-full rounded-full transition-all duration-500" 
                style={{ width: `${getPercent(breakdown.trucks)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Recent Analyses or Empty State */}
      <div className="bg-[#0f1c3a]/60 rounded-2xl border border-[#152449] p-6 backdrop-blur-md">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-base font-semibold text-white tracking-tight">
            Recent Video Analyses
          </h3>
          <button
            onClick={() => setActiveTab('history')}
            className="text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center space-x-1 transition-colors"
          >
            <span>View All History</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {recent.length === 0 ? (
          <div className="text-center py-12 px-4 rounded-xl border border-dashed border-[#1e3363]/80 bg-[#070d18]/40">
            <div className="w-12 h-12 mx-auto rounded-full bg-blue-500/10 flex items-center justify-center mb-3 text-cyan-400">
              <Video className="w-6 h-6" />
            </div>
            <h4 className="text-base font-semibold text-white">No Traffic Videos Analyzed Yet</h4>
            <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 mb-5">
              Upload a traffic video file (MP4, AVI, MOV) or load the bundled test video to start detecting, tracking, and estimating traffic density.
            </p>
            <div className="flex justify-center gap-3">
              <button
                onClick={() => setActiveTab('upload')}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20"
              >
                Upload Video
              </button>
              <button
                onClick={onLoadSample}
                disabled={loadingSample}
                className="px-4 py-2 rounded-lg bg-[#152449] hover:bg-[#1e3363] text-cyan-300 text-xs font-semibold border border-cyan-500/20"
              >
                {loadingSample ? 'Loading Demo...' : 'Load Demo Video'}
              </button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#1e3363]/60 text-slate-400 uppercase tracking-wider">
                  <th className="pb-3 font-medium">Video</th>
                  <th className="pb-3 font-medium">Analyzed At</th>
                  <th className="pb-3 font-medium">Counted</th>
                  <th className="pb-3 font-medium">Avg Density</th>
                  <th className="pb-3 font-medium">Congestion</th>
                  <th className="pb-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#152449]/40">
                {recent.map((item) => (
                  <tr key={item.id} className="hover:bg-[#152449]/30 transition-colors">
                    <td className="py-3.5 pr-4 font-medium text-slate-200 flex items-center space-x-2">
                      <Video className="w-4 h-4 text-cyan-400 shrink-0" />
                      <span className="truncate max-w-[180px]">{item.video_filename || 'Traffic Footage'}</span>
                    </td>
                    <td className="py-3.5 pr-4 text-slate-400">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 pr-4 text-white font-semibold">
                      {item.total_vehicles_counted}
                    </td>
                    <td className="py-3.5 pr-4 text-slate-300 font-mono">
                      {item.average_density} / frame
                    </td>
                    <td className="py-3.5 pr-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                        item.congestion_level === 'High'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : item.congestion_level === 'Medium'
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      }`}>
                        {item.congestion_level}
                      </span>
                    </td>
                    <td className="py-3.5 text-right space-x-2">
                      <button
                        onClick={() => onSelectVideo(item.video_id, item.id, 'monitoring')}
                        className="px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/40 text-cyan-300 border border-cyan-500/20 text-[11px] font-medium"
                      >
                        Monitoring
                      </button>
                      <button
                        onClick={() => onSelectVideo(item.video_id, item.id, 'analytics')}
                        className="px-2.5 py-1 rounded bg-[#1e3363]/50 hover:bg-[#1e3363] text-slate-200 text-[11px] font-medium"
                      >
                        Analytics
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
