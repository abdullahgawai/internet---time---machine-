from fastapi import APIRouter, HTTPException, Query
from app.models import AnalyzeRequest

router = APIRouter(prefix="/api", tags=["ai-stubs"])

@router.post("/analyze")
async def analyze_comparison(body: AnalyzeRequest):
    """
    [Phase 2/3 AI Feature Stub]
    Triggers headless screenshot capture (Playwright) and AI vision comparison.
    Currently stubbed with 501 Not Implemented.
    """
    raise HTTPException(
        status_code=501,
        detail={
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "AI vision analysis is planned for Phase 2. Structural metadata diff is available via /api/compare."
            }
        }
    )

@router.get("/evolution-score")
async def get_evolution_score(url: str = Query(..., description="Target website URL")):
    """
    [Phase 2/3 AI Feature Stub]
    Computes holistic 0-100 site evolution score across historical redesign events.
    Currently stubbed with 501 Not Implemented.
    """
    raise HTTPException(
        status_code=501,
        detail={
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "Evolution score engine is scheduled for Phase 2/3."
            }
        }
    )

@router.get("/report/{report_id}")
async def get_report(report_id: str):
    """
    [Phase 2/3 AI Feature Stub]
    Fetches pre-rendered shareable digital archaeology report.
    Currently stubbed with 501 Not Implemented.
    """
    raise HTTPException(
        status_code=501,
        detail={
            "error": {
                "code": "NOT_IMPLEMENTED",
                "message": "Shareable evolution reports are planned for Phase 4."
            }
        }
    )
