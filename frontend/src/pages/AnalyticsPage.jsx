import React, { useState, useEffect } from 'react';
import { 
  AreaChart, 
  Area, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';
import { 
  BarChart3, 
  TrendingUp, 
  PieChart as PieIcon, 
  Clock, 
  Activity, 
  Zap, 
  Download 
} from 'lucide-react';
import { getAnalysis, getHistory } from '../services/api';

const PIE_COLORS = ['#10b981', '#f59e0b', '#06b6d4', '#a855f7'];

export default function AnalyticsPage({ 
  selectedAnalysisId, 
  selectedVideoId, 
  setActiveTab 
}) {
  const [analysis, setAnalysis] = useState(null);
  const [historyList, setHistoryList] = useState([]);
  const [currentId, setCurrentId] = useState(selectedAnalysisId);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHistoryList();
  }, []);

  useEffect(() => {
    if (selectedAnalysisId) {
      setCurrentId(selectedAnalysisId);
    }
  }, [selectedAnalysisId]);

  useEffect(() => {
    if (currentId) {
      fetchAnalysis(currentId);
    } else if (historyList.length > 0 && !currentId) {
      setCurrentId(historyList[0].id);
    }
  }, [currentId, historyList]);

  const loadHistoryList = async () => {
    try {
      const res = await getHistory();
      setHistoryList(res.analyses || []);
      if (res.analyses?.length > 0 && !currentId) {
        setCurrentId(res.analyses[0].id);
      }
    } catch (err) {
      console.error('Failed to load history list:', err);
    }
  };

  const fetchAnalysis = async (id) => {
    setLoading(true);
    try {
      const res = await getAnalysis(id);
      setAnalysis(res.analysis);
    } catch (err) {
      console.error('Failed to load analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!analysis && !loading) {
    return (
      <div className="text-center py-20 px-4 max-w-md mx-auto">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-cyan-400 mb-4">
          <BarChart3 className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-white">No Analytics Data Available</h3>
        <p className="text-xs text-slate-400 mt-2 mb-6">
          Analyze a video first to visualize vehicle flow rates, category distributions, and congestion trends over time.
        </p>
        <button
          onClick={() => setActiveTab('upload')}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-600/30"
        >
          Upload and Analyze Video
        </button>
      </div>
    );
  }

  // Format Timeline points for Recharts
  const timelineData = (analysis?.timeline || []).map((tp) => ({
    time: `${tp.timestamp_sec}s`,
    timestamp: tp.timestamp_sec,
    activeVehicles: tp.active_vehicles,
    cumulative: tp.cumulative_count,
    density: tp.density,
    cars: tp.car_count,
    motorcycles: tp.motorcycle_count,
    buses: tp.bus_count,
    trucks: tp.truck_count,
    congestionLevel: tp.congestion_level,
  }));

  // Bar & Pie Chart Data
  const categoryData = [
    { name: 'Cars', count: analysis?.car_count || 0, color: '#10b981' },
    { name: 'Motorcycles', count: analysis?.motorcycle_count || 0, color: '#f59e0b' },
    { name: 'Buses', count: analysis?.bus_count || 0, color: '#06b6d4' },
    { name: 'Trucks', count: analysis?.truck_count || 0, color: '#a855f7' },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Session Header & Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#0f1c3a]/70 border border-[#1e3363]/60 backdrop-blur-md">
        <div>
          <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
            Flow Analytics Report
          </span>
          <h2 className="text-xl font-bold text-white mt-0.5">
            {analysis?.video_filename || 'Traffic Session Analytics'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Processed on {new Date(analysis?.created_at).toLocaleString()} • {analysis?.total_frames_analyzed} frames analyzed
          </p>
        </div>

        {/* Session Dropdown */}
        {historyList.length > 1 && (
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">Select Session:</span>
            <select
              value={currentId || ''}
              onChange={(e) => setCurrentId(e.target.value)}
              className="bg-[#0b1329] border border-[#1e3363] text-xs text-slate-200 rounded-lg px-3 py-2 outline-none focus:border-cyan-400"
            >
              {historyList.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.video_filename || 'Video'} ({new Date(item.created_at).toLocaleTimeString()})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0f1c3a]/60 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400">Total Vehicles Counted</span>
          <div className="text-2xl font-bold text-white mt-1">
            {analysis?.total_vehicles_counted || 0}
          </div>
          <span className="text-[11px] text-emerald-400">Unique crossing tracks</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0f1c3a]/60 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400">Peak Density</span>
          <div className="text-2xl font-bold text-cyan-400 mt-1">
            {analysis?.peak_density || 0}
          </div>
          <span className="text-[11px] text-slate-400">Vehicles / frame max</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0f1c3a]/60 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400">Processing Speed</span>
          <div className="text-2xl font-bold text-white mt-1">
            {analysis?.processing_time_seconds || 0}s
          </div>
          <span className="text-[11px] text-slate-400">Total compute time</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0f1c3a]/60 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400">Congestion Level</span>
          <div className="text-2xl font-bold text-amber-400 mt-1">
            {analysis?.congestion_level || 'Low'}
          </div>
          <span className="text-[11px] text-slate-400">Index: {analysis?.congestion_score || 0}%</span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Active Vehicles & Density Trend */}
        <div className="p-6 rounded-2xl bg-[#0f1c3a]/60 border border-[#1e3363]/60 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Active Vehicle Density Over Time
              </h3>
              <p className="text-xs text-slate-400">
                Live vehicle presence per second in camera view
              </p>
            </div>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timelineData}>
                <defs>
                  <linearGradient id="densityGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e3363" opacity={0.5} />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#070d18', borderColor: '#1e3363', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="activeVehicles" 
                  name="Active Vehicles"
                  stroke="#06b6d4" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#densityGrad)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Cumulative Flow Rate */}
        <div className="p-6 rounded-2xl bg-[#0f1c3a]/60 border border-[#1e3363]/60 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Cumulative Traffic Throughput
              </h3>
              <p className="text-xs text-slate-400">
                Total vehicle arrivals crossing virtual detection line
              </p>
            </div>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e3363" opacity={0.5} />
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#070d18', borderColor: '#1e3363', borderRadius: '8px', fontSize: '12px' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="cumulative" 
                  name="Total Counted"
                  stroke="#10b981" 
                  strokeWidth={2.5}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Vehicle Class Volume Bar Chart */}
        <div className="p-6 rounded-2xl bg-[#0f1c3a]/60 border border-[#1e3363]/60 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Vehicle Volume by Category
              </h3>
              <p className="text-xs text-slate-400">
                Absolute count distribution across detected classifications
              </p>
            </div>
            <BarChart3 className="w-4 h-4 text-indigo-400" />
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e3363" opacity={0.5} />
                <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#070d18', borderColor: '#1e3363', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="count" name="Count" radius={[6, 6, 0, 0]}>
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Vehicle Composition Ratio */}
        <div className="p-6 rounded-2xl bg-[#0f1c3a]/60 border border-[#1e3363]/60 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-white">
                Vehicle Composition Proportion
              </h3>
              <p className="text-xs text-slate-400">
                Modal share percentage of road traffic
              </p>
            </div>
            <PieIcon className="w-4 h-4 text-cyan-400" />
          </div>

          <div className="h-64 w-full flex items-center justify-center">
            {analysis?.total_vehicles_counted > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="count"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {categoryData.map((entry, index) => (
                      <Cell key={`pie-cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#070d18', borderColor: '#1e3363', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Legend 
                    wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-500">No vehicles recorded in session</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
