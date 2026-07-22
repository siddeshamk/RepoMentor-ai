"""
Repository health scorer: computes multi-dimensional scores for architecture,
documentation, security, maintainability, testing, and overall health.
"""
from pathlib import Path
from typing import Any

from app.utils.logger import get_logger
from app.utils.file_utils import _long_path

logger = get_logger(__name__)


def compute_health_score(
    repo_path: Path,
    tree_data: dict,
    tech_data: dict,
    security_data: dict,
    quality_data: dict,
) -> dict:
    """
    Compute a comprehensive health score for the repository.
    Returns scores (0-100) for each dimension plus an overall score.
    """
    scores = {}
    explanations = {}

    # 1. Documentation score
    doc_score, doc_exp = _documentation_score(repo_path, tree_data)
    scores["documentation"] = doc_score
    explanations["documentation"] = doc_exp

    # 2. Security score (directly from security analyzer)
    sec_score = security_data.get("score", 100)
    sec_count = security_data.get("total", 0)
    scores["security"] = sec_score
    explanations["security"] = (
        f"Found {sec_count} security issue(s). "
        + (f"Critical issues: {security_data.get('summary', {}).get('critical', 0)}."
           if security_data.get('summary', {}).get('critical', 0) else "No critical issues found.")
    )

    # 3. Maintainability score
    maint_score = quality_data.get("maintainability_score", 100)
    large_files = quality_data.get("summary", {}).get("large_file_count", 0)
    long_funcs = quality_data.get("summary", {}).get("long_function_count", 0)
    scores["maintainability"] = maint_score
    explanations["maintainability"] = (
        f"{large_files} large file(s), {long_funcs} long function(s). "
        + ("Code is well-structured." if maint_score >= 80 else "Consider refactoring large files and functions.")
    )

    # 4. Testing score
    test_score, test_exp = _testing_score(repo_path, tree_data)
    scores["testing"] = test_score
    explanations["testing"] = test_exp

    # 5. Architecture score (based on folder structure and modularity)
    arch_score, arch_exp = _architecture_score(repo_path, tree_data, tech_data)
    scores["architecture"] = arch_score
    explanations["architecture"] = arch_exp

    # 6. Readability score (based on naming, comments, docs)
    read_score, read_exp = _readability_score(repo_path, quality_data)
    scores["readability"] = read_score
    explanations["readability"] = read_exp

    # 7. Performance (heuristic)
    perf_score, perf_exp = _performance_score(quality_data, security_data)
    scores["performance"] = perf_score
    explanations["performance"] = perf_exp

    # Overall: weighted average
    weights = {
        "documentation": 0.15,
        "security": 0.20,
        "maintainability": 0.20,
        "testing": 0.15,
        "architecture": 0.15,
        "readability": 0.10,
        "performance": 0.05,
    }
    overall = sum(scores[k] * weights[k] for k in weights)
    overall = round(overall)

    return {
        "scores": scores,
        "overall": overall,
        "grade": _grade(overall),
        "explanations": explanations,
        "recommendations": _generate_recommendations(scores, security_data, quality_data),
    }


def _documentation_score(repo_path: Path, tree_data: dict) -> tuple[int, str]:
    """Score based on presence of README, comments, and docs."""
    score = 40  # Start at 40
    notes = []

    # README presence
    has_readme = any(
        Path(_long_path(repo_path / name)).exists()
        for name in ["README.md", "README.txt", "README.rst", "readme.md"]
    )
    if has_readme:
        score += 25
        notes.append("README present (+25)")
    else:
        notes.append("No README found (-25)")

    # Docs directory
    has_docs = Path(_long_path(repo_path / "docs")).exists() or Path(_long_path(repo_path / "documentation")).exists()
    if has_docs:
        score += 15
        notes.append("Docs directory found (+15)")

    # CHANGELOG
    has_changelog = Path(_long_path(repo_path / "CHANGELOG.md")).exists() or Path(_long_path(repo_path / "HISTORY.md")).exists()
    if has_changelog:
        score += 10
        notes.append("CHANGELOG present (+10)")

    # Contributing guide
    has_contrib = Path(_long_path(repo_path / "CONTRIBUTING.md")).exists()
    if has_contrib:
        score += 10
        notes.append("CONTRIBUTING.md found (+10)")

    return min(100, score), ". ".join(notes) or "Basic documentation only."


