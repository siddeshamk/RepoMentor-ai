"""
Architecture Generator

Generates text/ASCII architecture descriptions instead of Mermaid syntax.
The frontend renders these directly without Mermaid.js.
"""

from pathlib import Path
from typing import Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_all_diagrams(
    tree_data: dict,
    tech_data: dict,
    file_analyses: dict,
) -> dict:
    """
    Generate all architecture outputs.

    Returned keys are kept identical to the previous implementation so the
    frontend and database schema continue working.
    """

    return {
        "folder_structure": generate_folder_structure(tree_data),
        "tech_stack": generate_tech_stack(tree_data, tech_data),
        "data_flow": generate_data_flow(tech_data),
        "dependency_graph": generate_dependency_graph(file_analyses),
        "architecture": generate_architecture(tree_data, tech_data),
    }


def _section(title: str) -> str:
    return f"\n{'=' * 70}\n{title}\n{'=' * 70}\n"


def _bullet(text: str) -> str:
    return f"• {text}"


def _frameworks(tech_data: dict) -> list[str]:
    return [x["name"] for x in tech_data.get("frameworks", [])]


def _categories(tech_data: dict) -> dict:
    return tech_data.get("categories", {})
def generate_folder_structure(tree_data: dict) -> str:
    """
    Generate a readable repository folder tree.
    """

    root = tree_data.get("root", {})
    lines = [_section("REPOSITORY STRUCTURE")]

    if not root:
        lines.append("No repository tree available.")
        return "\n".join(lines)

    def walk(node, prefix=""):
        name = node.get("name", "unknown")
        node_type = node.get("type", "file")

        if node_type == "directory":
            lines.append(f"{prefix}📁 {name}")

            children = node.get("children", [])

            dirs = [c for c in children if c.get("type") == "directory"]
            files = [c for c in children if c.get("type") == "file"]

            for child in dirs[:8]:
                walk(child, prefix + "    ")

            for child in files[:8]:
                lines.append(prefix + "    📄 " + child.get("name", ""))

            remaining = len(children) - min(len(children), 16)

            if remaining > 0:
                lines.append(prefix + f"    ... {remaining} more items")

        else:
            lines.append(prefix + "📄 " + name)

    walk(root)

    return "\n".join(lines)


def generate_tech_stack(tree_data: dict, tech_data: dict) -> str:
    """
    Generate a readable technology stack summary.
    """

    categories = _categories(tech_data)

    lines = [_section("TECHNOLOGY STACK")]

    if not categories:
        lines.append("No technologies detected.")
        return "\n".join(lines)

    for category, technologies in categories.items():

        lines.append(f"\n{category}")

        lines.append("-" * len(category))

        for tech in technologies:
            lines.append(_bullet(tech))

    frameworks = _frameworks(tech_data)

    if frameworks:
        lines.append(_section("FRAMEWORK SUMMARY"))

        for framework in frameworks:
            lines.append(_bullet(framework))

    return "\n".join(lines)
def generate_data_flow(tech_data: dict) -> str:
    """
    Generate a readable request/data flow.
    """

    frameworks = _frameworks(tech_data)

    frontend = next(
        (x for x in ["React", "Next.js", "Vue.js", "Angular", "Svelte"] if x in frameworks),
        None,
    )

    backend = next(
        (x for x in ["FastAPI", "Django", "Flask", "Express.js", "NestJS", "Spring Boot"] if x in frameworks),
        None,
    )

    database = next(
        (x for x in ["PostgreSQL", "MySQL", "SQLite", "MongoDB"] if x in frameworks),
        None,
    )

    cache = "Redis" if "Redis" in frameworks else None

    lines = [_section("APPLICATION FLOW")]

    if frontend:
        lines.append("[ User ]")
        lines.append("     │")
        lines.append("     ▼")
        lines.append(f"[ {frontend} ]")

    if backend:
        if frontend:
            lines.append("     │")
            lines.append(" REST / HTTP")
            lines.append("     ▼")
        else:
            lines.append("[ User ]")
            lines.append("     │")
            lines.append("     ▼")

        lines.append(f"[ {backend} ]")

    if database:
        lines.append("     │")
        lines.append(" SQL")
        lines.append("     ▼")
        lines.append(f"[ {database} ]")

    if cache:
        lines.append("")
        lines.append(f"Cache Layer : {cache}")

    if not (frontend or backend or database):
        lines.append("Architecture could not be determined.")

    return "\n".join(lines)


def generate_dependency_graph(file_analyses: dict) -> str:
    """
    Generate a simplified dependency report.
    """

    lines = [_section("MODULE DEPENDENCIES")]

    if not file_analyses:
        lines.append("No dependency information available.")
        return "\n".join(lines)

    shown = 0

    for path, analysis in file_analyses.items():

        if shown >= 30:
            break

        if not analysis:
            continue

        deps = analysis.get("dependencies", [])

        if not deps:
            continue

        lines.append(f"\n{Path(path).name}")

        for dep in deps[:8]:
            lines.append(f"   ├── {dep}")

        shown += 1

    if shown == 0:
        lines.append("No dependencies detected.")

    return "\n".join(lines)
