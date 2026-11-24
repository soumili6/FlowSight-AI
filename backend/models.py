"""
FlowSight AI - Domain Data Models
Defines core data structures for videos, traffic analyses, and timeline metrics.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class VideoRecord:
    id: str
    filename: str
    original_filename: str
    file_path: str
    file_size_bytes: int
    processed_path: Optional[str] = None
    fps: float = 25.0
    total_frames: int = 0
    width: int = 0
    height: int = 0
    duration_seconds: float = 0.0
    status: str = "uploaded"
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class AnalysisRecord:
    id: str
    video_id: str
    total_vehicles_counted: int = 0
    car_count: int = 0
    motorcycle_count: int = 0
    bus_count: int = 0
    truck_count: int = 0
    peak_density: float = 0.0
    average_density: float = 0.0
    congestion_level: str = "Low"
    congestion_score: float = 0.0
    processing_time_seconds: float = 0.0
    total_frames_analyzed: int = 0
    counting_method: str = "bytetrack_virtual_line"
    status: str = "completed"
    summary_insights: str = ""
    created_at: Optional[datetime] = None

@dataclass
class TimelineRecord:
    analysis_id: str
    timestamp_sec: float
    frame_number: int
    active_vehicles: int = 0
    cumulative_count: int = 0
    car_count: int = 0
    motorcycle_count: int = 0
    bus_count: int = 0
    truck_count: int = 0
    density: float = 0.0
    congestion_level: str = "Low"
