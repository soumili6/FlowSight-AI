import React, { useState, useEffect, useRef } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  Video,
  Eye,
  Layers,
  Activity,
  Car,
  Bike,
  Bus,
  Truck,
  Gauge,
  BarChart2,
  Clock,
  FileText,
  Loader2
} from 'lucide-react';
import { getAnalysis, getLatestAnalysis, getAnalysisStatus } from '../services/api';

export default function MonitoringPage({
  selectedVideoId,
  selectedAnalysisId,
  setActiveTab
}) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null); // null | 'processing' | 'completed' | 'failed'
  const [processingProgress, setProcessingProgress] = useState(0);
  const [processingMessage, setProcessingMessage] = useState('');
  const [viewMode, setViewMode] = useState('annotated'); // 'annotated' or 'original'
  const [videoError, setVideoError] = useState(null);
  const videoRef = useRef(null);
  const pollRef = useRef(null);

  // Clear any active poll when the component unmounts or video changes
  const clearPoll = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  useEffect(() => {
    clearPoll();
    fetchAnalysisData();
    return () => clearPoll();
  }, [selectedVideoId, selectedAnalysisId]);

  const fetchAnalysisData = async () => {
    if (!selectedAnalysisId && !selectedVideoId) return;

    setLoading(true);
    try {
      if (selectedAnalysisId) {
        const res = await getAnalysis(selectedAnalysisId);
        setAnalysis(res.analysis);
        setProcessingStatus('completed');
      } else if (selectedVideoId) {
        // Try fetching analysis; if none yet, start polling the job status
        try {
          const res = await getLatestAnalysis(selectedVideoId);
          setAnalysis(res.analysis);
          setProcessingStatus('completed');
        } catch {
          // No analysis yet — start polling the job status
          startPolling(selectedVideoId);
        }
      }
    } catch (err) {
      console.error('Failed to load analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const startPolling = (videoId) => {
    setProcessingStatus('processing');
    setProcessingProgress(0);
    setProcessingMessage('Analysis running in background...');

    pollRef.current = setInterval(async () => {
      try {
        const status = await getAnalysisStatus(videoId);
        setProcessingProgress(status.progress || 0);
        setProcessingMessage(status.message || 'Processing frames with YOLOv8...');

        if (status.status === 'completed') {
          clearPoll();
          // Fetch the completed analysis
          try {
            const res = await getLatestAnalysis(videoId);
            setAnalysis(res.analysis);
            setProcessingStatus('completed');
          } catch (e) {
            console.error('Analysis complete but fetch failed:', e);
          }
        } else if (status.status === 'failed') {
          clearPoll();
          setProcessingStatus('failed');
          setProcessingMessage(status.message || 'Analysis failed');
        }
      } catch (err) {
        console.error('Status poll error:', err);
      }
    }, 2000); // poll every 2 seconds
  };

  if (!selectedVideoId && !selectedAnalysisId && !analysis) {
    return (
      <div className="text-center py-20 px-4 max-w-md mx-auto">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-cyan-400 mb-4">
          <Video className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-white">No Video Selected For Monitoring</h3>
        <p className="text-xs text-slate-400 mt-2 mb-6">
          Upload a traffic video or select an existing session from the Overview or History page to view annotated video tracking and live telemetry.
        </p>
        <button
          onClick={() => setActiveTab('upload')}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-600/30"
        >
          Go to Video Ingestion
        </button>
      </div>
    );
  }

  const processedPath = analysis?.video_processed_path || analysis?.video?.processed_path;
  const originalPath = analysis?.video_file_path || analysis?.video?.file_path;

  // Extract filenames for media URL
  const processedFilename = processedPath ? processedPath.split(/[/\\]/).pop() : null;
  const originalFilename = originalPath ? originalPath.split(/[/\\]/).pop() : null;

  const currentVideoSrc = viewMode === 'annotated' && processedFilename
    ? `/media/processed/${processedFilename}`
    : originalFilename
      ? `/media/uploads/${originalFilename}`
      : null;

  const congestionBadgeColor =
    analysis?.congestion_level === 'High'
      ? 'bg-rose-500/20 text-rose-300 border-rose-500/30'
      : analysis?.congestion_level === 'Medium'
        ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
        : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';

  return (
    <div className="space-y-6 pb-12">
      {/* Top Bar / Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60 backdrop-blur-md">
        <div>
          <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center space-x-1.5">
            <Activity className="w-3.5 h-3.5" />
            <span>Active Vision Stream</span>
          </span>
          <h2 className="text-lg font-bold text-white">
            {analysis?.video_filename || 'Traffic Monitoring Stream'}
          </h2>
        </div>

        <div className="flex items-center space-x-3">
          {/* Switch View Toggle */}
          <div className="inline-flex rounded-lg p-1 bg-[#0b1329] border border-[#1e3363]">
            <button
              onClick={() => setViewMode('annotated')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition-all ${viewMode === 'annotated'
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-white'
                }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Annotated AI View</span>
            </button>
            <button
              onClick={() => setViewMode('original')}
              className={`px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition-all ${viewMode === 'original'
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-white'
                }`}
            >
              <Video className="w-3.5 h-3.5" />
              <span>Raw Camera View</span>
            </button>
          </div>

          <button
            onClick={() => setActiveTab('analytics')}
            className="px-3.5 py-1.5 rounded-lg bg-[#152449] hover:bg-[#1e3363] border border-[#1e3363] text-xs font-semibold text-cyan-300 flex items-center space-x-1.5 transition-colors"
          >
            <BarChart2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>View Full Analytics</span>
          </button>
        </div>
      </div>

      {/* Main Monitoring Video Player */}
      <div className="relative rounded-2xl overflow-hidden bg-black border border-[#1e3363] shadow-2xl">
        {currentVideoSrc ? (
          <div className="relative w-full">
            <video
              ref={videoRef}
              key={currentVideoSrc}
              controls
              autoPlay
              loop
              muted
              playsInline
              preload="auto"
              className="w-full max-h-[540px] object-contain mx-auto bg-black"
              onError={(e) => {
                const err = e.currentTarget.error;
                const errMsg = err ? `Code ${err.code}: ${err.message || 'Media decode/playback error'}` : 'Video load failed';
                console.error("Video playback error:", errMsg);
                setVideoError(errMsg);
              }}
              onLoadedData={() => setVideoError(null)}
            >
              <source src={currentVideoSrc} type="video/mp4" />
              Your browser does not support HTML5 video playback.
            </video>

            {videoError && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/85 p-6 text-center space-y-3 z-10">
                <p className="text-sm font-semibold text-rose-400">Video Playback Notice</p>
                <p className="text-xs text-slate-300 max-w-md">{videoError}</p>
                <button
                  onClick={() => {
                    setVideoError(null);
                    if (videoRef.current) {
                      videoRef.current.load();
                      videoRef.current.play().catch(() => {});
                    }
                  }}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium flex items-center space-x-1.5 shadow"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Retry Playback</span>
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="h-80 flex flex-col items-center justify-center text-slate-500">
            <Video className="w-12 h-12 mb-2 opacity-50" />
            <p className="text-sm font-medium">Video rendering in progress...</p>
          </div>
        )}

        {/* Live HUD Banner Overlay on top */}
        <div className="absolute top-3 left-3 right-3 pointer-events-none flex flex-wrap justify-between items-center gap-2">
          <div className="px-3 py-1.5 rounded-lg bg-[#070d18]/80 backdrop-blur-md border border-[#1e3363]/80 text-xs font-mono text-cyan-400 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-semibold">FlowSight AI • {viewMode.toUpperCase()} STREAM</span>
          </div>

          <div className="flex items-center space-x-2">
            <div className={`px-3 py-1.5 rounded-lg backdrop-blur-md border text-xs font-semibold ${congestionBadgeColor}`}>
              Traffic Congestion: {analysis?.congestion_level || 'Normal'}
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Telemetry Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400 font-medium">Total Vehicles Passed</span>
          <div className="text-2xl font-extrabold text-white mt-1">
            {analysis?.total_vehicles_counted || 0}
          </div>
          <span className="text-[11px] text-cyan-400">ByteTrack Track IDs</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400 font-medium">Peak Density</span>
          <div className="text-2xl font-extrabold text-white mt-1">
            {analysis?.peak_density || 0}
          </div>
          <span className="text-[11px] text-slate-400">Max vehicles per frame</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400 font-medium">Average Density</span>
          <div className="text-2xl font-extrabold text-white mt-1">
            {analysis?.average_density || 0}
          </div>
          <span className="text-[11px] text-slate-400">Vehicles / frame</span>
        </div>

        <div className="p-4 rounded-xl bg-[#0f1c3a]/70 border border-[#1e3363]/60">
          <span className="text-xs text-slate-400 font-medium">Congestion Score</span>
          <div className="text-2xl font-extrabold text-white mt-1">
            {analysis?.congestion_score || 0}%
          </div>
          <span className="text-[11px] text-amber-400">Flow saturation index</span>
        </div>
      </div>

      {/* Vehicle Category Counters */}
      <div className="p-5 rounded-xl bg-[#0f1c3a]/60 border border-[#1e3363]/50">
        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Category Volume Breakdown
        </h4>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg bg-[#0b1329]/80 border border-emerald-500/20 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Car className="w-4 h-4 text-emerald-400" />
              <span className="text-xs text-slate-300 font-medium">Cars</span>
            </div>
            <span className="text-base font-bold text-white font-mono">{analysis?.car_count || 0}</span>
          </div>

          <div className="p-3 rounded-lg bg-[#0b1329]/80 border border-amber-500/20 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bike className="w-4 h-4 text-amber-400" />
              <span className="text-xs text-slate-300 font-medium">Motorcycles</span>
            </div>
            <span className="text-base font-bold text-white font-mono">{analysis?.motorcycle_count || 0}</span>
          </div>

          <div className="p-3 rounded-lg bg-[#0b1329]/80 border border-cyan-500/20 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bus className="w-4 h-4 text-cyan-400" />
              <span className="text-xs text-slate-300 font-medium">Buses</span>
            </div>
            <span className="text-base font-bold text-white font-mono">{analysis?.bus_count || 0}</span>
          </div>

          <div className="p-3 rounded-lg bg-[#0b1329]/80 border border-purple-500/20 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Truck className="w-4 h-4 text-purple-400" />
              <span className="text-xs text-slate-300 font-medium">Trucks</span>
            </div>
            <span className="text-base font-bold text-white font-mono">{analysis?.truck_count || 0}</span>
          </div>
        </div>
      </div>

      {/* AI Narrative Insights */}
      {analysis?.summary_insights && (
        <div className="p-5 rounded-xl bg-gradient-to-r from-blue-900/30 to-slate-900/40 border border-blue-500/20 flex items-start space-x-3">
          <FileText className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
          <div>
            <h5 className="text-xs font-semibold text-cyan-300 uppercase tracking-wider">
              AI Vision Executive Summary
            </h5>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              {analysis.summary_insights}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
