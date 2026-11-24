import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import OverviewPage from './pages/OverviewPage';
import UploadPage from './pages/UploadPage';
import MonitoringPage from './pages/MonitoringPage';
import AnalyticsPage from './pages/AnalyticsPage';
import HistoryPage from './pages/HistoryPage';
import { 
  getDashboardStats, 
  getHealth, 
  loadSampleVideo, 
  startAnalysis 
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedVideoId, setSelectedVideoId] = useState(null);
  const [selectedAnalysisId, setSelectedAnalysisId] = useState(null);
  const [stats, setStats] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    setIsRefreshing(true);
    try {
      const [statsRes, healthRes] = await Promise.allSettled([
        getDashboardStats(),
        getHealth(),
      ]);
      if (statsRes.status === 'fulfilled') setStats(statsRes.value);
      if (healthRes.status === 'fulfilled') setSystemHealth(healthRes.value);
    } catch (err) {
      console.error('Failed to load initial data:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSelectVideo = (videoId, analysisId, targetTab = 'monitoring') => {
    setSelectedVideoId(videoId);
    setSelectedAnalysisId(analysisId);
    setActiveTab(targetTab);
  };

  const handleAnalysisStarted = (videoId) => {
    setSelectedVideoId(videoId);
    setSelectedAnalysisId(null);
    setActiveTab('monitoring');
    fetchInitialData();
  };

  const handleLoadSample = async () => {
    setLoadingSample(true);
    try {
      // 1. Generate / load sample video in backend
      const res = await loadSampleVideo();
      const video = res.video;
      setSelectedVideoId(video.id);

      // 2. Start analysis asynchronously (never use runAsync:false — it blocks
      //    the server event loop inside the HTTP request and causes OpenCV C++ exceptions)
      await startAnalysis(video.id, {
        sampleStride: 2,        // stride=2: process every other frame → 2× faster
        linePosition: 0.55,
        runAsync: true          // always background; poll for completion below
      });

      // 3. Navigate to monitoring immediately — the page polls /analysis/status itself
      await fetchInitialData();
      setActiveTab('monitoring');
    } catch (err) {
      console.error('Failed to load sample video:', err);
      alert('Error loading demo video: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoadingSample(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#070d18] text-slate-100">
      {/* Sidebar Navigation */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        systemHealth={systemHealth} 
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar 
          activeTab={activeTab} 
          onRefresh={fetchInitialData} 
          isRefreshing={isRefreshing} 
        />

        <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">
          {activeTab === 'overview' && (
            <OverviewPage
              stats={stats}
              onSelectVideo={handleSelectVideo}
              setActiveTab={setActiveTab}
              onLoadSample={handleLoadSample}
              loadingSample={loadingSample}
            />
          )}

          {activeTab === 'upload' && (
            <UploadPage
              onAnalysisStarted={handleAnalysisStarted}
              onLoadSample={handleLoadSample}
              loadingSample={loadingSample}
            />
          )}

          {activeTab === 'monitoring' && (
            <MonitoringPage
              selectedVideoId={selectedVideoId}
              selectedAnalysisId={selectedAnalysisId}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsPage
              selectedAnalysisId={selectedAnalysisId}
              selectedVideoId={selectedVideoId}
              setActiveTab={setActiveTab}
            />
          )}

          {activeTab === 'history' && (
            <HistoryPage
              onSelectVideo={handleSelectVideo}
              setActiveTab={setActiveTab}
            />
          )}
        </main>
      </div>
    </div>
  );
}
