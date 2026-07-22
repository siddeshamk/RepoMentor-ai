"""
File system utilities: filtering, walking, reading, and classifying files.
"""
import os
import re
import sys
from pathlib import Path
from typing import Generator, Optional

# Directories to always skip during analysis
IGNORE_DIRS = frozenset({
    "node_modules", ".git", "venv", ".venv", "env", "__pycache__",
    "build", "dist", ".next", ".nuxt", "out", "target", ".gradle",
    "coverage", ".pytest_cache", ".mypy_cache", ".tox", "eggs", ".eggs",
    "wheels", "buck-out", ".buck", ".cache", ".terraform", "vendor",
    "bower_components", "jspm_packages", ".cargo", ".rustup",
    "site-packages", "lib64", ".angular", "android", "ios",
})

# Files to always skip
IGNORE_FILES = frozenset({
    ".DS_Store", "Thumbs.db", "package-lock.json", "yarn.lock",
    "poetry.lock", "Pipfile.lock", "composer.lock", "Gemfile.lock",
    "pnpm-lock.yaml", ".gitkeep",
})

# Extensions that can be read as text
TEXT_EXTENSIONS = frozenset({
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs",
    ".rb", ".php", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift",
    ".kt", ".scala", ".vue", ".html", ".htm", ".css", ".scss",
    ".less", ".json", ".yaml", ".yml", ".toml", ".xml", ".md",
    ".txt", ".env.example", ".gitignore", ".dockerignore", ".sql",
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    ".tf", ".hcl", ".graphql", ".gql", ".proto", ".r", ".R",
    ".lua", ".pl", ".ex", ".exs", ".clj", ".dart", ".makefile",
    ".mk", ".gradle", ".dockerfile", ".ini", ".cfg", ".conf",
    ".properties",
})


def should_ignore_dir(dir_name: str) -> bool:
    """Return True if this directory should be skipped."""
    return dir_name.startswith(".") and dir_name not in {".env.example"} or dir_name in IGNORE_DIRS


def should_ignore_file(file_name: str) -> bool:
    """Return True if this file should be skipped."""
    if file_name in IGNORE_FILES:
        return True
    # Skip compiled / binary extensions
    skip_exts = {".pyc", ".pyo", ".class", ".o", ".so", ".dll", ".exe",
                 ".bin", ".obj", ".lib", ".a", ".jar", ".war", ".ear",
                 ".wasm", ".map", ".min.js", ".min.css"}
    suffix = Path(file_name).suffix.lower()
    return suffix in skip_exts


def is_text_file(path: Path) -> bool:
    """Return True if the file is a readable text file."""
    suffix = path.suffix.lower()
    # Special names without extensions
    special_names = {"makefile", "dockerfile", "rakefile", "gemfile",
                     "vagrantfile", "procfile", "jenkinsfile"}
    if path.name.lower() in special_names:
        return True
    return suffix in TEXT_EXTENSIONS


def _long_path(path: Path) -> str:
    """Convert a path to a Windows long-path-aware string if needed.

    On Windows, paths longer than ~260 characters cause [WinError 3].
    Prefixing with '\\\\?\\' tells Windows APIs to support up to 32k chars.
    """
    s = str(path.resolve())
    if sys.platform == "win32" and not s.startswith("\\\\?\\"):
        s = "\\\\?\\" + s
    return s


def walk_repo(repo_path: Path, max_files: int = 2000) -> Generator[Path, None, None]:
    """
    Walk a repository directory, yielding text file paths.
    Respects IGNORE_DIRS and IGNORE_FILES filters.
    Uses long-path-aware strings on Windows to avoid MAX_PATH errors.
    """
    count = 0
    walk_root = _long_path(repo_path)
    for root, dirs, files in os.walk(walk_root):
        # Prune ignored directories in-place (modifies the walk)
        dirs[:] = [d for d in dirs if not should_ignore_dir(d)]

        for file in sorted(files):
            if should_ignore_file(file):
                continue
            file_path = Path(root) / file
            if is_text_file(file_path):
                yield file_path
                count += 1
                if count >= max_files:
                    return


def read_file_safe(path: Path, max_bytes: int = 2 * 1024 * 1024) -> Optional[str]:
    """
    Read a file safely, returning None on binary/encoding errors.
    Caps read at max_bytes to avoid huge files.
    Uses long-path-aware strings on Windows.
    """
    try:
        lp = _long_path(path)
        size = os.path.getsize(lp)
        if size > max_bytes:
            return None  # Skip very large files
        with open(lp, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except (OSError, PermissionError):
        return None


def get_relative_path(file_path: Path, repo_path: Path) -> str:
    """Return the relative path of a file from the repo root as a POSIX string."""
    fp_str = str(file_path)
    rp_str = str(repo_path)
    if fp_str.startswith("\\\\?\\"):
        fp_str = fp_str[4:]
    if rp_str.startswith("\\\\?\\"):
        rp_str = rp_str[4:]
    # Use os.path.relpath which is robust against various Windows path representations
    rel = os.path.relpath(fp_str, rp_str)
    return rel.replace("\\", "/")


def count_lines(content: str) -> int:
    """Count non-empty lines in a string."""
    return sum(1 for line in content.splitlines() if line.strip())


def get_dir_size_mb(path: Path) -> float:
    """Calculate total directory size in megabytes."""
    total = 0
    walk_root = _long_path(path)
    for root, _dirs, files in os.walk(walk_root):
        for fname in files:
            try:
                fp = os.path.join(root, fname)
                total += os.path.getsize(fp)
            except OSError:
                pass
    return round(total / (1024 * 1024), 2)