def generate_architecture(tree_data: dict, tech_data: dict) -> str:
    """
    Generate a high-level application architecture report.
    """

    frameworks = _frameworks(tech_data)

    frontend = next(
        (x for x in ["React", "Next.js", "Vue.js", "Angular", "Svelte"] if x in frameworks),
        None,
    )

    backend = next(
        (x for x in ["FastAPI", "Django", "Flask", "Express.js", "NestJS", "Spring Boot"] if x in frameworks),
        None,
    )

    database = next(
        (x for x in ["PostgreSQL", "MySQL", "SQLite", "MongoDB"] if x in frameworks),
        None,
    )

    cache = "Redis" if "Redis" in frameworks else None

    lines = [_section("SYSTEM ARCHITECTURE")]

    lines.append("┌──────────────────────────────┐")
    lines.append("│            USER              │")
    lines.append("└──────────────┬───────────────┘")

    if frontend:
        lines.append("               │")
        lines.append("               ▼")
        lines.append("┌──────────────────────────────┐")
        lines.append(f"│ Frontend : {frontend:<16}│")
        lines.append("└──────────────┬───────────────┘")

    if backend:
        lines.append("               │")
        lines.append("               ▼")
        lines.append("┌──────────────────────────────┐")
        lines.append(f"│ Backend  : {backend:<16}│")
        lines.append("└──────────────┬───────────────┘")

    if database:
        lines.append("               │")
        lines.append("               ▼")
        lines.append("┌──────────────────────────────┐")
        lines.append(f"│ Database : {database:<16}│")
        lines.append("└──────────────────────────────┘")

    if cache:
        lines.append("")
        lines.append(f"Cache Layer : {cache}")

    lines.append("")
    lines.append(_section("ARCHITECTURE SUMMARY"))

    if frontend:
        lines.append(_bullet(f"Frontend Framework : {frontend}"))

    if backend:
        lines.append(_bullet(f"Backend Framework : {backend}"))

    if database:
        lines.append(_bullet(f"Database : {database}"))

    if cache:
        lines.append(_bullet(f"Cache : {cache}"))

    layers = _detect_layers(tree_data)

    if layers:
        lines.append("")
        lines.append("Detected Layers")

        for layer in layers:
            lines.append(_bullet(layer))

    patterns = _detect_patterns(tree_data)

    if patterns:
        lines.append("")
        lines.append("Detected Patterns")

        for pattern in patterns:
            lines.append(_bullet(pattern))

    return "\n".join(lines)


def _detect_layers(tree_data: dict) -> list[str]:
    """
    Detect common architectural layers from directory names.
    """

    root = tree_data.get("root", {})
    names = set()

    def walk(node):
        if node.get("type") == "directory":
            names.add(node.get("name", "").lower())

        for child in node.get("children", []):
            walk(child)

    walk(root)

    mapping = {
        "controllers": "Controller Layer",
        "controller": "Controller Layer",
        "routes": "Routing Layer",
        "router": "Routing Layer",
        "views": "Presentation Layer",
        "templates": "Presentation Layer",
        "services": "Service Layer",
        "service": "Service Layer",
        "models": "Data Model Layer",
        "model": "Data Model Layer",
        "repositories": "Repository Layer",
        "repository": "Repository Layer",
        "database": "Database Layer",
        "db": "Database Layer",
        "config": "Configuration Layer",
        "configs": "Configuration Layer",
        "middleware": "Middleware Layer",
        "utils": "Utility Layer",
        "helpers": "Utility Layer",
        "api": "API Layer",
        "tests": "Testing Layer",
        "docs": "Documentation",
    }

    result = []

    for folder, layer in mapping.items():
        if folder in names and layer not in result:
            result.append(layer)

    return result


def _detect_patterns(tree_data: dict) -> list[str]:
    """
    Detect common software architecture patterns.
    """

    root = tree_data.get("root", {})
    folders = set()

    def walk(node):
        if node.get("type") == "directory":
            folders.add(node.get("name", "").lower())

        for child in node.get("children", []):
            walk(child)

    walk(root)

    patterns = []

    if {"controllers", "models", "views"}.issubset(folders):
        patterns.append("MVC Architecture")

    if {"routes", "services", "models"}.issubset(folders):
        patterns.append("Layered Architecture")

    if {"api", "services"}.issubset(folders):
        patterns.append("Service-Oriented Design")

    if {"repository", "repositories"}.intersection(folders):
        patterns.append("Repository Pattern")

    if {"middleware"}.intersection(folders):
        patterns.append("Middleware Pipeline")

    if {"tests"}.intersection(folders):
        patterns.append("Test-Oriented Development")

    return patterns