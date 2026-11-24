import os
import shutil
import uuid
import cv2
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List

from backend.config import UPLOAD_DIR
from backend import crud
from backend.sample_generator import generate_sample_traffic_video

router = APIRouter(prefix="/videos", tags=["Videos"])

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

def extract_video_metadata(file_path: str) -> dict:
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        return {
            "fps": 25.0,
            "total_frames": 0,
            "width": 0,
            "height": 0,
            "duration_seconds": 0.0
        }
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 0
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 0
    duration = total_frames / fps if fps > 0 else 0.0
    cap.release()
    return {
        "fps": round(fps, 2),
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration_seconds": round(duration, 2)
    }

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Uploads a traffic video, extracts metadata, and registers it in SQLite."""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format '{ext}'. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    unique_filename = f"{uuid.uuid4().hex}_{file.filename.replace(' ', '_')}"
    save_path = UPLOAD_DIR / unique_filename

    # Save to disk
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(save_path)
    meta = extract_video_metadata(str(save_path))

    video_data = {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": str(save_path),
        "file_size_bytes": file_size,
        "fps": meta["fps"],
        "total_frames": meta["total_frames"],
        "width": meta["width"],
        "height": meta["height"],
        "duration_seconds": meta["duration_seconds"],
        "status": "uploaded"
    }

    record = crud.create_video(video_data)
    return {
        "message": "Video uploaded successfully",
        "video": record
    }

@router.post("/load-sample")
async def load_sample_video():
    """Generates and registers the synthetic FlowSight test sample video."""
    sample_path = generate_sample_traffic_video(duration_sec=8, fps=25)
    file_size = os.path.getsize(sample_path)
    meta = extract_video_metadata(sample_path)

    unique_filename = f"sample_traffic_{uuid.uuid4().hex[:6]}.mp4"
    dest_path = UPLOAD_DIR / unique_filename
    shutil.copyfile(sample_path, dest_path)

    video_data = {
        "filename": unique_filename,
        "original_filename": "sample_traffic_highway.mp4",
        "file_path": str(dest_path),
        "file_size_bytes": file_size,
        "fps": meta["fps"],
        "total_frames": meta["total_frames"],
        "width": meta["width"],
        "height": meta["height"],
        "duration_seconds": meta["duration_seconds"],
        "status": "uploaded"
    }

    record = crud.create_video(video_data)
    return {
        "message": "Sample traffic video loaded successfully",
        "video": record
    }

@router.get("")
async def list_all_videos(limit: int = 50):
    """Lists all uploaded videos."""
    videos = crud.list_videos(limit=limit)
    return {"videos": videos}

@router.get("/{video_id}")
async def get_video_by_id(video_id: str):
    """Gets details of a single video."""
    video = crud.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"video": video}

@router.delete("/{video_id}")
async def delete_video_by_id(video_id: str):
    """Deletes a video record and associated files."""
    video = crud.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if os.path.exists(video["file_path"]):
        try:
            os.remove(video["file_path"])
        except Exception:
            pass

    if video.get("processed_path") and os.path.exists(video["processed_path"]):
        try:
            os.remove(video["processed_path"])
        except Exception:
            pass

    crud.delete_video(video_id)
    return {"message": "Video deleted successfully"}
