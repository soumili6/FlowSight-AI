import cv2
import time
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import numpy as np

from backend.config import (
    UPLOAD_DIR,
    PROCESSED_DIR,
    VEHICLE_CLASS_IDS
)
from backend.tracker import TrafficTracker
from backend import crud

logger = logging.getLogger(__name__)

# In-memory progress tracking for asynchronous or background jobs
# {video_id: {"progress": float, "status": str, "message": str, "frame": int, "total_frames": int}}
processing_jobs: Dict[str, Dict[str, Any]] = {}

def create_browser_video_writer(output_path: str, fps: float, width: int, height: int):
    """
    Creates an OpenCV VideoWriter configured with browser-compatible H.264 (avc1).
    On Windows, uses cv2.CAP_MSMF with H264 for native browser playback without external DLL dependencies.
    Falls back gracefully to alternative backends/codecs.
    """
    # 1. On Windows, use MSMF backend - produces native H.264 MP4 (avc1) supported by Chrome and Edge
    if os.name == 'nt' and hasattr(cv2, 'CAP_MSMF'):
        for tag in ['H264', 'avc1']:
            try:
                fourcc = cv2.VideoWriter_fourcc(*tag)
                writer = cv2.VideoWriter(output_path, cv2.CAP_MSMF, fourcc, fps, (width, height))
                if writer.isOpened():
                    logger.info(f"Initialized MSMF VideoWriter with codec '{tag}' for {output_path}")
                    return writer
            except Exception as e:
                logger.warning(f"MSMF codec '{tag}' failed: {e}")

    # 2. Try standard VideoWriter with avc1 / H264
    for tag in ['avc1', 'H264']:
        try:
            fourcc = cv2.VideoWriter_fourcc(*tag)
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if writer.isOpened():
                logger.info(f"Initialized VideoWriter with codec '{tag}' for {output_path}")
                return writer
        except Exception as e:
            logger.warning(f"Codec '{tag}' failed: {e}")

    # 3. Default fallback
    logger.warning(f"H.264 codecs failed; falling back to mp4v for {output_path}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    return cv2.VideoWriter(output_path, fourcc, fps, (width, height))

def get_job_progress(video_id: str) -> Dict[str, Any]:
    return processing_jobs.get(video_id, {"status": "not_found", "progress": 0})

def update_job_progress(video_id: str, progress: float, status: str, message: str, frame: int = 0, total_frames: int = 0):
    processing_jobs[video_id] = {
        "video_id": video_id,
        "progress": round(progress, 1),
        "status": status,
        "message": message,
        "frame": frame,
        "total_frames": total_frames,
        "updated_at": time.time()
    }

def process_video_pipeline(
    video_id: str,
    stride: int = 1,
    line_position: float = 0.55,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Dict[str, Any]:
    """
    Main processing pipeline:
    1. Reads uploaded video.
    2. Runs YOLO + ByteTrack frame-by-frame.
    3. Writes annotated video.
    4. Records time series timeline and overall analytics into SQLite.
    """
    start_time = time.time()
    video_record = crud.get_video(video_id)
    if not video_record:
        raise ValueError(f"Video {video_id} not found in database.")

    input_path = video_record["file_path"]
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Video file not found at: {input_path}")

    update_job_progress(video_id, 0.0, "processing", "Opening video file...")
    crud.update_video_status(video_id, "processing")

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        err = f"Failed to open video file: {input_path}"
        update_job_progress(video_id, 0.0, "failed", err)
        crud.update_video_status(video_id, "failed", error_message=err)
        raise RuntimeError(err)

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = total_frames / fps if fps > 0 else 0

    # Output video path
    processed_filename = f"{video_id}_processed.mp4"
    processed_path = str(PROCESSED_DIR / processed_filename)

    # Initialize browser-compatible H.264 writer
    out = create_browser_video_writer(processed_path, fps / stride, width, height)

    tracker = TrafficTracker()
    tracker.reset()

    timeline_points = []
    densities = []
    congestion_scores = []
    
    frame_idx = 0
    processed_frame_count = 0

    update_job_progress(video_id, 5.0, "processing", "Initializing AI vehicle tracking...", 0, total_frames)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Frame skipping according to stride
            if frame_idx % stride != 0:
                frame_idx += 1
                continue

            # Process frame through tracker
            annotated_frame, metrics = tracker.process_frame(
                frame=frame,
                frame_idx=frame_idx,
                line_ratio=line_position,
                draw_annotations=True
            )

            # Write annotated frame to output video
            # Prepare frame before writing to output video
            if annotated_frame is not None:
                # Ensure frame has the expected dimensions
                if annotated_frame.shape[1] != width or annotated_frame.shape[0] != height:
                    annotated_frame = cv2.resize(
                        annotated_frame,
                        (width, height),
                        interpolation=cv2.INTER_LINEAR
                    )

                # Ensure frame is in 3-channel BGR format
                if len(annotated_frame.shape) == 2:
                    annotated_frame = cv2.cvtColor(
                        annotated_frame,
                        cv2.COLOR_GRAY2BGR
                    )
                elif annotated_frame.shape[2] == 4:
                    annotated_frame = cv2.cvtColor(
                        annotated_frame,
                        cv2.COLOR_BGRA2BGR
                    )

                # Ensure frame is uint8, 3-channel BGR, and contiguous
                annotated_frame = np.asarray(annotated_frame)

                if annotated_frame.dtype != np.uint8:
                    annotated_frame = np.clip(annotated_frame, 0, 255).astype(np.uint8)

                if annotated_frame.ndim == 2:
                    annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_GRAY2BGR)
                elif annotated_frame.shape[2] == 4:
                    annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGRA2BGR)

                annotated_frame = np.ascontiguousarray(annotated_frame)

                out.write(annotated_frame)
            processed_frame_count += 1

            # Accumulate metrics
            densities.append(metrics["density"])
            congestion_scores.append(metrics["congestion_score"])

            # Sample timeline points approximately once per second or every few frames
            sample_interval = max(1, int(fps / stride))
            if processed_frame_count % sample_interval == 0 or frame_idx == total_frames - 1:
                timestamp = frame_idx / fps if fps > 0 else 0.0
                timeline_points.append({
                    "timestamp_sec": round(timestamp, 2),
                    "frame_number": frame_idx,
                    "active_vehicles": metrics["active_vehicles"],
                    "cumulative_count": metrics["cumulative_count"],
                    "car_count": metrics["category_counts"]["car"],
                    "motorcycle_count": metrics["category_counts"]["motorcycle"],
                    "bus_count": metrics["category_counts"]["bus"],
                    "truck_count": metrics["category_counts"]["truck"],
                    "density": metrics["density"],
                    "congestion_level": metrics["congestion_level"]
                })

            # Update progress
            progress_pct = min(95.0, (frame_idx / total_frames) * 90.0 + 5.0)
            if processed_frame_count % 10 == 0:
                msg = f"Analyzing frame {frame_idx}/{total_frames} ({metrics['cumulative_count']} vehicles counted)"
                update_job_progress(video_id, progress_pct, "processing", msg, frame_idx, total_frames)
                if progress_callback:
                    progress_callback(progress_pct, msg)

            frame_idx += 1

    except Exception as e:
        logger.exception("Error during video analysis processing")
        update_job_progress(video_id, 0.0, "failed", str(e))
        crud.update_video_status(video_id, "failed", error_message=str(e))
        raise
    finally:
        cap.release()
        out.release()

    total_processing_time = round(time.time() - start_time, 2)
    avg_density = round(float(np.mean(densities)), 2) if densities else 0.0
    peak_density = round(float(np.max(densities)), 2) if densities else 0.0
    avg_congestion_score = round(float(np.mean(congestion_scores)), 1) if congestion_scores else 0.0

    # Determine overall congestion classification
    if avg_congestion_score >= 65.0 or avg_density >= 10.0:
        overall_congestion = "High"
    elif avg_congestion_score >= 35.0 or avg_density >= 4.0:
        overall_congestion = "Medium"
    else:
        overall_congestion = "Low"

    # Total vehicles counted across categories
    cat_counts = tracker.category_counts
    # Use the final cumulative_count from the tracker's counted_ids set.
    # Avoid calling process_frame again here (it re-runs inference on a stale frame).
    total_counted = max(len(tracker.counted_ids), sum(cat_counts.values()))

    # Fallback to unique track IDs if line crossing was lower than observed vehicles
    if len(tracker.counted_ids) > total_counted:
        total_counted = len(tracker.counted_ids)
    if sum(cat_counts.values()) == 0 and total_counted > 0:
        cat_counts["car"] = total_counted

    # Automated intelligent traffic insights narrative
    insights = (
        f"FlowSight AI analyzed {total_frames} frames ({duration_sec:.1f}s footage) in {total_processing_time}s. "
        f"Detected {total_counted} vehicles total with breakdown: {cat_counts['car']} Cars, "
        f"{cat_counts['motorcycle']} Motorcycles, {cat_counts['bus']} Buses, and {cat_counts['truck']} Trucks. "
        f"Average traffic density was {avg_density:.1f} vehicles/frame (Peak: {peak_density:.1f}), "
        f"yielding an overall congestion level of {overall_congestion} (Congestion Index: {avg_congestion_score}%)."
    )

    analysis_data = {
        "video_id": video_id,
        "total_vehicles_counted": total_counted,
        "car_count": cat_counts["car"],
        "motorcycle_count": cat_counts["motorcycle"],
        "bus_count": cat_counts["bus"],
        "truck_count": cat_counts["truck"],
        "peak_density": peak_density,
        "average_density": avg_density,
        "congestion_level": overall_congestion,
        "congestion_score": avg_congestion_score,
        "processing_time_seconds": total_processing_time,
        "total_frames_analyzed": processed_frame_count,
        "counting_method": "bytetrack_virtual_line",
        "status": "completed",
        "summary_insights": insights
    }

    # Save to SQLite
    analysis_record = crud.create_analysis(analysis_data, timeline_points)
    crud.update_video_status(video_id, "completed", processed_path=processed_path)

    update_job_progress(video_id, 100.0, "completed", "Traffic analysis complete!", total_frames, total_frames)

    return analysis_record
