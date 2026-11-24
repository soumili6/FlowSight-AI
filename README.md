# FlowSight AI — Intelligent Traffic Monitoring & Analytics System

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg)](https://tailwindcss.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6F00.svg)](https://ultralytics.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**FlowSight AI** is an AI-powered computer vision and traffic intelligence system developed as a portfolio-quality BTech CSE project. It ingests traffic video footage, performs real-time multi-class vehicle detection, tracks vehicles with ByteTrack, eliminates duplicate counts via virtual boundary triggers, calculates traffic densities, and classifies congestion levels (Low, Medium, High).

---

## Key Features

1. **Multi-Class Vehicle Detection**: Detects and classifies **Cars**, **Motorcycles**, **Buses**, and **Trucks** using Ultralytics YOLOv8.
2. **ByteTrack Vehicle Tracking**: Assigns persistent tracking IDs across frame occlusions and variable lighting.
3. **No-Duplicate Counting**: Uses virtual line crossing triggers with trajectory history to prevent repeatedly counting the same vehicle.
4. **Traffic Density Estimation**: Computes instantaneous and average vehicles per frame.
5. **Congestion Classification**: Automatically classifies traffic states into **Low**, **Medium**, or **High** using flow saturation and velocity proxies.
6. **Live Video Monitoring Interface**: Dual-mode video player with instant toggle between AI-annotated video (bounding boxes, trajectories, HUD) and raw footage.
7. **Comprehensive Recharts Analytics**:
   - Vehicle density trend over time (Area chart)
   - Cumulative throughput flow rate (Line chart)
   - Category distribution (Bar chart)
   - Modal share composition (Pie chart)
8. **Persistent SQLite Database**: Audits video metadata, aggregated metrics, and frame-level time series.
9. **Modern Dark-Navy UI**: Built with React, Vite, and Tailwind CSS.
10. **Built-in Demo Generator**: 1-click synthetic highway test generator for instant zero-config testing.

---

## Project Structure

```
FlowSight-AI/
├── backend/                  # FastAPI Application
│   ├── config.py             # Paths, model parameters, thresholds
│   ├── database.py           # SQLite connection & schema initialization
│   ├── models.py             # Internal data representations
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── crud.py               # SQLite database queries & mutations
│   ├── tracker.py            # YOLOv8 + ByteTrack computer vision engine
│   ├── video_processor.py    # Video pipeline & progress tracking
│   ├── sample_generator.py   # Synthetic highway video generator
│   ├── main.py               # FastAPI entrypoint & static mounts
│   └── routes/               # API route modules
│       ├── videos.py         # Video upload & management
│       ├── analysis.py       # Detection & tracking endpoints
│       ├── history.py        # Past analysis reports
│       └── stats.py          # Dashboard aggregate telemetry
├── frontend/                 # React + Vite + Tailwind CSS Application
│   ├── src/
│   │   ├── components/       # Sidebar, Navbar, MetricCard
│   │   ├── pages/            # Overview, Upload, Monitoring, Analytics, History
│   │   ├── services/api.js   # Axios REST client
│   │   ├── App.jsx           # Root layout & page router
│   │   ├── main.jsx          # React DOM entrypoint
│   │   └── index.css         # Tailwind & glassmorphism styles
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
├── database/                 # SQLite database files (flowsight.db)
├── models/                   # Pretrained weights (yolov8n.pt)
├── traffic_videos/           # Video storage
│   ├── uploads/              # Uploaded user videos
│   ├── processed/            # Annotated video outputs
│   └── samples/              # Synthetic test videos
├── documentation/            # Detailed documentation
│   ├── architecture.md       # Full architecture diagram & design
│   ├── api_spec.md           # REST API endpoints & schemas
│   └── user_guide.md         # Step-by-step user manual
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

---

## Getting Started

### 1. Start the Backend

```powershell
# From the project root with the virtual environment activated:
.\venv\Scripts\Activate.ps1

# Run the FastAPI server:
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend

```powershell
# Open a new terminal in the frontend directory:
cd frontend

# Install dependencies (if not already done):
npm install

# Start Vite dev server:
npm run dev
```
- Dashboard URL: `http://127.0.0.1:5173`

---

## Technical Highlights

- **Edge-Ready AI**: Uses YOLOv8 nano model with CPU optimization (~30–50 ms/frame on modern CPUs).
- **Trajectory Interpolation**: Bounding boxes feature corner accents, smooth centroid trajectory trails, and class-specific color badges.
- **RESTful Clean Architecture**: Modular separation between computer vision trackers, asynchronous job runners, SQLite transactions, and frontend components.

---

## License
MIT License. Created as an intermediate-level portfolio CSE project.
