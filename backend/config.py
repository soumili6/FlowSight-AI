import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "flowsight.db"
TRAFFIC_VIDEOS_DIR = BASE_DIR / "traffic_videos"
UPLOAD_DIR = TRAFFIC_VIDEOS_DIR / "uploads"
PROCESSED_DIR = TRAFFIC_VIDEOS_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
DOCS_DIR = BASE_DIR / "documentation"

# Ensure all directories exist
for folder in [DATABASE_DIR, UPLOAD_DIR, PROCESSED_DIR, MODELS_DIR, DOCS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Ultralytics Config Dir override to avoid permission warnings on Windows
os.environ["YOLO_CONFIG_DIR"] = str(BASE_DIR / ".ultralytics")
(BASE_DIR / ".ultralytics").mkdir(exist_ok=True)

# YOLO and Computer Vision Settings
YOLO_MODEL_NAME = "yolov8n.pt"
YOLO_MODEL_PATH = MODELS_DIR / YOLO_MODEL_NAME

# COCO Vehicle Classes:
# 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASS_IDS = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

# Detection & Tracking Config
CONFIDENCE_THRESHOLD = 0.35
IOU_THRESHOLD = 0.45
TRACKER_TYPE = "bytetrack.yaml"

# Traffic Density Thresholds (average vehicles detected per frame)
DENSITY_LOW_THRESHOLD = 4.0      # < 4: Low
DENSITY_MEDIUM_THRESHOLD = 10.0  # 4 - 10: Medium, > 10: High

# Congestion Thresholds
CONGESTION_LEVELS = {
    "LOW": "Low",
    "MEDIUM": "Medium",
    "HIGH": "High",
}

# API Config
HOST = "127.0.0.1"
PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]
