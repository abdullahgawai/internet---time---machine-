import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes.snapshots import router as snapshots_router
from app.routes.metadata import router as metadata_router
from app.routes.compare import router as compare_router
from app.routes.stubs import router as stubs_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("internet-time-machine")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    logger.info("Initializing SQLite database...")
    await init_db()
    logger.info("Database initialized successfully.")
    yield
    # Shutdown
    logger.info("Shutting down Internet Time Machine Backend.")

app = FastAPI(
    title="Internet Time Machine API",
    description="Digital archaeology backend powered by the Wayback Machine CDX API, with SQLite caching and DOM complexity analytics.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handler to guarantee consistent error response schema:
# {"error": {"code": "...", "message": "..."}}
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(detail)}}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred."}}
    )

# Mount API routers
app.include_router(snapshots_router)
app.include_router(metadata_router)
app.include_router(compare_router)
app.include_router(stubs_router)

@app.get("/")
async def root():
    return {
        "name": "Internet Time Machine API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
