"""
Repository API routes: CRUD operations and analysis trigger.
"""
import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db
from app.models.repo_models import Repository
from app.services.clone_service import validate_github_url, normalize_url, clone_repository
from app.services.analysis_service import run_full_analysis
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ── Request / Response Schemas ─────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    url: str


class RepoBasicResponse(BaseModel):
    id: str
    url: str
    name: str
    owner: str
    description: Optional[str]
    status: str
    progress: int
    progress_message: str
    total_files: int
    total_folders: int
    total_lines: int
    repo_size_mb: float
    created_at: str
    analyzed_at: Optional[str]


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/analyze")
async def analyze_repository(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Validate and clone a GitHub repository, then start background analysis.
    Returns immediately with repo_id — frontend polls /repos/{id}/status.
    """
    raw_url = request.url.strip()

    # Validate URL
    is_valid, owner, repo_name = validate_github_url(raw_url)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub URL. Expected format: https://github.com/owner/repo",
        )

    # Normalize to canonical format so that e.g. .git suffix,
    # http vs https, and /tree/main variants all resolve to the same entry
    url = normalize_url(raw_url)

    # Check if already analyzed
    result = await db.execute(select(Repository).where(Repository.url == url))
    existing = result.scalar_one_or_none()

    if existing:
        # If complete or analyzing, return existing
        if existing.status in ("complete", "analyzing"):
            return {"repo_id": existing.id, "status": existing.status, "message": "Already analyzed or in progress"}

        # If error, allow re-analysis by resetting status
        existing.status = "pending"
        existing.progress = 0
        existing.progress_message = "Re-starting analysis..."
        existing.error_message = None
        await db.commit()

        background_tasks.add_task(run_full_analysis, existing.id, existing.clone_path)
        return {"repo_id": existing.id, "status": "analyzing", "message": "Re-analysis started"}

    # Clone the repository (blocking — usually fast for shallow clone)
    try:
        clone_path, metadata = clone_repository(url, owner, repo_name)
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Create DB record
    repo = Repository(
        url=url,
        name=repo_name,
        owner=owner,
        description=metadata.get("description", ""),
        default_branch=metadata.get("default_branch", "main"),
        clone_path=str(clone_path),
        status="analyzing",
        progress=2,
        progress_message="Repository cloned. Starting analysis...",
    )
    db.add(repo)
    await db.commit()
    await db.refresh(repo)

    # Start background analysis
    background_tasks.add_task(run_full_analysis, repo.id, repo.clone_path)

    logger.info(f"Analysis started for {owner}/{repo_name} (id={repo.id})")
    return {
        "repo_id": repo.id,
        "status": "analyzing",
        "message": f"Cloned {owner}/{repo_name}. Analysis running in background.",
    }


@router.get("/")
async def list_repositories(db: AsyncSession = Depends(get_db)):
    """List all analyzed repositories."""
    result = await db.execute(select(Repository).order_by(Repository.created_at.desc()))
    repos = result.scalars().all()
    return [_repo_to_basic(r) for r in repos]


@router.get("/{repo_id}/status")
async def get_status(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Poll analysis progress."""
    repo = await _get_repo_or_404(repo_id, db)
    return {
        "status": repo.status,
        "progress": repo.progress,
        "message": repo.progress_message,
        "error": repo.error_message,
    }


@router.get("/{repo_id}")
async def get_repository(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get full repository metadata and summary."""
    repo = await _get_repo_or_404(repo_id, db)
    data = _repo_to_basic(repo)
    if repo.tech_stack:
        data["tech_stack"] = json.loads(repo.tech_stack)
    if repo.summary:
        data["summary"] = json.loads(repo.summary)
    if repo.health_score:
        data["health_score"] = json.loads(repo.health_score)
    if repo.learning_path:
        data["learning_path"] = json.loads(repo.learning_path)
    return data


@router.get("/{repo_id}/tree")
async def get_tree(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get the repository file tree."""
    repo = await _get_repo_or_404(repo_id, db)
    _require_complete(repo)
    return json.loads(repo.file_tree) if repo.file_tree else {}


@router.get("/{repo_id}/file")
async def get_file_analysis(
    repo_id: str,
    path: str = Query(..., description="Relative file path"),
    db: AsyncSession = Depends(get_db),
):
    """Get analysis for a specific file."""
    repo = await _get_repo_or_404(repo_id, db)
    _require_complete(repo)
    analyses = json.loads(repo.file_analyses) if repo.file_analyses else {}
    if path not in analyses:
        raise HTTPException(status_code=404, detail=f"File '{path}' not found in analysis")
    return analyses[path]


@router.get("/{repo_id}/tech")
async def get_tech_stack(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get detected technology stack."""
    repo = await _get_repo_or_404(repo_id, db)
    _require_complete(repo)
    return json.loads(repo.tech_stack) if repo.tech_stack else {}


@router.get("/{repo_id}/security")
async def get_security(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get security analysis findings."""
    repo = await _get_repo_or_404(repo_id, db)
    _require_complete(repo)
    return json.loads(repo.security_findings) if repo.security_findings else {}


@router.get("/{repo_id}/quality")
async def get_quality(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get code quality report."""
    repo = await _get_repo_or_404(repo_id, db)
    _require_complete(repo)
    return json.loads(repo.quality_report) if repo.quality_report else {}


@router.get("/{repo_id}/health")
async def get_health(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get repository health scores."""
    repo = await _get_repo_or_404(repo_id, db)
    _require_complete(repo)
    return json.loads(repo.health_score) if repo.health_score else {}


@router.get("/{repo_id}/architecture")
async def get_architecture(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Get architecture analysis and Mermaid diagrams."""
    repo = await _get_repo_or_404(repo_id, db)
    _require_complete(repo)
    return json.loads(repo.architecture) if repo.architecture else {}


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a repository and its analysis data."""
    repo = await _get_repo_or_404(repo_id, db)
    await db.execute(delete(Repository).where(Repository.id == repo_id))
    await db.commit()
    return {"message": f"Repository {repo_id} deleted"}


# ── Helpers ────────────────────────────────────────────────────────────────

async def _get_repo_or_404(repo_id: str, db: AsyncSession) -> Repository:
    result = await db.execute(select(Repository).where(Repository.id == repo_id))
    repo = result.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    return repo


def _require_complete(repo: Repository):
    if repo.status != "complete":
        raise HTTPException(
            status_code=202,
            detail=f"Analysis in progress ({repo.progress}%). Status: {repo.status}",
        )


def _repo_to_basic(repo: Repository) -> dict:
    return {
        "id": repo.id,
        "url": repo.url,
        "name": repo.name,
        "owner": repo.owner,
        "description": repo.description or "",
        "default_branch": repo.default_branch,
        "status": repo.status,
        "progress": repo.progress,
        "progress_message": repo.progress_message,
        "error_message": repo.error_message,
        "total_files": repo.total_files,
        "total_folders": repo.total_folders,
        "total_lines": repo.total_lines,
        "repo_size_mb": repo.repo_size_mb,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
        "analyzed_at": repo.analyzed_at.isoformat() if repo.analyzed_at else None,
    }
