"""
Documentation API routes.
"""
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.repo_models import Repository
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/{repo_id}")
async def get_documentation(
    repo_id: str,
    section: str = Query("all", description="Section: all | readme | architecture | api | onboarding | installation | learning_path | folder_guide"),
    db: AsyncSession = Depends(get_db),
):
    """Get generated documentation for a repository."""
    result = await db.execute(select(Repository).where(Repository.id == repo_id))
    repo = result.scalar_one_or_none()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repo.status != "complete":
        raise HTTPException(status_code=202, detail="Analysis still in progress")

    docs = json.loads(repo.documentation) if repo.documentation else {}

    if section == "all":
        return docs
    elif section in docs:
        return {"section": section, "content": docs[section]}
    else:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
