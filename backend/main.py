import logging
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse, Response

from backend.config import (
    CORS_ORIGINS,
    UPLOAD_DIR,
    PROCESSED_DIR,
    YOLO_MODEL_PATH
)
from backend.database import init_db
from backend.routes import videos, analysis, history, stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("flowsight")

app = FastAPI(
    title="FlowSight AI API",
    description="Intelligent Traffic Monitoring and Analytics System API",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing FlowSight AI database...")
    init_db()
    logger.info("FlowSight AI backend ready.")

# Include API Routers
app.include_router(videos.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


# ── Byte-range aware video streaming ────────────────────────────────────────
# Browsers (Chrome/Edge/Firefox) require HTTP 206 partial-content responses
# to calculate video duration, enable the seek bar, and start playback.
# FastAPI's plain FileResponse does NOT send Accept-Ranges headers, so we
# implement byte-range streaming manually.

CHUNK = 1024 * 512   # 512 KB chunks

def _stream_video(file_path: Path, request: Request):
    """
    Returns a StreamingResponse that honours HTTP Range requests (including suffix ranges).
    Sends 206 Partial Content when a Range header is present,
    or 200 with the full file otherwise.
    Always sets Accept-Ranges: bytes so browsers can probe duration and seek.
    """
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"detail": "Video file not found"})

    file_size = file_path.stat().st_size
    range_header = request.headers.get("Range")

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": "video/mp4",
        "Content-Length": str(file_size),
        "Cache-Control": "public, max-age=3600",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        "Access-Control-Allow-Headers": "Range, Accept-Ranges, Content-Range, Content-Type",
    }

    # Handle HEAD request for media probing
    if request.method == "HEAD":
        return Response(status_code=200, headers=headers, media_type="video/mp4")

    if range_header:
        # Standard HTTP Range: bytes=start-end, bytes=start-, or bytes=-suffix_len
        try:
            byte_range = range_header.replace("bytes=", "").strip()
            if "," in byte_range:
                byte_range = byte_range.split(",")[0].strip()

            start_str, end_str = byte_range.split("-")
            start_str = start_str.strip()
            end_str = end_str.strip()

            if not start_str:
                # Suffix byte range: bytes=-500 (last 500 bytes of the file)
                suffix_len = int(end_str)
                start = max(0, file_size - suffix_len)
                end = file_size - 1
            else:
                start = int(start_str)
                end = int(end_str) if end_str else file_size - 1

            if start < 0 or start >= file_size or start > end:
                return JSONResponse(
                    status_code=416,
                    content={"detail": "Range Not Satisfiable"},
                    headers={
                        "Content-Range": f"bytes */{file_size}",
                        "Accept-Ranges": "bytes"
                    }
                )

            end = min(end, file_size - 1)
            chunk_size = end - start + 1

            def iter_range():
                with open(file_path, "rb") as f:
                    f.seek(start)
                    remaining = chunk_size
                    while remaining > 0:
                        data = f.read(min(CHUNK, remaining))
                        if not data:
                            break
                        remaining -= len(data)
                        yield data

            range_headers = {
                **headers,
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(chunk_size),
            }
            return StreamingResponse(
                iter_range(),
                status_code=206,
                headers=range_headers,
                media_type="video/mp4",
            )
        except Exception as e:
            logger.warning(f"Failed to parse Range header '{range_header}': {e}; serving full file")

    # Full file (no Range header or parse error fallback)
    def iter_full():
        with open(file_path, "rb") as f:
            while True:
                data = f.read(CHUNK)
                if not data:
                    break
                yield data

    return StreamingResponse(iter_full(), status_code=200, headers=headers, media_type="video/mp4")


@app.api_route("/media/uploads/{filename}", methods=["GET", "HEAD"])
async def serve_upload_media(filename: str, request: Request):
    """Streams an original uploaded video with byte-range support."""
    return _stream_video(UPLOAD_DIR / filename, request)


@app.api_route("/media/processed/{filename}", methods=["GET", "HEAD"])
async def serve_processed_media(filename: str, request: Request):
    """Streams an AI-annotated processed video with byte-range support."""
    return _stream_video(PROCESSED_DIR / filename, request)


# Mount static directories (for direct static serving fallback)
app.mount("/static/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/static/processed", StaticFiles(directory=str(PROCESSED_DIR)), name="processed")


@app.get("/api/health")
async def health_check():
    """Health check endpoint providing model and backend status."""
    return {
        "status": "healthy",
        "service": "FlowSight AI Backend",
        "model_loaded": YOLO_MODEL_PATH.exists(),
        "model_name": YOLO_MODEL_PATH.name
    }
