# FlowSight AI — System Architecture Specification

## 1. Executive Overview
**FlowSight AI** is an intelligent, automated traffic monitoring and computer vision analytics system. It transforms raw traffic video streams into actionable traffic intelligence: detecting multi-class vehicles, tracking individual movement trajectories across frames using ByteTrack, computing lane-level and screen density, classifying real-time congestion levels, and maintaining historical telemetry in an SQLite database.

```
                      +-----------------------------------+
                      |       Raw Traffic Video Feed      |
                      |   (Highway, Junction, Arterial)   |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |     FastAPI Ingestion Engine      |
                      |    (Metadata, Stride, Resizer)    |
                      +-----------------+-----------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |    AI Vision Processing Core      |
                      |  - YOLOv8 Multi-Class Detection   |
                      |  - ByteTrack Association Filter   |
                      |  - Trajectory & Velocity Vector   |
                      |  - Virtual Counting Line Sensor   |
                      +-----------------+-----------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
  +--------------+---------------+             +---------------+--------------+
  |    SQLite Persistence Store   |             |   Annotated Video Stream     |
  |  - analyses (summary stats)   |             |  - Bounding Box HUD          |
  |  - analysis_timeline (series) |             |  - Trajectory trails         |
  |  - videos (metadata)          |             |  - Real-time density badge   |
  +--------------+---------------+             +---------------+--------------+
                 |                                             |
                 +----------------------+----------------------+
                                        |
                                        v
                      +-----------------+-----------------+
                      |    React + Vite + Tailwind UI     |
                      |  - Live Video Monitoring Player   |
                      |  - Recharts Density & Flow Trends |
                      |  - Class Breakdown Distribution   |
                      |  - Historical Audit Archive       |
                      +-----------------------------------+
```

---

## 2. Component Architecture

### 2.1 Backend Core (Python FastAPI)
- **FastAPI Framework**: High-throughput asynchronous REST API with automatic Pydantic validation, CORS middleware, and static streaming.
- **Computer Vision Pipeline (`backend/tracker.py`)**:
  - **Detector**: Pretrained `YOLOv8n` optimized for edge inference on COCO vehicles (Class 2: Car, Class 3: Motorcycle, Class 5: Bus, Class 7: Truck).
  - **Tracker**: `ByteTrack` association filter maintaining persistent integer IDs across occlusions, variable lighting, and camera motion.
  - **Trajectory & Counting Engine**: Maintains vehicle centroid history buffer (\(cx, cy\)). When a trajectory intersects the designated virtual counting line \(y = line\_pos \times height\), the vehicle ID is irreversibly registered into the counted set, preventing duplicate increments.
  - **Density & Congestion Classifier**:
    $$\text{Density} = \text{Active Vehicles Detected per Frame}$$
    $$\text{Congestion Score} = f(\text{Density}, \text{Heavy Vehicle Ratio}, \text{Mean Velocity Displacement})$$
    - **Low Congestion**: Density < 4.0 vehicles/frame (Score 0–35%)
    - **Medium Congestion**: Density 4.0–10.0 vehicles/frame (Score 35–70%)
    - **High Congestion**: Density > 10.0 vehicles/frame or stationary queue (Score 70–100%)

### 2.2 Storage Engine (SQLite)
- **`videos`**: Tracks uploaded and processed MP4 files, duration, FPS, resolutions, and lifecycle status.
- **`analyses`**: Stores aggregated session metrics (total counted, vehicle category breakdown, peak density, average density, congestion classification, AI executive summary).
- **`analysis_timeline`**: High-granularity time series captured at 1-second intervals for rendering Recharts time-series graphs.

### 2.3 Frontend Dashboard (React + Vite + Tailwind CSS)
- **Vite 5 Build Tool**: Sub-millisecond HMR and optimized production bundles.
- **Tailwind CSS**: Modern dark-navy dashboard theme (`#070d18`, `#0b1329`, `#0f1c3a`) with cyan, emerald, and amber accent glows.
- **Recharts**: Responsive visualization including Area charts (density trends), Line charts (cumulative flow throughput), Bar charts (category volume), and Pie charts (modal composition).
- **Video Player**: Seamless HTML5 video player with instant toggle between AI-annotated stream (with bounding boxes, trails, and HUD) and raw footage.
