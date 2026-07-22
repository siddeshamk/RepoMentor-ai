"""
Clone service: validates GitHub URLs and clones repositories using GitPython.
"""
import os
import re
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import git
from git import Repo, GitCommandError

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Matches various GitHub URL formats:
#   https://github.com/owner/repo
#   https://github.com/owner/repo.git
#   http://github.com/owner/repo
#   https://www.github.com/owner/repo
#   https://github.com/owner/repo/tree/main  (extra path segments stripped)
#   github.com/owner/repo  (no protocol)
GITHUB_URL_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?(?:/.*)?$"
)


def validate_github_url(url: str) -> tuple[bool, str, str]:
    """
    Validate a GitHub URL.
    Returns (is_valid, owner, repo_name).
    """
    url = url.strip()
    match = GITHUB_URL_PATTERN.match(url)
    if not match:
        return False, "", ""
    return True, match.group(1), match.group(2)


def normalize_url(url: str) -> str:
    """
    Normalize a GitHub URL to canonical https://github.com/owner/repo format.
    Strips .git suffix, extra path segments (/tree/main, /issues, etc.),
    protocol variations (http/https/none), and www subdomain.
    """
    is_valid, owner, repo_name = validate_github_url(url)
    if not is_valid:
        return url.strip()
    return f"https://github.com/{owner}/{repo_name}"


def get_clone_path(owner: str, repo_name: str) -> Path:
    """Return the local clone destination path as an absolute path."""
    # Resolve to absolute path to support Windows long paths (>260 chars)
    return settings.repos_dir.resolve() / f"{owner}__{repo_name}"

def clone_repository(url: str, owner: str, repo_name: str) -> tuple[Path, dict]:
    """
    Clone a GitHub repository to local disk.
    Returns (clone_path, metadata_dict).
    Raises RuntimeError if clone fails.
    """

    clone_path = get_clone_path(owner, repo_name)

    # Repository already exists
    if clone_path.exists():
        try:
            logger.info(f"Repository already exists at {clone_path}, pulling latest...")

            repo = Repo(clone_path)
            origin = repo.remotes.origin
            origin.pull()

            logger.info("✅ Repository updated")

        except Exception as e:
            logger.warning(f"Repository is invalid or corrupted. Re-cloning... ({e})")

            # Delete the broken repository
            shutil.rmtree(clone_path, ignore_errors=True)

            try:
                repo = Repo.clone_from(
                    url,
                    clone_path,
                    depth=1,
                    single_branch=True,
                )
                logger.info("✅ Repository re-cloned successfully")

            except GitCommandError as clone_error:
                raise RuntimeError(
                    f"Git clone failed: {clone_error}"
                ) from clone_error

    else:
        try:
            logger.info(f"Cloning {url} → {clone_path}")

            repo = Repo.clone_from(
                url,
                clone_path,
                depth=1,
                single_branch=True,
            )

            logger.info("✅ Repository cloned successfully")

        except GitCommandError as e:
            if clone_path.exists():
                shutil.rmtree(clone_path, ignore_errors=True)

            raise RuntimeError(f"Git clone failed: {e}") from e

    metadata = extract_repo_metadata(repo, url, owner, repo_name)

    return clone_path, metadata

def extract_repo_metadata(repo: Repo, url: str, owner: str, repo_name: str) -> dict:
    """Extract metadata from a cloned repository."""
    description = ""
    default_branch = "main"

    try:
        # Try to get branch name
        default_branch = repo.active_branch.name
    except Exception:
        pass

    # Try to read description from git config
    try:
        description = repo.description or ""
        if description == "Unnamed repository; edit this file 'description' to name the repository.":
            description = ""
    except Exception:
        pass

    # Parse README for description if not found
    if not description:
        readme_path = None
        for name in ["README.md", "README.txt", "README.rst", "readme.md"]:
            p = Path(repo.working_dir) / name
            if p.exists():
                readme_path = p
                break
        if readme_path:
            try:
                content = readme_path.read_text(encoding="utf-8", errors="ignore")
                # Take first non-empty paragraph
                lines = [l.strip() for l in content.splitlines() if l.strip()]
                # Skip headings and badges
                for line in lines:
                    if not line.startswith("#") and not line.startswith("!") and len(line) > 20:
                        description = line[:300]
                        break
            except Exception:
                pass

    return {
        "url": url,
        "name": repo_name,
        "owner": owner,
        "description": description,
        "default_branch": default_branch,
        "clone_path": str(repo.working_dir),
    }
