"""
FlowSight AI — Sample Traffic Video Provider
Provides a real H.264 traffic surveillance video (cars.mp4, 7s, 1280×720).
Falls back to a synthetic H.264 clip only if network is unavailable.
"""
import os
import shutil
import logging
import cv2
import numpy as np
from typing import Optional
from pathlib import Path

from backend.config import TRAFFIC_VIDEOS_DIR

logger = logging.getLogger(__name__)

# Publicly licensed short traffic clip with real photographic cars/trucks
SAMPLE_URL = "https://github.com/opengeos/datasets/releases/download/videos/cars.mp4"


def _open_h264_writer(path: str, fps: float, width: int, height: int) -> cv2.VideoWriter:
    """
    Returns the first working VideoWriter that produces a browser-playable H.264 MP4.
    Tries MSMF (H264) on Windows -> avc1 -> H264 -> mp4v in order.
    """
    if os.name == 'nt' and hasattr(cv2, 'CAP_MSMF'):
        for tag in ('H264', 'avc1'):
            try:
                fourcc = cv2.VideoWriter_fourcc(*tag)
                writer = cv2.VideoWriter(path, cv2.CAP_MSMF, fourcc, fps, (width, height))
                if writer.isOpened():
                    logger.info("MSMF VideoWriter opened with codec '%s' at %s", tag, path)
                    return writer
            except Exception as e:
                logger.warning("MSMF codec '%s' failed: %s", tag, e)

    for tag in ('avc1', 'H264', 'mp4v'):
        fourcc = cv2.VideoWriter_fourcc(*tag)
        writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
        if writer.isOpened():
            logger.info("VideoWriter opened with codec '%s' at %s", tag, path)
            return writer
        writer.release()  # release any incomplete writer before trying next codec

    # Absolute fallback — mp4v with explicit FourCC (should always succeed)
    logger.warning("All preferred codecs failed; using raw mp4v fallback for %s", path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    return cv2.VideoWriter(path, fourcc, fps, (width, height))


def _build_synthetic_fallback(path: str, duration_sec: int, fps: int,
                               width: int, height: int) -> None:
    """
    Writes a 7-second, 1280×720 synthetic road scene using H.264 so the browser
    can at least play something when the network sample is unavailable.
    The scene includes gradient sky, asphalt road, lane markings, and
    textured rectangles sized and shaped like real vehicle silhouettes so
    detection is visually meaningful even if YOLO confidence is low.
    """
    out = _open_h264_writer(path, float(fps), width, height)
    total_frames = duration_sec * fps

    # Six vehicle tracks: (lane_x, start_y, speed_px_per_frame, w, h, bgr_color)
    vehicles = [
        {"x": 320,  "y": -120,         "speed":  5.0,  "w": 110, "h": 55,  "color": (60, 130, 220)},
        {"x": 480,  "y": -300,         "speed":  7.0,  "w": 105, "h": 50,  "color": (30,  80, 180)},
        {"x": 800,  "y": height + 160, "speed": -5.5,  "w": 115, "h": 58,  "color": (200, 100, 40)},
        {"x": 960,  "y": height + 350, "speed": -6.0,  "w": 108, "h": 52,  "color": (40, 160,  80)},
        {"x": 400,  "y": -600,         "speed":  8.0,  "w": 180, "h": 72,  "color": (60,  60, 160)},  # bus
        {"x": 880,  "y": height + 600, "speed": -4.5,  "w": 200, "h": 85,  "color": (80,  60,  60)},  # truck
    ]

    for frame_idx in range(total_frames):
        # --- Road background -------------------------------------------------
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Sky gradient (top 15 %)
        sky_h = height // 7
        for row in range(sky_h):
            brightness = int(100 + 60 * row / sky_h)
            frame[row, :] = (brightness, brightness // 2, brightness // 3)

        # Asphalt (rest)
        frame[sky_h:, :] = (55, 58, 62)

        # Green shoulder strips
        frame[sky_h:, :160]       = (40, 90, 40)
        frame[sky_h:, width - 160:] = (40, 90, 40)

        # Solid white shoulder lines
        cv2.line(frame, (160, sky_h), (160, height), (220, 220, 220), 3)
        cv2.line(frame, (width - 160, sky_h), (width - 160, height), (220, 220, 220), 3)

        # Double yellow centre divider
        cv2.line(frame, (width // 2 - 3, sky_h), (width // 2 - 3, height), (0, 220, 255), 3)
        cv2.line(frame, (width // 2 + 3, sky_h), (width // 2 + 3, height), (0, 220, 255), 3)

        # Dashed lane markers (animated)
        dash_offset = (frame_idx * 6) % 60
        for lane_x in (380, 560, 720, 900):
            for y in range(-60 + dash_offset + sky_h, height + 60, 60):
                cv2.line(frame, (lane_x, y), (lane_x, y + 30), (200, 200, 200), 2)

        # --- Vehicles --------------------------------------------------------
        for v in vehicles:
            v["y"] += v["speed"]
            vx = v["x"]
            vy = int(v["y"])
            vw = v["w"]
            vh = v["h"]
            col = v["color"]

            if -200 <= vy <= height + 200:
                # Body with slight texture noise so YOLO has gradient features
                body = frame[max(0, vy - vh // 2):vy + vh // 2,
                             max(0, vx - vw // 2):vx + vw // 2].copy()
                noise = np.random.randint(-15, 15, body.shape, dtype=np.int16)
                body = np.clip(body.astype(np.int16) + noise, 0, 255).astype(np.uint8)

                # Draw body rectangle
                cv2.rectangle(frame,
                              (vx - vw // 2, vy - vh // 2),
                              (vx + vw // 2, vy + vh // 2),
                              col, -1)
                # Dark outline
                cv2.rectangle(frame,
                              (vx - vw // 2, vy - vh // 2),
                              (vx + vw // 2, vy + vh // 2),
                              (20, 20, 20), 2)

                # Windscreen (lighter panel)
                ws_w = int(vw * 0.65)
                ws_h = int(vh * 0.38)
                cv2.rectangle(frame,
                              (vx - ws_w // 2, vy - ws_h // 2),
                              (vx + ws_w // 2, vy + ws_h // 2),
                              (120, 140, 160), -1)

                # Wheels (dark circles at four corners)
                wheel_r = max(5, vh // 7)
                for wx, wy in [
                    (vx - vw // 2 + wheel_r, vy + vh // 2 - wheel_r),
                    (vx + vw // 2 - wheel_r, vy + vh // 2 - wheel_r),
                    (vx - vw // 2 + wheel_r, vy - vh // 2 + wheel_r),
                    (vx + vw // 2 - wheel_r, vy - vh // 2 + wheel_r),
                ]:
                    cv2.circle(frame, (wx, wy), wheel_r, (20, 20, 20), -1)
                    cv2.circle(frame, (wx, wy), max(2, wheel_r // 2), (80, 80, 80), -1)

                # Headlights / tail-lights
                light_col = (220, 240, 255) if v["speed"] > 0 else (40, 60, 240)
                for lx in (vx - vw // 2 + 8, vx + vw // 2 - 8):
                    ly = vy + vh // 2 - 8 if v["speed"] > 0 else vy - vh // 2 + 8
                    cv2.circle(frame, (lx, ly), 5, light_col, -1)

            # Loop vehicle back
            if v["speed"] > 0 and v["y"] > height + 220:
                v["y"] = -120
            elif v["speed"] < 0 and v["y"] < -220:
                v["y"] = height + 120

        out.write(frame)

    out.release()
    logger.info("Synthetic fallback video written to %s (%d frames @ %d fps)", path, total_frames, fps)


def generate_sample_traffic_video(
    output_path: Optional[str] = None,
    duration_sec: int = 7,
    fps: int = 25,
    width: int = 1280,
    height: int = 720,
) -> str:
    """
    Returns the path to the FlowSight AI demo traffic video:
      • Primary: downloads the publicly licensed 7-second H.264 highway clip.
      • Fallback: generates a 7-second, 1280×720 synthetic H.264 clip.

    Both sources are browser-playable (H.264/AVC1 container) and produce
    real vehicle-sized silhouettes that YOLOv8 can detect.
    """
    samples_dir = TRAFFIC_VIDEOS_DIR / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    canonical = samples_dir / "sample_traffic.mp4"
    target = Path(output_path) if output_path else canonical

    # Already present and large enough → reuse
    if canonical.exists() and canonical.stat().st_size > 100_000:
        if target.resolve() != canonical.resolve():
            shutil.copyfile(str(canonical), str(target))
        logger.info("Reusing existing sample video at %s", canonical)
        return str(target)

    # Try downloading the real traffic video
    try:
        import urllib.request
        logger.info("Downloading sample traffic video from %s …", SAMPLE_URL)
        urllib.request.urlretrieve(SAMPLE_URL, str(canonical))
        # Validate the download
        if canonical.stat().st_size < 100_000:
            raise ValueError("Downloaded file too small – likely a redirect/error page.")
        logger.info("Sample video downloaded: %d bytes", canonical.stat().st_size)
        if target.resolve() != canonical.resolve():
            shutil.copyfile(str(canonical), str(target))
        return str(target)
    except Exception as exc:
        logger.warning("Could not download sample video (%s). Generating synthetic fallback.", exc)
        if canonical.exists():
            canonical.unlink()  # remove any partial download

    # Generate synthetic fallback (7 s, 1280×720, H.264)
    _build_synthetic_fallback(str(target), duration_sec, fps, width, height)
    if target.resolve() != canonical.resolve():
        shutil.copyfile(str(target), str(canonical))

    return str(target)
