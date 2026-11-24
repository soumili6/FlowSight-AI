"""
FlowSight AI - Rapid Smoke & Unit Test Suite
Executes quick validation tests without long video processing loops.
"""
import sys
import numpy as np
from fastapi.testclient import TestClient

from backend.database import init_db
from backend.main import app
from backend import crud
from backend.tracker import TrafficTracker
from backend.routes.videos import extract_video_metadata

def run_quick_tests():
    print("=" * 60)
    print("FlowSight AI — Rapid Smoke & Unit Tests")
    print("=" * 60)

    # 1. Database Operations Smoke Test
    print("\n[Test 1] Testing SQLite Database CRUD operations...")
    init_db()
    test_video = {
        "filename": "quick_test_video.mp4",
        "original_filename": "quick_test.mp4",
        "file_path": "traffic_videos/samples/sample_traffic.mp4",
        "file_size_bytes": 1024,
        "fps": 25.0,
        "total_frames": 50,
        "width": 640,
        "height": 360,
        "duration_seconds": 2.0,
        "status": "uploaded"
    }
    created_v = crud.create_video(test_video)
    assert created_v is not None, "Failed to create video record"
    v_id = created_v["id"]
    print(f" ✓ Video created with ID: {v_id}")

    test_analysis = {
        "video_id": v_id,
        "total_vehicles_counted": 8,
        "car_count": 5,
        "motorcycle_count": 2,
        "bus_count": 1,
        "truck_count": 0,
        "peak_density": 3.0,
        "average_density": 2.1,
        "congestion_level": "Low",
        "congestion_score": 25.0,
        "processing_time_seconds": 1.2,
        "total_frames_analyzed": 50,
        "status": "completed",
        "summary_insights": "Quick test analysis passed."
    }
    timeline_pts = [
        {"timestamp_sec": 0.0, "frame_number": 0, "active_vehicles": 2, "cumulative_count": 2,
         "car_count": 2, "motorcycle_count": 0, "bus_count": 0, "truck_count": 0, "density": 2.0, "congestion_level": "Low"},
        {"timestamp_sec": 1.0, "frame_number": 25, "active_vehicles": 3, "cumulative_count": 5,
         "car_count": 3, "motorcycle_count": 1, "bus_count": 1, "truck_count": 0, "density": 3.0, "congestion_level": "Low"}
    ]
    created_a = crud.create_analysis(test_analysis, timeline_pts)
    assert created_a is not None, "Failed to create analysis record"
    a_id = created_a["id"]
    print(f" ✓ Analysis record created with ID: {a_id} ({len(created_a.get('timeline', []))} timeline points)")

    stats = crud.get_dashboard_stats()
    assert stats["total_vehicles_counted"] >= 8
    print(" ✓ Dashboard stats aggregated successfully:", stats["vehicle_breakdown"])

    # Clean up test records
    crud.delete_analysis(a_id)
    crud.delete_video(v_id)
    print(" ✓ Cleaned up test records")

    # 2. FastAPI Endpoint Routes Smoke Test
    print("\n[Test 2] Testing FastAPI Endpoints...")
    client = TestClient(app)

    # Health
    r_health = client.get("/api/health")
    assert r_health.status_code == 200, f"Health check failed: {r_health.text}"
    assert r_health.json()["status"] == "healthy"
    print(" ✓ GET /api/health -> 200 OK (Model ready:", r_health.json()["model_loaded"], ")")

    # Videos List
    r_videos = client.get("/api/videos")
    assert r_videos.status_code == 200
    print(" ✓ GET /api/videos -> 200 OK")

    # History List
    r_history = client.get("/api/history")
    assert r_history.status_code == 200
    print(" ✓ GET /api/history -> 200 OK")

    # Dashboard Stats
    r_stats = client.get("/api/stats/dashboard")
    assert r_stats.status_code == 200
    print(" ✓ GET /api/stats/dashboard -> 200 OK")

    # 3. AI Tracker Single-Frame Inference Test
    print("\n[Test 3] Testing YOLOv8 + ByteTrack Single-Frame Inference & HUD...")
    tracker = TrafficTracker()
    tracker.reset()
    dummy_frame = np.full((360, 640, 3), 40, dtype=np.uint8)
    annotated_frame, metrics = tracker.process_frame(dummy_frame, frame_idx=0, line_ratio=0.55, draw_annotations=True)
    assert annotated_frame.shape == (360, 640, 3), "Annotated frame shape mismatch"
    assert "cumulative_count" in metrics, "Missing cumulative_count in metrics"
    assert "density" in metrics, "Missing density in metrics"
    assert "congestion_level" in metrics, "Missing congestion_level in metrics"
    print(f" ✓ Frame processed in real-time. Metrics: {metrics}")

    # 4. Video Metadata Extraction Test
    print("\n[Test 4] Testing Video Metadata Extraction...")
    meta = extract_video_metadata("traffic_videos/samples/sample_traffic.mp4")
    assert meta["width"] == 640
    assert meta["height"] == 360
    assert meta["fps"] > 0
    print(f" ✓ Video metadata valid: {meta['width']}x{meta['height']} @ {meta['fps']} FPS ({meta['duration_seconds']}s)")

    print("\n" + "=" * 60)
    print(" ALL RAPID BACKEND TESTS PASSED SUCCESSFULLY! ")
    print("=" * 60)

if __name__ == "__main__":
    run_quick_tests()
