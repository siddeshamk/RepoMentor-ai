"""
AI Chat API: streaming endpoint using Server-Sent Events (SSE).
"""
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.repo_models import Repository
from app.ai.qa_engine import qa_engine
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    repo_id: str
    question: str


@router.post("/stream")
async def chat_stream(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Streaming AI chat endpoint using Server-Sent Events.
    The frontend reads this as an EventSource stream.
    """
    # Validate repo exists and is complete
    result = await db.execute(select(Repository).where(Repository.id == request.repo_id))
    repo = result.scalar_one_or_none()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repo.status != "complete":
        raise HTTPException(status_code=202, detail="Analysis still in progress")

    # Build repo_meta for the QA engine
    repo_meta = {
        "name": repo.name,
        "owner": repo.owner,
        "description": repo.description,
        "tech_stack": json.loads(repo.tech_stack) if repo.tech_stack else {},
    }

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    async def event_generator():
        """Yield SSE-formatted tokens."""
        try:
            async for token in qa_engine.answer_stream(question, request.repo_id, repo_meta):
                # SSE format: "data: <content>\n\n"
                # Escape newlines in token for SSE compliance
                safe_token = token.replace("\n", "\\n")
                yield f"data: {safe_token}\n\n"
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"data: ❌ Error: {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/")
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Non-streaming chat endpoint (for simpler clients).
    Returns the full response at once.
    """
    result = await db.execute(select(Repository).where(Repository.id == request.repo_id))
    repo = result.scalar_one_or_none()

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    if repo.status != "complete":
        raise HTTPException(status_code=202, detail="Analysis still in progress")

    repo_meta = {
        "name": repo.name,
        "owner": repo.owner,
        "description": repo.description,
        "tech_stack": json.loads(repo.tech_stack) if repo.tech_stack else {},
    }

    answer = await qa_engine.answer(request.question, request.repo_id, repo_meta)
    return {"answer": answer, "repo_id": request.repo_id}
