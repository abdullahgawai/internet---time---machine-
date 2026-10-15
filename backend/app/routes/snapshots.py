from fastapi import APIRouter, Query, HTTPException
from app.models import SnapshotsResponse, SnapshotItem
from app.services.cdx_service import CDXService

router = APIRouter(prefix="/api", tags=["snapshots"])

@router.get("/snapshots", response_model=SnapshotsResponse)
async def get_snapshots(
    url: str = Query(..., description="Target website domain or URL e.g. apple.com")
):
    """
    Retrieve historical snapshots for a given website URL.
    Results are cached in SQLite with a 7-day TTL and grouped by year with capture density.
    """
    if not url or not url.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_URL", "message": "URL parameter cannot be empty."}}
        )

    response = await CDXService.fetch_snapshots(url)
    return response

@router.get("/snapshot", response_model=SnapshotItem)
async def get_single_snapshot(
    url: str = Query(..., description="Target website domain or URL"),
    timestamp: str = Query(..., description="Target timestamp YYYYMMDDHHMMSS or year YYYY")
):
    """
    Get the single closest snapshot to a specified date or year.
    """
    if not url or not url.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_URL", "message": "URL parameter cannot be empty."}}
        )

    item = await CDXService.get_nearest_snapshot(url, timestamp)
    if not item:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": f"No snapshot found near timestamp {timestamp}."}}
        )

    return item
