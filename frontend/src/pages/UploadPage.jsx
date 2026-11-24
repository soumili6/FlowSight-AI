import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileVideo, 
  Play, 
  Sliders, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  Sparkles,
  Zap
} from 'lucide-react';
import { uploadVideo, startAnalysis, getAnalysisStatus } from '../services/api';

export default function UploadPage({ 
  onAnalysisStarted, 
  onLoadSample, 
  loadingSample 
}) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [stride, setStride] = useState(1);
  const [linePosition, setLinePosition] = useState(0.55);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (file) => {
    setError(null);
    const validExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm'];
    const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    if (!validExtensions.includes(ext)) {
      setError(`Invalid file format. Please upload one of: ${validExtensions.join(', ')}`);
      return;
    }
    setSelectedFile(file);
  };

  const pollAnalysis = (videoId) => {
    const interval = setInterval(async () => {
      try {
        const status = await getAnalysisStatus(videoId);
        setAnalysisProgress(status.progress || 0);
        setStatusMessage(status.message || 'Processing frames with YOLOv8...');
        
        if (status.status === 'completed') {
          clearInterval(interval);
          setAnalyzing(false);
          setStatusMessage('Analysis complete! Transitioning to live monitoring...');
          setTimeout(() => {
            if (onAnalysisStarted) {
              onAnalysisStarted(videoId);
            }
          }, 1000);
        } else if (status.status === 'failed') {
          clearInterval(interval);
          setAnalyzing(false);
          setError(status.message || 'Analysis processing encountered an error');
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 1000);
  };

  const handleUploadAndAnalyze = async () => {
    if (!selectedFile) return;

    setError(null);
    setUploading(true);
    setUploadProgress(0);
    setStatusMessage('Uploading video to FlowSight server...');

    try {
      // 1. Upload video
      const uploadRes = await uploadVideo(selectedFile, (progress) => {
        setUploadProgress(progress);
      });

      const videoId = uploadRes.data.video.id;
      setUploading(false);
      setAnalyzing(true);
      setStatusMessage('Starting AI vehicle detection and ByteTrack tracking...');

      // 2. Start analysis
      await startAnalysis(videoId, {
        sampleStride: stride,
        linePosition: linePosition,
        runAsync: true
      });

      // 3. Poll progress
      pollAnalysis(videoId);

    } catch (err) {
      setUploading(false);
      setAnalyzing(false);
      setError(err.response?.data?.detail || err.message || 'Failed to upload and analyze video');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white tracking-tight sm:text-3xl">
          Ingest Traffic Video for Computer Vision Analysis
        </h2>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Upload real-world highway, intersection, or arterial road footage. FlowSight AI detects vehicles across classes, estimates lane density, and classifies congestion.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start space-x-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-rose-400" />
          <div>
            <span className="font-semibold">Notice: </span>
            {error}
          </div>
        </div>
      )}

      {/* Drag & Drop Upload Zone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 ${
          dragActive
            ? 'border-cyan-400 bg-cyan-950/20 scale-[1.01]'
            : selectedFile
            ? 'border-emerald-500/60 bg-emerald-950/10'
            : 'border-[#1e3363] hover:border-cyan-500/50 bg-[#0f1c3a]/40 hover:bg-[#0f1c3a]/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".mp4,.avi,.mov,.mkv,.webm"
          onChange={handleFileInput}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600/20 to-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/10">
            {selectedFile ? (
              <FileVideo className="w-8 h-8 text-emerald-400" />
            ) : (
              <UploadCloud className="w-8 h-8 text-cyan-400" />
            )}
          </div>

          <div>
            {selectedFile ? (
              <div className="space-y-1">
                <p className="text-base font-semibold text-white">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-slate-400">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Ready for inference
                </p>
              </div>
            ) : (
              <div className="space-y-1">
                <p className="text-base font-semibold text-white">
                  Drag & drop traffic video here, or <span className="text-cyan-400 underline underline-offset-2">browse file</span>
                </p>
                <p className="text-xs text-slate-400">
                  Supports MP4, AVI, MOV, MKV (H.264 / standard codecs)
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Tuning Options */}
      <div className="bg-[#0f1c3a]/70 rounded-2xl border border-[#1e3363]/60 p-6 backdrop-blur-md space-y-6">
        <div className="flex items-center space-x-2 text-sm font-semibold text-white pb-3 border-b border-[#152449]">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <span>Computer Vision & Tracking Tuning Parameters</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Virtual Line Position */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-slate-300">Virtual Counting Line Position:</span>
              <span className="font-mono text-cyan-400 font-semibold">{Math.round(linePosition * 100)}% from top</span>
            </div>
            <input
              type="range"
              min="0.2"
              max="0.8"
              step="0.05"
              value={linePosition}
              onChange={(e) => setLinePosition(parseFloat(e.target.value))}
              disabled={uploading || analyzing}
              className="w-full accent-cyan-400 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <p className="text-[11px] text-slate-400">
              Vehicles crossing this vertical screen boundary trigger unique counter increments.
            </p>
          </div>

          {/* Frame Stride */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-medium text-slate-300">Processing Stride:</span>
              <span className="font-mono text-cyan-400 font-semibold">
                {stride === 1 ? 'Every frame (Max Precision)' : `Every ${stride} frames (High Speed)`}
              </span>
            </div>
            <div className="flex gap-2">
              {[1, 2, 3].map((val) => (
                <button
                  key={val}
                  type="button"
                  onClick={() => setStride(val)}
                  disabled={uploading || analyzing}
                  className={`flex-1 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                    stride === val
                      ? 'bg-blue-600 text-white border-blue-400'
                      : 'bg-[#152449]/50 text-slate-300 border-[#1e3363] hover:bg-[#152449]'
                  }`}
                >
                  {val === 1 ? '1 (Default)' : `${val}x Stride`}
                </button>
              ))}
            </div>
            <p className="text-[11px] text-slate-400">
              Stride 1 inspects all video frames; stride 2 or 3 speeds up processing for long footage.
            </p>
          </div>
        </div>

        {/* Progress Display */}
        {(uploading || analyzing) && (
          <div className="pt-4 border-t border-[#152449] space-y-3">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-cyan-300 flex items-center space-x-1.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                <span>{statusMessage}</span>
              </span>
              <span className="font-mono text-white">
                {uploading ? `${uploadProgress}% Uploaded` : `${Math.round(analysisProgress)}% Processed`}
              </span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div 
                className="bg-gradient-to-r from-blue-500 via-indigo-500 to-cyan-400 h-full rounded-full transition-all duration-300"
                style={{ width: `${uploading ? uploadProgress : analysisProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <button
            onClick={handleUploadAndAnalyze}
            disabled={!selectedFile || uploading || analyzing}
            className="flex-1 inline-flex items-center justify-center space-x-2 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-semibold text-sm shadow-lg shadow-blue-600/30 transition-all hover:scale-[1.01] disabled:opacity-50 disabled:pointer-events-none"
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Uploading Video ({uploadProgress}%)...</span>
              </>
            ) : analyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running YOLO + ByteTrack ({Math.round(analysisProgress)}%)...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 text-cyan-300" />
                <span>Execute FlowSight Analysis</span>
              </>
            )}
          </button>

          <button
            onClick={onLoadSample}
            disabled={uploading || analyzing || loadingSample}
            className="inline-flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-[#152449] hover:bg-[#1e3363] border border-cyan-500/30 text-cyan-300 font-semibold text-sm transition-all hover:scale-[1.01] disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>{loadingSample ? 'Loading Demo Video...' : 'Load Demo Highway Footage'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
