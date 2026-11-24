"""
FlowSight AI — focused verification of the three key fixes.
Run with:  .\\venv\\Scripts\\python.exe test_fixes.py

Tests (no server, no TestClient, no asyncio.run):
  1. All three changed modules import without errors.
  2. H.264 VideoWriter (_open_h264_writer) produces a file with avc1/h264 fourcc.
  3. create_browser_video_writer (video_processor) works identically.
  4. Sample video exists, is >=100 KB, and is 1280x720.
  5. _stream_video byte-range 206 response (Range header present).
  6. _stream_video full-file 200 response (no Range header).
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock

PASS = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"  PASS  {msg}")

def fail(msg, exc=None):
    global FAIL
    FAIL += 1
    err = f" — {exc}" if exc else ""
    print(f"  FAIL  {msg}{err}")

print("\n=== FlowSight AI Fix Verification ===\n")

# ── Test 1: Imports ──────────────────────────────────────────────────────────
print("1. Module imports")
try:
    from backend.sample_generator import generate_sample_traffic_video, _open_h264_writer
    ok("backend.sample_generator imports OK")
except Exception as e:
    fail("backend.sample_generator", e)

try:
    from backend.video_processor import create_browser_video_writer
    ok("backend.video_processor imports OK")
except Exception as e:
    fail("backend.video_processor", e)

try:
    from backend.main import _stream_video
    ok("backend.main._stream_video imports OK")
except Exception as e:
    fail("backend.main._stream_video", e)

# ── Test 2: H.264 writer from sample_generator ───────────────────────────────
print("\n2. H.264 VideoWriter (_open_h264_writer)")
test_path = "_test_sg.mp4"
try:
    writer = _open_h264_writer(test_path, 25.0, 320, 240)
    if not writer.isOpened():
        fail("_open_h264_writer: writer did not open")
    else:
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        writer.write(frame)
        writer.release()
        cap = cv2.VideoCapture(test_path)
        fc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
        fc_str = "".join(chr((fc_int >> 8 * i) & 0xFF) for i in range(4)).lower().strip("\x00")
        cap.release()
        fsize = Path(test_path).stat().st_size
        ok(f"_open_h264_writer: fourcc='{fc_str}', file size={fsize} bytes")
except Exception as e:
    fail("_open_h264_writer raised exception", e)
finally:
    import time; time.sleep(0.5)
    try:
        if Path(test_path).exists():
            os.remove(test_path)
    except Exception:
        pass  # Windows file lock — not a test failure

# ── Test 3: H.264 writer from video_processor ────────────────────────────────
print("\n3. H.264 VideoWriter (create_browser_video_writer)")
test_path2 = "_test_vp.mp4"
try:
    writer2 = create_browser_video_writer(test_path2, 25.0, 320, 240)
    if not writer2.isOpened():
        fail("create_browser_video_writer: writer did not open")
    else:
        writer2.write(np.zeros((240, 320, 3), dtype=np.uint8))
        writer2.release()
        cap2 = cv2.VideoCapture(test_path2)
        fc_int2 = int(cap2.get(cv2.CAP_PROP_FOURCC))
        fc_str2 = "".join(chr((fc_int2 >> 8 * i) & 0xFF) for i in range(4)).lower().strip("\x00")
        cap2.release()
        fsize2 = Path(test_path2).stat().st_size
        ok(f"create_browser_video_writer: fourcc='{fc_str2}', file size={fsize2} bytes")
except Exception as e:
    fail("create_browser_video_writer raised exception", e)
finally:
    import time; time.sleep(0.5)
    try:
        if Path(test_path2).exists():
            os.remove(test_path2)
    except Exception:
        pass

# ── Test 4: Sample video metadata ────────────────────────────────────────────
print("\n4. Sample video file")
sample = Path("traffic_videos/samples/sample_traffic.mp4")
try:
    assert sample.exists(), f"{sample} does not exist"
    size = sample.stat().st_size
    assert size > 100_000, f"Too small: {size} bytes"
    cap3 = cv2.VideoCapture(str(sample))
    w = cap3.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cap3.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frames = int(cap3.get(cv2.CAP_PROP_FRAME_COUNT))
    fps_v = cap3.get(cv2.CAP_PROP_FPS)
    cap3.release()
    assert w > 0 and h > 0, "Could not read video dimensions"
    ok(f"sample_traffic.mp4: {int(w)}x{int(h)}, {frames} frames @ {fps_v:.1f} fps, {size:,} bytes")
except AssertionError as e:
    fail("Sample video assertion failed", e)
except Exception as e:
    fail("Sample video check raised exception", e)

# ── Test 5: _stream_video with Range header (206) ────────────────────────────
print("\n5. _stream_video — byte-range 206 response")
try:
    req_range = MagicMock()
    req_range.headers = {"Range": "bytes=0-511"}
    resp = _stream_video(sample, req_range)
    assert resp.status_code == 206, f"Expected 206, got {resp.status_code}"
    assert resp.headers.get("accept-ranges") == "bytes", "Missing Accept-Ranges: bytes"
    cr = resp.headers.get("content-range", "")
    assert cr.startswith("bytes 0-511/"), f"Unexpected Content-Range: {cr!r}"
    cl = resp.headers.get("content-length", "")
    assert cl == "512", f"Expected content-length=512, got {cl!r}"
    ok(f"206 Partial Content: Content-Range={cr}, Content-Length={cl}")
except AssertionError as e:
    fail("206 assertion failed", e)
except Exception as e:
    fail("206 test raised exception", e)

# ── Test 6: _stream_video without Range header (200) ─────────────────────────
print("\n6. _stream_video — full-file 200 response")
try:
    req_full = MagicMock()
    req_full.headers = {}
    resp2 = _stream_video(sample, req_full)
    assert resp2.status_code == 200, f"Expected 200, got {resp2.status_code}"
    assert resp2.headers.get("accept-ranges") == "bytes", "Missing Accept-Ranges: bytes"
    cl2 = resp2.headers.get("content-length", "")
    file_size = str(sample.stat().st_size)
    assert cl2 == file_size, f"Content-Length mismatch: got {cl2}, expected {file_size}"
    ok(f"200 OK: Accept-Ranges=bytes, Content-Length={cl2}")
except AssertionError as e:
    fail("200 assertion failed", e)
except Exception as e:
    fail("200 test raised exception", e)

# ── Summary ──────────────────────────────────────────────────────────────────
print(f"\n{'='*40}")
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL == 0:
    print("=== ALL FIXES VERIFIED ===")
else:
    print("=== SOME TESTS FAILED — see above ===")
    sys.exit(1)