def _testing_score(repo_path: Path, tree_data: dict) -> tuple[int, str]:
    """Score based on presence and extent of tests."""
    score = 30  # Start at 30
    notes = []

    # Test directory
    has_tests = any(
        Path(_long_path(repo_path / d)).exists()
        for d in ["tests", "test", "__tests__", "spec", "specs"]
    )
    if has_tests:
        score += 30
        notes.append("Test directory found (+30)")

    # Test config files
    has_pytest = Path(_long_path(repo_path / "pytest.ini")).exists() or Path(_long_path(repo_path / "pyproject.toml")).exists()
    has_jest = Path(_long_path(repo_path / "jest.config.js")).exists() or Path(_long_path(repo_path / "jest.config.ts")).exists()
    has_vitest = Path(_long_path(repo_path / "vitest.config.js")).exists() or Path(_long_path(repo_path / "vitest.config.ts")).exists()

    if has_pytest or has_jest or has_vitest:
        score += 20
        notes.append("Test configuration found (+20)")

    # CI/CD (usually runs tests)
    has_ci = Path(_long_path(repo_path / ".github" / "workflows")).exists()
    if has_ci:
        score += 20
        notes.append("CI/CD pipeline detected (+20)")

    return min(100, score), ". ".join(notes) or "No test files detected."


def _architecture_score(repo_path: Path, tree_data: dict, tech_data: dict) -> tuple[int, str]:
    """Score based on folder structure and separation of concerns."""
    score = 50
    notes = []

    stats = tree_data.get("stats", {})
    total_files = stats.get("total_files", 0)
    total_dirs = stats.get("total_dirs", 1)

    # Good directory structure (files not all in root)
    if total_dirs > 3:
        score += 20
        notes.append("Good directory structure (+20)")

    # Separation of concerns indicators
    good_dirs = {"api", "services", "models", "controllers", "utils", "config", "tests"}
    found = 0
    for d in good_dirs:
        if Path(_long_path(repo_path / d)).exists() or Path(_long_path(repo_path / "src" / d)).exists():
            found += 1
    if found >= 3:
        score += 20
        notes.append(f"{found} concern-separated directories (+20)")
    elif found >= 1:
        score += 10

    # Config files present
    has_config = any(
        Path(_long_path(repo_path / f)).exists()
        for f in [".env.example", "config.py", "settings.py", "config.js", "config.ts"]
    )
    if has_config:
        score += 10
        notes.append("Configuration files present (+10)")

    return min(100, score), ". ".join(notes) or "Flat project structure."


def _readability_score(repo_path: Path, quality_data: dict) -> tuple[int, str]:
    """Score based on code quality indicators."""
    score = 60
    notes = []

    todo_count = quality_data.get("summary", {}).get("todo_count", 0)
    fixme_count = quality_data.get("summary", {}).get("fixme_count", 0)

    if todo_count == 0 and fixme_count == 0:
        score += 20
        notes.append("No TODO/FIXME comments")
    else:
        penalty = min(30, (todo_count + fixme_count * 2))
        score -= penalty
        notes.append(f"{todo_count} TODOs, {fixme_count} FIXMEs (-{penalty})")

    return max(0, min(100, score)), ". ".join(notes) or "Code readability appears acceptable."


def _performance_score(quality_data: dict, security_data: dict) -> tuple[int, str]:
    """Heuristic performance score."""
    score = 80
    notes = []

    large_files = quality_data.get("summary", {}).get("large_file_count", 0)
    if large_files > 5:
        score -= 20
        notes.append(f"{large_files} large files may impact build/load performance")
    elif large_files > 0:
        score -= 10

    return max(0, score), ". ".join(notes) or "No obvious performance concerns detected."


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def _generate_recommendations(scores: dict, security_data: dict, quality_data: dict) -> list[str]:
    """Generate actionable recommendations based on scores."""
    recs = []

    if scores.get("documentation", 100) < 70:
        recs.append("📝 Add a comprehensive README.md with setup, usage, and API documentation.")

    if scores.get("security", 100) < 80:
        critical = security_data.get("summary", {}).get("critical", 0)
        if critical:
            recs.append(f"🚨 Fix {critical} critical security issue(s) immediately — remove hardcoded secrets.")
        recs.append("🔒 Review security findings and move secrets to environment variables.")

    if scores.get("testing", 100) < 60:
        recs.append("🧪 Add unit tests to improve reliability and enable confident refactoring.")

    if scores.get("maintainability", 100) < 70:
        recs.append("♻️  Refactor large files and long functions to improve maintainability.")

    if scores.get("architecture", 100) < 60:
        recs.append("🏗️  Organize code into clear directories (api, services, models, tests).")

    if not recs:
        recs.append("✅ Repository looks healthy! Continue maintaining code quality and documentation.")

    return recs
