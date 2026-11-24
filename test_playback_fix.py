import sys
import os
import cv2
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock

print('=== 1. CHECK PROCESSED VIDEOS ON DISK ===')
processed_dir = Path('traffic_videos/processed')
videos = [v for v in processed_dir.glob('*_processed.mp4') if v.stat().st_size > 50000]
print(f'Found {len(videos)} valid processed video(s):')
for v in videos:
    cap = cv2.VideoCapture(str(v))
    opened = cap.isOpened()
    fc = int(cap.get(cv2.CAP_PROP_FOURCC))
    fc_str = ''.join([chr((fc >> 8 * i) & 0xFF) for i in range(4)]).lower()
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    ret, frame = cap.read() if opened else (False, None)
    cap.release()
    print(f'  {v.name}:')
    print(f'    Size: {v.stat().st_size:,} bytes')
    print(f'    Codec fourcc: {fc_str} (H.264 compatible: {fc_str in ["h264", "avc1"]})')
    print(f'    Dims: {w}x{h} @ {fps} fps, frames: {frames}, readable: {ret}')
    assert fc_str in ['h264', 'avc1'], f'Expected H.264 codec, got {fc_str}'

print('\n=== 2. CHECK FASTAPI VIDEO SERVING ENDPOINT ===')
from backend.main import _stream_video
target_video = videos[0]

# A: Full GET request (no Range header) -> 200 OK
req_full = MagicMock()
req_full.headers = {}
req_full.method = 'GET'
res_full = _stream_video(target_video, req_full)
print(f'  Full GET: status={res_full.status_code}, Accept-Ranges={res_full.headers.get("accept-ranges")}, Content-Type={res_full.headers.get("content-type")}, Content-Length={res_full.headers.get("content-length")}')
assert res_full.status_code == 200
assert res_full.headers.get('accept-ranges') == 'bytes'
assert res_full.headers.get('content-type') == 'video/mp4'

# B: Standard Range request (bytes=0-1023) -> 206 Partial Content
req_r1 = MagicMock()
req_r1.headers = {'Range': 'bytes=0-1023'}
req_r1.method = 'GET'
res_r1 = _stream_video(target_video, req_r1)
print(f'  Range 0-1023: status={res_r1.status_code}, Content-Range={res_r1.headers.get("content-range")}, Content-Length={res_r1.headers.get("content-length")}')
assert res_r1.status_code == 206
assert res_r1.headers.get('content-range').startswith('bytes 0-1023/')
assert res_r1.headers.get('content-length') == '1024'

# C: Suffix Range request (bytes=-2048) -> 206 Partial Content (critical for moov atom at end of file)
req_r2 = MagicMock()
req_r2.headers = {'Range': 'bytes=-2048'}
req_r2.method = 'GET'
res_r2 = _stream_video(target_video, req_r2)
print(f'  Suffix Range -2048: status={res_r2.status_code}, Content-Range={res_r2.headers.get("content-range")}, Content-Length={res_r2.headers.get("content-length")}')
assert res_r2.status_code == 206
assert 'bytes ' in res_r2.headers.get('content-range')
assert res_r2.headers.get('content-length') == '2048'

# D: Open-ended Range request (bytes=1000-) -> 206 Partial Content
req_r3 = MagicMock()
req_r3.headers = {'Range': 'bytes=1000-'}
req_r3.method = 'GET'
res_r3 = _stream_video(target_video, req_r3)
print(f'  Open-ended Range 1000-: status={res_r3.status_code}, Content-Range={res_r3.headers.get("content-range")}')
assert res_r3.status_code == 206

# E: HEAD request -> 200 OK (no body, proper headers for browser probe)
req_head = MagicMock()
req_head.headers = {}
req_head.method = 'HEAD'
res_head = _stream_video(target_video, req_head)
print(f'  HEAD request: status={res_head.status_code}, Accept-Ranges={res_head.headers.get("accept-ranges")}')
assert res_head.status_code == 200
assert res_head.headers.get('accept-ranges') == 'bytes'

print('\n=== 3. CHECK create_browser_video_writer ===')
from backend.video_processor import create_browser_video_writer

tmp_out = '_verify_browser_writer.mp4'
wtr = create_browser_video_writer(tmp_out, 25.0, 640, 360)
assert wtr.isOpened(), 'Writer failed to open'
dummy_frame = np.zeros((360, 640, 3), dtype=np.uint8)
for _ in range(5):
    wtr.write(dummy_frame)
wtr.release()

cap_wtr = cv2.VideoCapture(tmp_out)
fc_wtr = ''.join([chr((int(cap_wtr.get(cv2.CAP_PROP_FOURCC)) >> 8 * i) & 0xFF) for i in range(4)]).lower()
cap_wtr.release()
print(f'  Browser writer output fourcc: {fc_wtr}')
assert fc_wtr in ['h264', 'avc1'], f'Expected h264, got {fc_wtr}'
try:
    os.remove(tmp_out)
except:
    pass

print('\n=== ALL PLAYBACK & STREAMING CHECKS PASSED ===')
