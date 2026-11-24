import uuid
import json
from typing import Optional, List, Dict, Any
from backend.database import get_db

def create_video(video_data: dict) -> dict:
    video_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO videos (
                id, filename, original_filename, file_path, processed_path,
                file_size_bytes, fps, total_frames, width, height, duration_seconds,
                status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id,
            video_data["filename"],
            video_data["original_filename"],
            video_data["file_path"],
            video_data.get("processed_path"),
            video_data["file_size_bytes"],
            video_data.get("fps", 0),
            video_data.get("total_frames", 0),
            video_data.get("width", 0),
            video_data.get("height", 0),
            video_data.get("duration_seconds", 0),
            video_data.get("status", "uploaded"),
            video_data.get("error_message")
        ))
    return get_video(video_id)

def get_video(video_id: str) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        return cursor.fetchone()

def list_videos(limit: int = 50) -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM videos ORDER BY created_at DESC LIMIT ?", (limit,))
        return cursor.fetchall()

def update_video_status(video_id: str, status: str, processed_path: Optional[str] = None, error_message: Optional[str] = None):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE videos
            SET status = ?, processed_path = COALESCE(?, processed_path),
                error_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, processed_path, error_message, video_id))

def create_analysis(analysis_data: dict, timeline_points: List[dict] = None) -> dict:
    analysis_id = str(uuid.uuid4())
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analyses (
                id, video_id, total_vehicles_counted, car_count, motorcycle_count,
                bus_count, truck_count, peak_density, average_density,
                congestion_level, congestion_score, processing_time_seconds,
                total_frames_analyzed, counting_method, status, summary_insights
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            analysis_data["video_id"],
            analysis_data.get("total_vehicles_counted", 0),
            analysis_data.get("car_count", 0),
            analysis_data.get("motorcycle_count", 0),
            analysis_data.get("bus_count", 0),
            analysis_data.get("truck_count", 0),
            analysis_data.get("peak_density", 0.0),
            analysis_data.get("average_density", 0.0),
            analysis_data.get("congestion_level", "Low"),
            analysis_data.get("congestion_score", 0.0),
            analysis_data.get("processing_time_seconds", 0.0),
            analysis_data.get("total_frames_analyzed", 0),
            analysis_data.get("counting_method", "virtual_line"),
            analysis_data.get("status", "completed"),
            analysis_data.get("summary_insights", "")
        ))

        if timeline_points:
            cursor.executemany("""
                INSERT INTO analysis_timeline (
                    analysis_id, timestamp_sec, frame_number, active_vehicles,
                    cumulative_count, car_count, motorcycle_count, bus_count,
                    truck_count, density, congestion_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    analysis_id,
                    tp["timestamp_sec"],
                    tp["frame_number"],
                    tp.get("active_vehicles", 0),
                    tp.get("cumulative_count", 0),
                    tp.get("car_count", 0),
                    tp.get("motorcycle_count", 0),
                    tp.get("bus_count", 0),
                    tp.get("truck_count", 0),
                    tp.get("density", 0.0),
                    tp.get("congestion_level", "Low")
                )
                for tp in timeline_points
            ])

    return get_analysis(analysis_id, include_timeline=True)

def get_analysis(analysis_id: str, include_timeline: bool = True) -> Optional[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, v.original_filename as video_filename, v.file_path as video_file_path,
                   v.processed_path as video_processed_path, v.duration_seconds as video_duration,
                   v.fps as video_fps
            FROM analyses a
            LEFT JOIN videos v ON a.video_id = v.id
            WHERE a.id = ?
        """, (analysis_id,))
        analysis = cursor.fetchone()
        if not analysis:
            return None

        if include_timeline:
            cursor.execute("""
                SELECT timestamp_sec, frame_number, active_vehicles, cumulative_count,
                       car_count, motorcycle_count, bus_count, truck_count, density, congestion_level
                FROM analysis_timeline
                WHERE analysis_id = ?
                ORDER BY frame_number ASC
            """, (analysis_id,))
            analysis["timeline"] = cursor.fetchall()
        else:
            analysis["timeline"] = []

        return analysis

def list_analyses(limit: int = 50) -> List[dict]:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, v.original_filename as video_filename, v.file_path as video_file_path,
                   v.processed_path as video_processed_path, v.duration_seconds as video_duration
            FROM analyses a
            LEFT JOIN videos v ON a.video_id = v.id
            ORDER BY a.created_at DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

def get_dashboard_stats() -> dict:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total_videos FROM videos WHERE status = 'completed'")
        total_videos = cursor.fetchone()["total_videos"]

        cursor.execute("""
            SELECT 
                COALESCE(SUM(total_vehicles_counted), 0) as total_vehicles,
                COALESCE(SUM(car_count), 0) as total_cars,
                COALESCE(SUM(motorcycle_count), 0) as total_motorcycles,
                COALESCE(SUM(bus_count), 0) as total_buses,
                COALESCE(SUM(truck_count), 0) as total_trucks,
                COALESCE(AVG(average_density), 0.0) as avg_density,
                COALESCE(SUM(CASE WHEN congestion_level = 'High' THEN 1 ELSE 0 END), 0) as high_congestion_count
            FROM analyses
            WHERE status = 'completed'
        """)
        agg = cursor.fetchone()

        cursor.execute("""
            SELECT a.*, v.original_filename as video_filename
            FROM analyses a
            LEFT JOIN videos v ON a.video_id = v.id
            ORDER BY a.created_at DESC
            LIMIT 5
        """)
        recent = cursor.fetchall()

        return {
            "total_videos_analyzed": total_videos,
            "total_vehicles_counted": agg["total_vehicles"],
            "average_system_density": round(agg["avg_density"], 2),
            "high_congestion_incidents": agg["high_congestion_count"],
            "vehicle_breakdown": {
                "cars": agg["total_cars"],
                "motorcycles": agg["total_motorcycles"],
                "buses": agg["total_buses"],
                "trucks": agg["total_trucks"]
            },
            "recent_analyses": recent
        }

def delete_analysis(analysis_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        return cursor.rowcount > 0

def delete_video(video_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        return cursor.rowcount > 0
