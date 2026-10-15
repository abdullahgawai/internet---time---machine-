import asyncio
from fastapi import APIRouter, Query, HTTPException
from app.models import CompareResponse
from app.services.metadata_service import MetadataService
from app.services.diff_service import DiffService

router = APIRouter(prefix="/api", tags=["compare"])

@router.get("/compare", response_model=CompareResponse)
async def compare_snapshots(
    url: str = Query(..., description="Target website URL"),
    ts1: str = Query(..., description="Timestamp for snapshot A (YYYYMMDDHHMMSS)"),
    ts2: str = Query(..., description="Timestamp for snapshot B (YYYYMMDDHHMMSS)")
):
    """
    Compare two snapshots of a website. Computes complexity metadata for both eras
    and returns the structural delta (DOM size, byte size, image counts, mobile readiness, frameworks).
    """
    if not url or not ts1 or not ts2:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "INVALID_PARAMS", "message": "url, ts1, and ts2 are required."}}
        )

    # Fetch metadata for both snapshots concurrently
    meta_a, meta_b = await asyncio.gather(
        MetadataService.get_or_compute_metadata(url, ts1),
        MetadataService.get_or_compute_metadata(url, ts2)
    )

    diff = DiffService.compute_diff(meta_a, meta_b)

    return CompareResponse(
        url=url,
        snapshot_a=meta_a,
        snapshot_b=meta_b,
        diff=diff
    )
