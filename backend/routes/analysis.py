import asyncio
import threading
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from backend import crud
from backend.video_processor import (
    process_video_pipeline,
    get_job_progress,
    update_job_progress
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])
logger = logging.getLogger(__name__)

class StartAnalysisRequest(BaseModel):
    video_id: str
    sample_stride: Optional[int] = 1
    line_position: Optional[float] = 0.55
    run_async: Optional[bool] = True

def _run_background_analysis(video_id: str, stride: int, line_pos: float):
    """
    Runs the CPU-bound video analysis pipeline in a plain Python thread.
    This keeps OpenCV and PyTorch off the asyncio event loop, which prevents
    the 'Unknown C++ exception from OpenCV code' crash that occurs when
    OpenCV's FFMPEG backend is called while the asyncio loop is running.
    """
    try:
        process_video_pipeline(
            video_id=video_id,
            stride=stride,
            line_position=line_pos
        )
    except Exception as e:
        logger.exception(f"Background analysis failed for video {video_id}: {e}")
        update_job_progress(video_id, 0.0, "failed", str(e))

@router.post("/start")
async def start_analysis(payload: StartAnalysisRequest, background_tasks: BackgroundTasks):
    """Starts YOLO vehicle detection, tracking, and traffic analytics on a video."""
    video = crud.get_video(payload.video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Always run the CPU-bound pipeline in a background thread to avoid blocking
    # the asyncio event loop.  Running OpenCV/FFMPEG synchronously inside an
    # async handler causes 'Unknown C++ exception from OpenCV code'.
    update_job_progress(payload.video_id, 0.0, "processing", "Queueing analysis job...")

    if payload.run_async:
        # FastAPI BackgroundTask — runs after the response is sent
        background_tasks.add_task(
            _run_background_analysis,
            payload.video_id,
            payload.sample_stride,
            payload.line_position
        )
        return {
            "message": "Analysis started in background",
            "video_id": payload.video_id,
            "status": "processing"
        }
    else:
        # 'run_async=false' requested: still offload to a thread so we don't
        # block asyncio, but we await its completion before responding.
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,  # default ThreadPoolExecutor
                lambda: process_video_pipeline(
                    video_id=payload.video_id,
                    stride=payload.sample_stride,
                    line_position=payload.line_position
                )
            )
            return {
                "message": "Analysis completed successfully",
                "analysis": result
            }
        except Exception as e:
            logger.exception(f"Synchronous analysis failed for video {payload.video_id}")
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{video_id}")
async def check_analysis_status(video_id: str):
    """Returns current real-time progress of video analysis."""
    job = get_job_progress(video_id)
    return job

@router.get("/{analysis_id}")
async def get_analysis_details(analysis_id: str):
    """Retrieves full analysis report including time-series timeline metrics."""
    analysis = crud.get_analysis(analysis_id, include_timeline=True)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found")
    return {"analysis": analysis}

@router.get("/by-video/{video_id}")
async def get_latest_video_analysis(video_id: str):
    """Retrieves the latest analysis associated with a given video ID."""
    with crud.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM analyses WHERE video_id = ? ORDER BY created_at DESC LIMIT 1
        """, (video_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No analysis found for this video")
        
        return await get_analysis_details(row["id"])
