"""
RepoMind AI Backend
Entry point for the FastAPI application.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.api import repos, chat, docs_router
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("[START] Starting RepoMind AI Backend...")

    # Initialize the database
    await init_db()
    logger.info("[OK] Database initialized")

    # Create required directories
    settings.repos_dir.mkdir(parents=True, exist_ok=True)
    settings.indices_dir.mkdir(parents=True, exist_ok=True)
    logger.info("[OK] Directories ready")

    # Check Ollama availability (non-blocking)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_url}/api/tags")
            if resp.status_code == 200:
                logger.info(f"[OK] Ollama connected at {settings.ollama_url}")
            else:
                logger.warning("[WARN] Ollama responded with unexpected status - AI features may be limited")
    except Exception:
        logger.warning("[WARN] Ollama not reachable - AI chat features disabled. Start Ollama to enable them.")

    yield

    logger.info("[STOP] Shutting down RepoMind AI Backend...")


app = FastAPI(
    title="RepoMind AI",
    description="AI-powered GitHub repository analysis platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Vite dev server and any local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(repos.router, prefix="/api/repos", tags=["repositories"])
app.include_router(chat.router, prefix="/api/chat", tags=["ai-chat"])
app.include_router(docs_router.router, prefix="/api/docs", tags=["documentation"])


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "app": "RepoMind AI", "version": "1.0.0"}


@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint used by frontend."""
    ollama_ok = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.ollama_url}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    return {
        "status": "ok",
        "ollama": ollama_ok,
        "ollama_url": settings.ollama_url,
        "model": settings.ollama_model,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )
