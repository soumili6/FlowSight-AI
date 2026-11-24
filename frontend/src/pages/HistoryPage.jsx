import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  Trash2, 
  Video, 
  BarChart2, 
  Eye, 
  Calendar, 
  Clock, 
  Layers 
} from 'lucide-react';
import { getHistory, deleteHistory } from '../services/api';

export default function HistoryPage({ onSelectVideo, setActiveTab }) {
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState('');
  const [filterLevel, setFilterLevel] = useState('ALL');
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await getHistory();
      setHistory(res.analyses || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this analysis session?')) {
      return;
    }
    setDeletingId(id);
    try {
      await deleteHistory(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Failed to delete history item:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const filteredHistory = history.filter((item) => {
    const matchesSearch = 
      (item.video_filename || '').toLowerCase().includes(search.toLowerCase()) ||
      (item.id || '').toLowerCase().includes(search.toLowerCase());
    const matchesLevel = 
      filterLevel === 'ALL' || item.congestion_level?.toUpperCase() === filterLevel;
    return matchesSearch && matchesLevel;
  });

  return (
    <div className="space-y-6 pb-12">
      {/* Header & Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-2xl bg-[#0f1c3a]/70 border border-[#1e3363]/60 backdrop-blur-md">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <History className="w-5 h-5 text-cyan-400" />
            <span>Traffic Analysis History Archive</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Complete database audit log of processed video sessions and historical density analytics
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by video filename..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-[#0b1329] border border-[#1e3363] text-xs text-slate-200 rounded-lg pl-8 pr-3 py-2 outline-none focus:border-cyan-400 w-48 sm:w-60"
            />
          </div>

          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="bg-[#0b1329] border border-[#1e3363] text-xs text-slate-200 rounded-lg px-3 py-2 outline-none focus:border-cyan-400"
          >
            <option value="ALL">All Congestion Levels</option>
            <option value="LOW">Low Congestion</option>
            <option value="MEDIUM">Medium Congestion</option>
            <option value="HIGH">High Congestion</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-[#0f1c3a]/60 rounded-2xl border border-[#152449] overflow-hidden backdrop-blur-md">
        {filteredHistory.length === 0 ? (
          <div className="text-center py-16 px-4">
            <div className="w-12 h-12 mx-auto rounded-full bg-blue-500/10 flex items-center justify-center mb-3 text-cyan-400">
              <History className="w-6 h-6" />
            </div>
            <h4 className="text-base font-semibold text-white">No Analysis Records Found</h4>
            <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1 mb-5">
              {search || filterLevel !== 'ALL'
                ? 'No historical logs match your current filter criteria.'
                : 'Processed traffic videos and calculated densities will automatically be recorded here in SQLite.'}
            </p>
            <button
              onClick={() => setActiveTab('upload')}
              className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20"
            >
              Analyze New Video
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#1e3363] bg-[#0b1329]/50 text-slate-400 uppercase tracking-wider">
                  <th className="py-3.5 px-4 font-semibold">Video Session</th>
                  <th className="py-3.5 px-4 font-semibold">Date & Time</th>
                  <th className="py-3.5 px-4 font-semibold">Total Vehicles</th>
                  <th className="py-3.5 px-4 font-semibold">Category Breakdown</th>
                  <th className="py-3.5 px-4 font-semibold">Avg Density</th>
                  <th className="py-3.5 px-4 font-semibold">Congestion</th>
                  <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#152449]/40">
                {filteredHistory.map((item) => (
                  <tr key={item.id} className="hover:bg-[#152449]/30 transition-colors">
                    <td className="py-4 px-4 font-medium text-slate-200">
                      <div className="flex items-center space-x-2">
                        <Video className="w-4 h-4 text-cyan-400 shrink-0" />
                        <span className="truncate max-w-[200px]" title={item.video_filename}>
                          {item.video_filename || 'Video'}
                        </span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-400">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-4 px-4 font-bold text-white text-sm">
                      {item.total_vehicles_counted}
                    </td>
                    <td className="py-4 px-4 text-slate-300">
                      <div className="flex items-center space-x-1.5 font-mono text-[11px]">
                        <span className="text-emerald-400" title="Cars">C:{item.car_count}</span>
                        <span>•</span>
                        <span className="text-amber-400" title="Motorcycles">M:{item.motorcycle_count}</span>
                        <span>•</span>
                        <span className="text-cyan-400" title="Buses">B:{item.bus_count}</span>
                        <span>•</span>
                        <span className="text-purple-400" title="Trucks">T:{item.truck_count}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 font-mono text-slate-200">
                      {item.average_density} / frame
                    </td>
                    <td className="py-4 px-4">
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
                    <td className="py-4 px-4 text-right space-x-2">
                      <button
                        onClick={() => onSelectVideo(item.video_id, item.id, 'monitoring')}
                        className="p-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600/40 text-cyan-300 border border-cyan-500/20"
                        title="View Video Monitoring Stream"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => onSelectVideo(item.video_id, item.id, 'analytics')}
                        className="p-1.5 rounded-lg bg-[#1e3363]/50 hover:bg-[#1e3363] text-slate-200"
                        title="View Recharts Traffic Analytics"
                      >
                        <BarChart2 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => handleDelete(item.id)}
                        disabled={deletingId === item.id}
                        className="p-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/30 text-rose-400 border border-rose-500/20 disabled:opacity-50"
                        title="Delete record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
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
