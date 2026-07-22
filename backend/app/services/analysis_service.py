"""
Analysis service: orchestrates the full analysis pipeline for a repository.
Runs all analyzers in sequence, updates progress in the database.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import AsyncSessionLocal
from app.models.repo_models import Repository
from app.analyzers import tech_detector, tree_builder, file_analyzer, security_analyzer, quality_analyzer, health_scorer
from app.generators import doc_generator, mermaid_generator
from app.ai.vector_store import VectorStore, prepare_repo_chunks
from app.utils.file_utils import walk_repo, get_relative_path
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


async def _update_progress(repo_id: str, progress: int, message: str, status: str = "analyzing"):
    """Update analysis progress in the database."""
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(Repository)
            .where(Repository.id == repo_id)
            .values(progress=progress, progress_message=message, status=status)
        )
        await db.commit()


async def run_full_analysis(repo_id: str, clone_path: str):
    """
    Full analysis pipeline. Runs in a background task.
    Updates progress periodically so the frontend can poll for status.
    """
    repo_path = Path(clone_path)
    logger.info(f"Starting full analysis for repo {repo_id} at {repo_path}")

    try:
        # Phase 1: Build tree
        await _update_progress(repo_id, 5, "Building repository tree...")
        tree_data = tree_builder.build_tree(repo_path)
        stats = tree_data.get("stats", {})

        # Phase 2: Detect technologies
        await _update_progress(repo_id, 15, "Detecting technologies and frameworks...")
        tech_data = tech_detector.detect_technologies(repo_path)
        logger.info(f"Primary language: {tech_data.get('primary_language')}")

        # Phase 3: Analyze files
        await _update_progress(repo_id, 25, "Analyzing source files...")
        all_files = list(walk_repo(repo_path, max_files=settings.max_files_to_analyze))
        file_analyses: dict[str, Any] = {}

        total = len(all_files)
        for i, file_path in enumerate(all_files):
            rel_path = get_relative_path(file_path, repo_path)
            analysis = file_analyzer.analyze_file(file_path, repo_path)
            file_analyses[rel_path] = analysis

            # Update progress every 50 files
            if i % 50 == 0:
                prog = 25 + int((i / max(total, 1)) * 20)
                await _update_progress(repo_id, prog, f"Analyzed {i}/{total} files...")

        await _update_progress(repo_id, 46, f"Analyzed all {total} files.")

        # Phase 4: Security analysis
        await _update_progress(repo_id, 50, "Running security analysis...")
        security_data = security_analyzer.analyze_security(repo_path)
        logger.info(f"Security: {security_data.get('total', 0)} findings")

        # Phase 5: Code quality
        await _update_progress(repo_id, 60, "Analyzing code quality...")
        quality_data = quality_analyzer.analyze_quality(repo_path)

        # Phase 6: Generate documentation
        await _update_progress(repo_id, 68, "Generating documentation...")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Repository).where(Repository.id == repo_id))
            repo = result.scalar_one_or_none()
            repo_meta = {
                "name": repo.name if repo else "",
                "owner": repo.owner if repo else "",
                "description": repo.description if repo else "",
            }

        docs_data = doc_generator.generate_all_docs(
            repo_path, repo_meta, tree_data, tech_data, file_analyses,
            quality_data, security_data
        )

        # Phase 7: Generate Mermaid diagrams
        await _update_progress(repo_id, 76, "Generating architecture diagrams...")
        diagrams = mermaid_generator.generate_all_diagrams(tree_data, tech_data, file_analyses)

        # Phase 8: Build FAISS vector index
        await _update_progress(repo_id, 82, "Building semantic search index...")
        try:
            chunks = prepare_repo_chunks(tree_data, tech_data, file_analyses, docs_data)
            vs = VectorStore(repo_id)
            vs.build(chunks)
            logger.info(f"FAISS index built with {len(chunks)} chunks")
        except Exception as e:
            logger.warning(f"Could not build FAISS index (embeddings may not be installed): {e}")

        # Phase 9: Health scoring
        await _update_progress(repo_id, 92, "Computing health scores...")
        health_data = health_scorer.compute_health_score(
            repo_path, tree_data, tech_data, security_data, quality_data
        )

        # Generate summary
        summary = _generate_summary(tech_data, tree_data, file_analyses, repo_meta)

        # Save all results to database
        await _update_progress(repo_id, 98, "Saving analysis results...")
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Repository)
                .where(Repository.id == repo_id)
                .values(
                    status="complete",
                    progress=100,
                    progress_message="Analysis complete!",
                    analyzed_at=datetime.utcnow(),
                    tech_stack=json.dumps(tech_data),
                    file_tree=json.dumps(tree_data),
                    file_analyses=json.dumps(file_analyses),
                    summary=json.dumps({**summary, "diagrams": diagrams}),
                    architecture=json.dumps({
                        "overview": docs_data.get("architecture", ""),
                        "diagrams": diagrams,
                    }),
                    documentation=json.dumps(docs_data),
                    security_findings=json.dumps(security_data),
                    quality_report=json.dumps(quality_data),
                    health_score=json.dumps(health_data),
                    learning_path=json.dumps(docs_data.get("learning_path", [])),
                    total_files=stats.get("total_files", 0),
                    total_folders=stats.get("total_dirs", 0),
                    total_lines=quality_data.get("summary", {}).get("total_lines", 0),
                    repo_size_mb=stats.get("total_size_mb", 0.0),
                )
            )
            await db.commit()

        logger.info(f"✅ Analysis complete for repo {repo_id}")

    except Exception as e:
        logger.error(f"Analysis failed for {repo_id}: {e}", exc_info=True)
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Repository)
                .where(Repository.id == repo_id)
                .values(
                    status="error",
                    progress=0,
                    error_message=str(e),
                    progress_message=f"Error: {str(e)[:200]}",
                )
            )
            await db.commit()


def _generate_summary(
    tech_data: dict, tree_data: dict, file_analyses: dict, repo_meta: dict
) -> dict:
    """Generate an executive summary of the repository."""
    stats = tree_data.get("stats", {})
    primary_lang = tech_data.get("primary_language", "Unknown")
    frameworks = [f["name"] for f in tech_data.get("frameworks", [])]

    # Find entry points, configs, models
    entry_points = [p for p, a in file_analyses.items() if a and "entry point" in (a.get("purpose") or "").lower()]
    config_files = [p for p, a in file_analyses.items() if a and "configuration" in (a.get("purpose") or "").lower()]
    test_files = [p for p in file_analyses if "test" in p.lower()]

    # Collect all classes and functions count
    total_classes = sum(len(a.get("classes", [])) for a in file_analyses.values() if a)
    total_functions = sum(len(a.get("functions", [])) for a in file_analyses.values() if a)

    return {
        "primary_language": primary_lang,
        "frameworks": frameworks,
        "total_files": stats.get("total_files", 0),
        "total_dirs": stats.get("total_dirs", 0),
        "total_lines": 0,  # Will be updated from quality_data
        "size_mb": stats.get("total_size_mb", 0),
        "entry_points": entry_points[:5],
        "config_files": config_files[:5],
        "test_files": test_files[:5],
        "total_classes": total_classes,
        "total_functions": total_functions,
        "has_tests": len(test_files) > 0,
        "has_docs": any(
            (Path(p).name.lower().startswith("readme") for p in file_analyses)
        ),
    }
