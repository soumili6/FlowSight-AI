from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class VideoBase(BaseModel):
    filename: str
    original_filename: str
    file_size_bytes: int
    fps: float = 0.0
    total_frames: int = 0
    width: int = 0
    height: int = 0
    duration_seconds: float = 0.0
    status: str = "uploaded"
    error_message: Optional[str] = None

class VideoResponse(VideoBase):
    id: str
    file_path: str
    processed_path: Optional[str] = None
    created_at: str
    updated_at: str

class TimelinePoint(BaseModel):
    timestamp_sec: float
    frame_number: int
    active_vehicles: int
    cumulative_count: int
    car_count: int
    motorcycle_count: int
    bus_count: int
    truck_count: int
    density: float
    congestion_level: str

class AnalysisCreate(BaseModel):
    video_id: str
    counting_line_position: Optional[float] = 0.5  # Relative position 0.0 to 1.0 (vertical percentage)
    sample_stride: Optional[int] = 1              # Process every Nth frame for performance

class VehicleCategoryCounts(BaseModel):
    cars: int = 0
    motorcycles: int = 0
    buses: int = 0
    trucks: int = 0
    total: int = 0

class AnalysisResponse(BaseModel):
    id: str
    video_id: str
    video_filename: Optional[str] = None
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
    counting_method: str = "virtual_line"
    status: str = "completed"
    summary_insights: Optional[str] = None
    created_at: str
    timeline: Optional[List[TimelinePoint]] = None
    video: Optional[VideoResponse] = None

class DashboardOverviewStats(BaseModel):
    total_videos_analyzed: int
    total_vehicles_counted: int
    average_system_density: float
    high_congestion_incidents: int
    vehicle_breakdown: Dict[str, int]
    recent_analyses: List[AnalysisResponse]
