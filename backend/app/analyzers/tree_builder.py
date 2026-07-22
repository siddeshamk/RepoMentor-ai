"""
Tree builder: constructs a hierarchical directory/file tree of the repository.
"""
import os
from pathlib import Path
from typing import Any

from app.utils.file_utils import should_ignore_dir, should_ignore_file, is_text_file, get_dir_size_mb, _long_path, get_relative_path
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Folder purpose heuristics — common folder names mapped to explanations
FOLDER_PURPOSES: dict[str, str] = {
    "src": "Main source code directory",
    "lib": "Shared library code",
    "app": "Application entry points and core code",
    "api": "API route handlers and controllers",
    "models": "Data models and database schemas",
    "views": "View templates or UI components",
    "controllers": "Controller/handler logic",
    "services": "Business logic services",
    "utils": "Utility and helper functions",
    "helpers": "Helper functions",
    "middlewares": "Middleware functions",
    "middleware": "Middleware functions",
    "routes": "URL routing definitions",
    "config": "Configuration files",
    "settings": "Application settings",
    "tests": "Test suites",
    "test": "Test suites",
    "__tests__": "Jest test suites",
    "spec": "Specification/test files",
    "docs": "Documentation files",
    "scripts": "Build and utility scripts",
    "migrations": "Database migration files",
    "static": "Static assets (CSS, images, JS)",
    "assets": "Static assets",
    "public": "Publicly accessible files",
    "templates": "HTML/email templates",
    "components": "Reusable UI components",
    "pages": "Application pages or views",
    "hooks": "React hooks or lifecycle hooks",
    "store": "State management (Redux, Zustand, etc.)",
    "context": "React Context providers",
    "styles": "Stylesheets",
    "css": "CSS stylesheets",
    "scss": "SCSS stylesheets",
    "images": "Image assets",
    "icons": "Icon assets",
    "fonts": "Font files",
    "types": "TypeScript type definitions",
    "interfaces": "Interface definitions",
    "schemas": "Validation schemas",
    "validators": "Input validators",
    "serializers": "Data serializers",
    "forms": "Form definitions",
    "admin": "Admin panel files",
    "auth": "Authentication and authorization",
    "security": "Security utilities",
    "database": "Database configuration and queries",
    "db": "Database files",
    "seed": "Database seed data",
    "fixtures": "Test fixtures",
    "mocks": "Mock objects for testing",
    "deploy": "Deployment scripts",
    "infrastructure": "Infrastructure as code",
    "docker": "Docker configuration",
    "k8s": "Kubernetes manifests",
    "helm": "Helm chart files",
    "ci": "Continuous integration scripts",
    "workflows": "GitHub Actions workflows",
    "bin": "Executable scripts",
    "cmd": "Command-line entry points (Go)",
    "internal": "Internal packages (Go)",
    "pkg": "Public packages (Go)",
    "vendor": "Vendored dependencies",
    "core": "Core/fundamental modules",
    "common": "Shared/common code",
    "shared": "Shared utilities across modules",
    "features": "Feature modules",
    "modules": "Application modules",
    "plugins": "Plugin definitions",
    "extensions": "Extensions",
    "integrations": "Third-party integrations",
    "workers": "Background workers or tasks",
    "jobs": "Scheduled jobs",
    "tasks": "Celery or similar tasks",
    "events": "Event handlers",
    "listeners": "Event listeners",
    "handlers": "Request or event handlers",
    "resolvers": "GraphQL resolvers",
    "mutations": "GraphQL mutations",
    "queries": "GraphQL queries",
}


def build_tree(repo_path: Path, max_depth: int = 10) -> dict:
    """
    Build a complete, hierarchical tree of the repository.
    Returns a nested dict structure suitable for JSON serialization.
    """
    def _build_node(path: Path, depth: int) -> dict[str, Any]:
        name = path.name
        relative = get_relative_path(path, repo_path)

        # Wrap in Path(_long_path(...)) to handle Windows path length limits
        lp_path = Path(_long_path(path))

        if lp_path.is_file():
            size = 0
            try:
                size = os.path.getsize(str(lp_path))
            except OSError:
                pass
            return {
                "type": "file",
                "name": name,
                "path": relative,
                "extension": path.suffix.lower(),
                "size_bytes": size,
                "is_text": is_text_file(path),
            }

        # Directory node
        children = []
        if depth < max_depth:
            try:
                entries = sorted(lp_path.iterdir(), key=lambda p: (Path(_long_path(p)).is_file(), p.name.lower()))
                for entry in entries:
                    if Path(_long_path(entry)).is_dir():
                        if should_ignore_dir(entry.name):
                            continue
                        children.append(_build_node(entry, depth + 1))
                    else:
                        if should_ignore_file(entry.name):
                            continue
                        children.append(_build_node(entry, depth + 1))
            except PermissionError:
                pass

        purpose = FOLDER_PURPOSES.get(name.lower(), "")
        return {
            "type": "directory",
            "name": name,
            "path": relative if relative != "." else "",
            "purpose": purpose,
            "children": children,
            "child_count": len(children),
        }

    logger.info(f"Building repository tree for {repo_path.name}")
    tree = _build_node(repo_path, 0)

    # Collect flat stats
    stats = _collect_stats(tree)
    logger.info(f"Tree built: {stats['total_files']} files, {stats['total_dirs']} dirs")

    return {
        "root": tree,
        "stats": stats,
    }


def _collect_stats(node: dict) -> dict:
    """Recursively collect statistics from the tree."""
    total_files = 0
    total_dirs = 0
    total_size = 0
    extensions: dict[str, int] = {}

    def _traverse(n: dict):
        nonlocal total_files, total_dirs, total_size
        if n["type"] == "file":
            total_files += 1
            total_size += n.get("size_bytes", 0)
            ext = n.get("extension", "")
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
        else:
            total_dirs += 1
            for child in n.get("children", []):
                _traverse(child)

    _traverse(node)

    # Sort extensions by count
    top_extensions = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_files": total_files,
        "total_dirs": total_dirs,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "top_extensions": [{"ext": e, "count": c} for e, c in top_extensions],
    }


def get_folder_purpose(folder_name: str) -> str:
    """Return a human-readable purpose for a folder name."""
    return FOLDER_PURPOSES.get(folder_name.lower(), f"Contains {folder_name}-related files")
