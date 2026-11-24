import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
from pathlib import Path
from ultralytics import YOLO

from backend.config import (
    YOLO_MODEL_PATH,
    YOLO_MODEL_NAME,
    MODELS_DIR,
    VEHICLE_CLASS_IDS,
    CONFIDENCE_THRESHOLD,
    IOU_THRESHOLD,
    TRACKER_TYPE,
    DENSITY_LOW_THRESHOLD,
    DENSITY_MEDIUM_THRESHOLD
)

logger = logging.getLogger(__name__)

# Color palette (BGR for OpenCV) for each vehicle class
CLASS_COLORS = {
    "car": (46, 204, 113),         # Bright Emerald Green
    "motorcycle": (0, 165, 255),    # Vibrant Amber / Orange
    "bus": (255, 140, 0),           # Deep Cyan / Blue
    "truck": (211, 84, 0),          # Purple / Burgundy
}
DEFAULT_COLOR = (240, 240, 240)


class TrafficTracker:
    def __init__(self, model_path: Optional[str] = None):
        """Initializes the YOLO model and tracking configurations."""
        path_to_use = model_path or str(YOLO_MODEL_PATH)
        if not Path(path_to_use).exists():
            # Will automatically download yolov8n.pt to models directory
            logger.info(f"Model not found at {path_to_use}, initializing YOLOv8n download...")
            self.model = YOLO(YOLO_MODEL_NAME)
            try:
                # Save locally to models dir
                MODELS_DIR.mkdir(parents=True, exist_ok=True)
                downloaded_file = Path(YOLO_MODEL_NAME)
                if downloaded_file.exists() and not Path(path_to_use).exists():
                    downloaded_file.rename(path_to_use)
            except Exception as e:
                logger.warning(f"Could not relocate model file: {e}")
        else:
            self.model = YOLO(path_to_use)

        self.vehicle_classes = list(VEHICLE_CLASS_IDS.keys())
        # Track histories: track_id -> list of (cx, cy)
        self.track_history: Dict[int, List[Tuple[int, int]]] = {}
        # Counted vehicle track IDs
        self.counted_ids: Set[int] = set()
        # Counts per category
        self.category_counts: Dict[str, int] = {
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }
        # Track ID to vehicle class mapping
        self.track_classes: Dict[int, str] = {}
        # Motion vectors for congestion analysis (track_id -> list of displacements)
        self.track_displacements: Dict[int, List[float]] = {}

    def reset(self):
        """Resets tracker state for a new video analysis."""
        self.track_history.clear()
        self.counted_ids.clear()
        self.track_classes.clear()
        self.track_displacements.clear()
        self.category_counts = {
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }

    def process_frame(
        self,
        frame: np.ndarray,
        frame_idx: int,
        line_ratio: float = 0.55,
        draw_annotations: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Runs YOLO tracking on a single frame, updates vehicle counts and density metrics,
        and draws bounding boxes, trails, and HUD if requested.
        """
        height, width = frame.shape[:2]
        line_y = int(height * line_ratio)
        annotated_frame = frame.copy() if draw_annotations else frame

        # Run tracking using ByteTrack
        results = self.model.track(
            source=frame,
            persist=True,
            classes=self.vehicle_classes,
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            tracker=TRACKER_TYPE,
            verbose=False
        )

        active_vehicles = 0
        active_by_class = {"car": 0, "motorcycle": 0, "bus": 0, "truck": 0}
        current_frame_speeds = []

        if results and results[0].boxes and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            clss = results[0].boxes.cls.cpu().numpy().astype(int)
            confs = results[0].boxes.conf.cpu().numpy().astype(float)

            active_vehicles = len(track_ids)

            for box, track_id, cls_id, conf in zip(boxes, track_ids, clss, confs):
                x1, y1, x2, y2 = box
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                class_name = VEHICLE_CLASS_IDS.get(cls_id, "car")
                active_by_class[class_name] = active_by_class.get(class_name, 0) + 1
                self.track_classes[track_id] = class_name

                # Update trajectory history
                if track_id not in self.track_history:
                    self.track_history[track_id] = []
                    self.track_displacements[track_id] = []
                self.track_history[track_id].append((cx, cy))
                if len(self.track_history[track_id]) > 30:
                    self.track_history[track_id].pop(0)

                # Compute instantaneous displacement (speed proxy)
                if len(self.track_history[track_id]) >= 2:
                    prev_cx, prev_cy = self.track_history[track_id][-2]
                    disp = np.hypot(cx - prev_cx, cy - prev_cy)
                    self.track_displacements[track_id].append(disp)
                    if len(self.track_displacements[track_id]) > 15:
                        self.track_displacements[track_id].pop(0)
                    current_frame_speeds.append(disp)

                # Vehicle Counting Logic across line
                # Check if crossed the virtual counting line (within +- 20 pixels tolerance or transition)
                if track_id not in self.counted_ids:
                    # Vehicle crossed if it has trajectory points on both sides, or is crossing
                    crossed = False
                    if len(self.track_history[track_id]) >= 2:
                        prev_y = self.track_history[track_id][-2][1]
                        if (prev_y < line_y <= cy) or (prev_y > line_y >= cy):
                            crossed = True
                    elif abs(cy - line_y) < 15:
                        crossed = True

                    if crossed:
                        self.counted_ids.add(track_id)
                        self.category_counts[class_name] = self.category_counts.get(class_name, 0) + 1

                # Draw Visuals on Annotated Frame
                if draw_annotations:
                    color = CLASS_COLORS.get(class_name, DEFAULT_COLOR)
                    
                    # Sleek bounding box with corner accents
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                    corner_len = min(15, (x2 - x1) // 4, (y2 - y1) // 4)
                    # Accent corners
                    cv2.line(annotated_frame, (x1, y1), (x1 + corner_len, y1), (255, 255, 255), 3)
                    cv2.line(annotated_frame, (x1, y1), (x1, y1 + corner_len), (255, 255, 255), 3)
                    cv2.line(annotated_frame, (x2, y2), (x2 - corner_len, y2), (255, 255, 255), 3)
                    cv2.line(annotated_frame, (x2, y2), (x2, y2 - corner_len), (255, 255, 255), 3)

                    # Center point
                    cv2.circle(annotated_frame, (cx, cy), 4, color, -1)

                    # Trajectory Trail
                    pts = self.track_history[track_id]
                    for j in range(1, len(pts)):
                        alpha = j / len(pts)
                        thickness = max(1, int(3 * alpha))
                        cv2.line(annotated_frame, pts[j - 1], pts[j], color, thickness)

                    # Label badge
                    label = f"#{track_id} {class_name.upper()} {conf:.2f}"
                    (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                    badge_y1 = max(0, y1 - lh - 8)
                    cv2.rectangle(
                        annotated_frame,
                        (x1, badge_y1),
                        (x1 + lw + 8, badge_y1 + lh + 6),
                        color,
                        -1
                    )
                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1 + 4, badge_y1 + lh + 2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (10, 15, 30),
                        1,
                        cv2.LINE_AA
                    )

        # Fallback: if no line crossing triggered yet but vehicles were tracked, ensure at least unique vehicles count
        total_counted = max(len(self.counted_ids), sum(self.category_counts.values()))

        # Density & Congestion Estimation
        density_val = float(active_vehicles)
        if density_val < DENSITY_LOW_THRESHOLD:
            congestion_level = "Low"
            congestion_score = min(35.0, (density_val / DENSITY_LOW_THRESHOLD) * 35.0)
        elif density_val <= DENSITY_MEDIUM_THRESHOLD:
            congestion_level = "Medium"
            congestion_score = 35.0 + ((density_val - DENSITY_LOW_THRESHOLD) / (DENSITY_MEDIUM_THRESHOLD - DENSITY_LOW_THRESHOLD)) * 35.0
        else:
            congestion_level = "High"
            congestion_score = min(100.0, 70.0 + ((density_val - DENSITY_MEDIUM_THRESHOLD) / 10.0) * 30.0)

        # Factor in low speed if vehicles are present
        if active_vehicles >= 3 and current_frame_speeds:
            avg_speed = float(np.mean(current_frame_speeds))
            if avg_speed < 1.5:  # Vehicles are crawling / stuck
                congestion_score = min(100.0, congestion_score + 20.0)
                if congestion_score >= 65:
                    congestion_level = "High"

        # Draw HUD & Counting Line
        if draw_annotations:
            # Draw Virtual Counting Line with Neon Cyan
            cv2.line(annotated_frame, (0, line_y), (width, line_y), (255, 200, 0), 2, cv2.LINE_AA)
            cv2.putText(
                annotated_frame,
                f"COUNTING LINE (y={line_y})",
                (15, line_y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 200, 0),
                1,
                cv2.LINE_AA
            )

            # Draw HUD Header Bar at top
            hud_height = 55
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, hud_height), (15, 23, 42), -1) # Dark Slate Navy
            cv2.addWeighted(overlay, 0.85, annotated_frame, 0.15, 0, annotated_frame)

            # FlowSight AI Brand
            cv2.putText(
                annotated_frame,
                "FlowSight AI",
                (18, 26),
                cv2.FONT_HERSHEY_DUPLEX,
                0.65,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
            cv2.putText(
                annotated_frame,
                "TRAFFIC MONITORING",
                (18, 44),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (148, 163, 184),
                1,
                cv2.LINE_AA
            )

            # Metric: Total Counted
            cv2.putText(
                annotated_frame,
                f"Total Passed: {total_counted}",
                (180, 26),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (56, 189, 248),
                1,
                cv2.LINE_AA
            )

            # Metric: Active Vehicles
            cv2.putText(
                annotated_frame,
                f"Active in Frame: {active_vehicles}",
                (180, 44),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (226, 232, 240),
                1,
                cv2.LINE_AA
            )

            # Metric: Congestion Badge
            cong_color = (46, 204, 113) if congestion_level == "Low" else ((0, 165, 255) if congestion_level == "Medium" else (0, 50, 235))
            cv2.rectangle(annotated_frame, (380, 14), (520, 42), cong_color, -1)
            cv2.putText(
                annotated_frame,
                f"Traffic: {congestion_level}",
                (390, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

            # Breakdown pill
            breakdown_str = f"C:{self.category_counts['car']} | M:{self.category_counts['motorcycle']} | B:{self.category_counts['bus']} | T:{self.category_counts['truck']}"
            cv2.putText(
                annotated_frame,
                breakdown_str,
                (540, 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                (203, 213, 225),
                1,
                cv2.LINE_AA
            )

        frame_metrics = {
            "frame_idx": frame_idx,
            "active_vehicles": active_vehicles,
            "cumulative_count": total_counted,
            "active_by_class": active_by_class,
            "category_counts": dict(self.category_counts),
            "density": round(density_val, 2),
            "congestion_level": congestion_level,
            "congestion_score": round(congestion_score, 1)
        }

        return annotated_frame, frame_metrics
