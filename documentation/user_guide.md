# FlowSight AI — User & Developer Guide

## Introduction
**FlowSight AI** is an intelligent traffic monitoring application designed for traffic engineers, smart city researchers, and computer vision analysts. It automates vehicle counting, multi-class categorization, and congestion detection from traffic surveillance video feeds.

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.12 (with active virtual environment)
- Node.js (v18+ or v20+) and npm
- Windows 10/11, Linux, or macOS

### 2. Starting the Backend Server
1. Open a terminal in the project root:
   ```bash
   cd FlowSight-AI
   ```
2. Activate your Python 3.12 virtual environment:
   - On Windows:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
3. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. Verify backend is running by opening:
   `http://127.0.0.1:8000/docs` (Swagger UI) or `http://127.0.0.1:8000/api/health`

---

### 3. Starting the Frontend Dashboard
1. Open a second terminal window:
   ```bash
   cd FlowSight-AI/frontend
   ```
2. Install dependencies (if not already installed):
   ```bash
   npm install
   ```
3. Launch the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to:
   `http://127.0.0.1:5173`

---

## Dashboard Walkthrough

### 1. Overview Page
- Displays system-wide telemetry: total videos analyzed, cumulative unique vehicle count, average traffic density, and congestion incident count.
- Shows modal volume breakdown for **Cars**, **Motorcycles**, **Buses**, and **Trucks**.
- If no video has been analyzed, click **"Load Demo Highway Video"** for a 1-click end-to-end demo.

### 2. Video Upload Page
- **Drag-and-Drop Ingestion**: Upload any `.mp4`, `.avi`, `.mov`, `.mkv` video.
- **Virtual Counting Line Slider**: Adjust the horizontal trigger position (from 20% to 80% screen height) to match the roadway perspective.
- **Processing Stride**: Choose Stride 1 for max precision or Stride 2/3 for faster processing of long footage.
- **Live Progress**: Displays real-time frame progress percentage during inference.

### 3. Live Monitoring Page
- **Player View Toggle**: Switch instantly between **Annotated AI View** (with corner bounding boxes, class labels, confidence scores, trajectory trails, and HUD banner) and **Raw Camera View**.
- **Real-Time Telemetry Cards**: Inspect total vehicles passed, peak density, average density, and congestion score.
- **AI Executive Summary**: View automated natural language narrative detailing observed flow dynamics.

### 4. Analytics Page
- **Active Vehicle Density Over Time**: Area chart displaying fluctuating vehicle presence across video duration.
- **Cumulative Traffic Throughput**: Line chart tracking cumulative vehicle arrivals across the virtual detection boundary.
- **Volume by Category**: Bar chart comparing counts across Cars, Motorcycles, Buses, and Trucks.
- **Composition Share**: Donut pie chart representing modal share percentages.

### 5. History Page
- Searchable and filterable archive of all previous video runs.
- Instant 1-click access to replay annotated monitoring or view full analytics.
- Ability to delete old sessions.
