import os
import sys
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import init_db

def run_e2e_test():
    print("=" * 60)
    print("FlowSight AI — Full End-to-End System Integration Test")
    print("=" * 60)

    # 1. Initialize DB
    init_db()
    client = TestClient(app)

    # 2. Health Check
    print("\n[Step 1] Testing Health Endpoint...")
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200, f"Health check failed: {health_resp.text}"
    health_data = health_resp.json()
    print(" Health response:", health_data)
    assert health_data["status"] == "healthy"
    assert health_data["model_loaded"] is True

    # 3. Load Sample Video
    print("\n[Step 2] Testing Sample Video Generation & Ingestion...")
    sample_resp = client.post("/api/videos/load-sample")
    assert sample_resp.status_code == 200, f"Sample load failed: {sample_resp.text}"
    sample_data = sample_resp.json()
    video = sample_data["video"]
    video_id = video["id"]
    print(f" Sample video created: {video['filename']} (ID: {video_id})")
    print(f" Video resolution: {video['width']}x{video['height']} | Frames: {video['total_frames']} | Duration: {video['duration_seconds']}s")
    assert os.path.exists(video["file_path"]), "Uploaded video file does not exist on disk!"

    # 4. Run Analysis (Synchronous)
    print("\n[Step 3] Running Full AI Inference Pipeline (YOLOv8 + ByteTrack)...")
    analysis_resp = client.post("/api/analysis/start", json={
        "video_id": video_id,
        "sample_stride": 1,
        "line_position": 0.55,
        "run_async": False
    })
    assert analysis_resp.status_code == 200, f"Analysis failed: {analysis_resp.text}"
    analysis_data = analysis_resp.json()["analysis"]
    analysis_id = analysis_data["id"]
    print(f" Analysis Complete (ID: {analysis_id})")
    print(f"  - Total Vehicles Counted: {analysis_data['total_vehicles_counted']}")
    print(f"  - Cars: {analysis_data['car_count']}, Motorcycles: {analysis_data['motorcycle_count']}, Buses: {analysis_data['bus_count']}, Trucks: {analysis_data['truck_count']}")
    print(f"  - Avg Density: {analysis_data['average_density']} | Peak: {analysis_data['peak_density']}")
    print(f"  - Congestion Level: {analysis_data['congestion_level']} (Score: {analysis_data['congestion_score']}%)")
    print(f"  - Processing Time: {analysis_data['processing_time_seconds']}s")
    print(f"  - Timeline Records Generated: {len(analysis_data.get('timeline', []))}")

    # Check processed video exists
    processed_path = analysis_data.get("video_processed_path")
    if processed_path:
        assert os.path.exists(processed_path), f"Processed video output not found at: {processed_path}"
        print(f" Annotated video saved to disk: {os.path.basename(processed_path)} ({os.path.getsize(processed_path)} bytes)")

    # 5. Verify Timeline Data Points
    assert len(analysis_data.get("timeline", [])) > 0, "No timeline points recorded!"

    # 6. Verify Dashboard Stats Aggregation
    print("\n[Step 4] Testing Dashboard Statistics Endpoint...")
    stats_resp = client.get("/api/stats/dashboard")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    print(" Dashboard Telemetry:", stats)
    assert stats["total_videos_analyzed"] >= 1
    assert stats["total_vehicles_counted"] >= 1

    # 7. Verify History Endpoint
    print("\n[Step 5] Testing History Endpoint...")
    history_resp = client.get("/api/history")
    assert history_resp.status_code == 200
    history = history_resp.json()["analyses"]
    print(f" History count: {len(history)} records")
    assert len(history) >= 1

    print("\n" + "=" * 60)
    print(" ALL END-TO-END TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_test()
