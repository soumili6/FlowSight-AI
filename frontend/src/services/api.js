import axios from 'axios';

const api = axios.create({
  baseURL: 'https://flowsight-ai-backend.onrender.com/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Videos
export const uploadVideo = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/videos/upload', formData, {
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percent);
      }
    },
  });
};

export const loadSampleVideo = async () => {
  const res = await api.post('/videos/load-sample');
  return res.data;
};

export const getVideos = async () => {
  const res = await api.get('/videos');
  return res.data;
};

export const getVideoById = async (id) => {
  const res = await api.get(`/videos/${id}`);
  return res.data;
};

export const deleteVideo = async (id) => {
  const res = await api.delete(`/videos/${id}`);
  return res.data;
};

// Analysis
export const startAnalysis = async (videoId, options = {}) => {
  const res = await api.post('/analysis/start', {
    video_id: videoId,
    sample_stride: options.sampleStride || 1,
    line_position: options.linePosition || 0.55,
    run_async: options.runAsync !== false,
  });
  return res.data;
};

export const getAnalysisStatus = async (videoId) => {
  const res = await api.get(`/analysis/status/${videoId}`);
  return res.data;
};

export const getAnalysis = async (analysisId) => {
  const res = await api.get(`/analysis/${analysisId}`);
  return res.data;
};

export const getLatestAnalysis = async (videoId) => {
  const res = await api.get(`/analysis/by-video/${videoId}`);
  return res.data;
};

// History
export const getHistory = async () => {
  const res = await api.get('/history');
  return res.data;
};

export const deleteHistory = async (id) => {
  const res = await api.delete(`/history/${id}`);
  return res.data;
};

// Dashboard Stats
export const getDashboardStats = async () => {
  const res = await api.get('/stats/dashboard');
  return res.data;
};

// Health
export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export default api;
