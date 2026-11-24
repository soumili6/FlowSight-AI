import sqlite3
import json
from contextlib import contextmanager
from backend.config import DATABASE_PATH

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@contextmanager
def get_db():
    conn = sqlite3.connect(str(DATABASE_PATH), timeout=20.0)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes tables for videos, analysis results, and time series data."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Videos Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                processed_path TEXT,
                file_size_bytes INTEGER NOT NULL,
                fps REAL DEFAULT 0,
                total_frames INTEGER DEFAULT 0,
                width INTEGER DEFAULT 0,
                height INTEGER DEFAULT 0,
                duration_seconds REAL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'uploaded', -- uploaded, processing, completed, failed
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Analysis Results Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                video_id TEXT NOT NULL,
                total_vehicles_counted INTEGER DEFAULT 0,
                car_count INTEGER DEFAULT 0,
                motorcycle_count INTEGER DEFAULT 0,
                bus_count INTEGER DEFAULT 0,
                truck_count INTEGER DEFAULT 0,
                peak_density REAL DEFAULT 0,
                average_density REAL DEFAULT 0,
                congestion_level TEXT DEFAULT 'Low', -- Low, Medium, High
                congestion_score REAL DEFAULT 0, -- 0 - 100%
                processing_time_seconds REAL DEFAULT 0,
                total_frames_analyzed INTEGER DEFAULT 0,
                counting_method TEXT DEFAULT 'virtual_line',
                status TEXT NOT NULL DEFAULT 'completed',
                summary_insights TEXT, -- AI summary text
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
            )
        """)

        # Time Series / Frame Metrics Table (for Recharts graphs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id TEXT NOT NULL,
                timestamp_sec REAL NOT NULL,
                frame_number INTEGER NOT NULL,
                active_vehicles INTEGER DEFAULT 0,
                cumulative_count INTEGER DEFAULT 0,
                car_count INTEGER DEFAULT 0,
                motorcycle_count INTEGER DEFAULT 0,
                bus_count INTEGER DEFAULT 0,
                truck_count INTEGER DEFAULT 0,
                density REAL DEFAULT 0,
                congestion_level TEXT DEFAULT 'Low',
                FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
            )
        """)

        # Indices for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_created ON videos(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_video_id ON analyses(video_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_created ON analyses(created_at DESC);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_analysis ON analysis_timeline(analysis_id, timestamp_sec);")
