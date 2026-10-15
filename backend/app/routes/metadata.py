from fastapi import APIRouter, Query, HTTPException
from app.models import SnapshotMetadata
from app.services.metadata_service import MetadataService

router = APIRouter(prefix="/api", tags=["metadata"])

@router.get("/metadata", response_model=SnapshotMetadata)
async def get_metadata(
    url: str = Query(..., description="Target website URL"),
    timestamp: str = Query(..., description="Wayback capture timestamp YYYYMMDDHHMMSS")
):
    """
    Get or compute structural and complexity metadata for a snapshot.
    Computes HTML size, DOM node count, image count, external resources count,
    mobile viewport detection, and detected framework signals.
    Results are cached indefinitely in SQLite.
    """
    if not url or not timestamp:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_PARAMS", "message": "Both url and timestamp are required."}}
        )

    metadata = await MetadataService.get_or_compute_metadata(url, timestamp)
    return metadata
