# FlowSight AI — REST API Documentation

## Base URL
`http://localhost:8000/api`

---

## Endpoints

### 1. System Health
- **`GET /health`**
  - **Description**: Verifies backend health and YOLO model status.
  - **Response (200 OK)**:
    ```json
    {
      "status": "healthy",
      "service": "FlowSight AI Backend",
      "model_loaded": true,
      "model_name": "yolov8n.pt"
    }
    ```

---

### 2. Video Management
- **`POST /videos/upload`**
  - **Description**: Uploads a traffic video file (MP4, AVI, MOV, MKV, WEBM).
  - **Content-Type**: `multipart/form-data`
  - **Form Fields**: `file` (binary)
  - **Response (200 OK)**:
    ```json
    {
      "message": "Video uploaded successfully",
      "video": {
        "id": "e2a4b8...",
        "filename": "uuid_traffic.mp4",
        "original_filename": "highway.mp4",
        "fps": 25.0,
        "total_frames": 250,
        "duration_seconds": 10.0,
        "status": "uploaded"
      }
    }
    ```

- **`POST /videos/load-sample`**
  - **Description**: Automatically generates a high-definition synthetic multi-lane traffic video with animated vehicles for immediate zero-config testing.
  - **Response (200 OK)**: Video metadata record.

- **`GET /videos`**
  - **Description**: Lists all uploaded videos and processing statuses.
  - **Query Params**: `limit` (default: 50)

- **`DELETE /videos/{video_id}`**
  - **Description**: Deletes video record and associated files from disk.

---

### 3. Traffic Analysis
- **`POST /analysis/start`**
  - **Description**: Starts YOLO vehicle detection and ByteTrack tracking pipeline.
  - **Request Body**:
    ```json
    {
      "video_id": "e2a4b8...",
      "sample_stride": 1,
      "line_position": 0.55,
      "run_async": true
    }
    ```
  - **Response (200 OK)**:
    ```json
    {
      "message": "Analysis started in background",
      "video_id": "e2a4b8...",
      "status": "processing"
    }
    ```

- **`GET /analysis/status/{video_id}`**
  - **Description**: Real-time progress polling endpoint.
  - **Response (200 OK)**:
    ```json
    {
      "video_id": "e2a4b8...",
      "progress": 72.4,
      "status": "processing",
      "message": "Analyzing frame 181/250 (14 vehicles counted)",
      "frame": 181,
      "total_frames": 250
    }
    ```

- **`GET /analysis/{analysis_id}`**
  - **Description**: Retrieves complete analysis report with full time-series timeline array for charts.

- **`GET /analysis/by-video/{video_id}`**
  - **Description**: Retrieves the latest analysis for a given video ID.

---

### 4. History & Statistics
- **`GET /history`**
  - **Description**: Returns all historical analyses stored in SQLite.

- **`DELETE /history/{analysis_id}`**
  - **Description**: Deletes an analysis record and its time-series data.

- **`GET /stats/dashboard`**
  - **Description**: Aggregated telemetry for dashboard metric cards and modal distribution.
  - **Response (200 OK)**:
    ```json
    {
      "total_videos_analyzed": 5,
      "total_vehicles_counted": 142,
      "average_system_density": 4.8,
      "high_congestion_incidents": 1,
      "vehicle_breakdown": {
        "cars": 104,
        "motorcycles": 22,
        "buses": 8,
        "trucks": 8
      },
      "recent_analyses": [...]
    }
    ```

---

### 5. Media Streaming
- **`GET /media/uploads/{filename}`**: Streams original uploaded MP4 video.
- **`GET /media/processed/{filename}`**: Streams AI-annotated MP4 video with bounding boxes, trajectory lines, and HUD overlay.
