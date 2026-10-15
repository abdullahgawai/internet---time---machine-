import os
import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager

# Database file location
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "time_machine.db"))

SCHEMA_SQL = """
-- Cached list of snapshots per URL
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    timestamp TEXT NOT NULL,        -- Wayback timestamp format: YYYYMMDDHHMMSS
    status_code INTEGER,
    mimetype TEXT,
    length INTEGER,
    fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url, timestamp)
);

-- Index for fast URL lookups and sorting by timestamp
CREATE INDEX IF NOT EXISTS idx_snapshots_url_ts ON snapshots(url, timestamp);

-- Snapshot cache metadata for TTL tracking (7 days TTL)
CREATE TABLE IF NOT EXISTS snapshot_cache_meta (
    url TEXT PRIMARY KEY,
    last_fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_count INTEGER DEFAULT 0
);

-- Computed metadata/complexity per snapshot
CREATE TABLE IF NOT EXISTS snapshot_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER REFERENCES snapshots(id),
    url TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    html_size_bytes INTEGER,
    dom_node_count INTEGER,
    image_count INTEGER,
    external_resource_count INTEGER,
    has_mobile_viewport BOOLEAN,
    detected_frameworks TEXT,       -- JSON array, best-effort signal detection
    computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url, timestamp)
);

CREATE INDEX IF NOT EXISTS idx_metadata_url_ts ON snapshot_metadata(url, timestamp);

-- AI-generated comparison results (v2 stubbed schema)
CREATE TABLE IF NOT EXISTS ai_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    timestamp_a TEXT NOT NULL,
    timestamp_b TEXT NOT NULL,
    summary_text TEXT,
    change_categories TEXT,         -- JSON array e.g. ["layout","color","navigation"]
    visual_diff_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url, timestamp_a, timestamp_b)
);

-- Overall evolution score per URL (v2 stubbed schema)
CREATE TABLE IF NOT EXISTS evolution_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    score REAL,
    redesign_events TEXT,           -- JSON array of {timestamp, description}
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

async def init_db():
    """Initialize database tables and indexes."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()

@asynccontextmanager
async def get_db():
    """Async generator providing a connection to the SQLite database with Row factory."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
