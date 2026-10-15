from typing import List, Optional
from pydantic import BaseModel, Field

class SnapshotItem(BaseModel):
    timestamp: str = Field(..., description="Wayback 14-digit timestamp YYYYMMDDHHMMSS")
    year: int = Field(..., description="Snapshot calendar year")
    date: str = Field(..., description="Human readable date YYYY-MM-DD HH:MM:SS")
    status_code: Optional[int] = Field(default=200, description="HTTP status code at capture time")
    mimetype: Optional[str] = Field(default="text/html", description="MIME type")
    length: Optional[int] = Field(default=None, description="Reported archive byte length")
    playback_url: str = Field(..., description="Standard Wayback playback URL with banner")
    clean_playback_url: str = Field(..., description="Raw Wayback playback URL (id_) suitable for iframe embedding")

class YearDensity(BaseModel):
    year: int
    count: int
    first_timestamp: Optional[str] = None
    last_timestamp: Optional[str] = None
    representative_timestamp: Optional[str] = None

class SnapshotsResponse(BaseModel):
    url: str
    normalized_url: str
    total_snapshots: int
    years: List[YearDensity]
    snapshots: List[SnapshotItem]
    cached: bool
    message: Optional[str] = None

class SnapshotMetadata(BaseModel):
    url: str
    timestamp: str
    playback_url: str
    clean_playback_url: str
    html_size_bytes: int
    dom_node_count: int
    image_count: int
    external_resource_count: int
    has_mobile_viewport: bool
    detected_frameworks: List[str]
    computed_at: Optional[str] = None

class MetadataDiff(BaseModel):
    ts1: str
    ts2: str
    html_size_delta: int
    html_size_change_pct: float
    dom_node_delta: int
    image_count_delta: int
    external_resource_delta: int
    mobile_viewport_transition: str
    frameworks_added: List[str]
    frameworks_removed: List[str]

class CompareResponse(BaseModel):
    url: str
    snapshot_a: SnapshotMetadata
    snapshot_b: SnapshotMetadata
    diff: MetadataDiff

class AnalyzeRequest(BaseModel):
    url: str
    ts1: str
    ts2: str

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    error: ErrorDetail
