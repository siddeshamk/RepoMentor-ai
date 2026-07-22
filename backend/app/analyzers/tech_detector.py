"""
Technology detection analyzer.
Detects programming languages, frameworks, tools, and infrastructure from
file extensions, configuration files, and dependency manifests.
"""
import json
import re
from pathlib import Path
from typing import Any

from app.utils.file_utils import walk_repo, read_file_safe, IGNORE_DIRS, _long_path
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Map file extensions → language
EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".java": "Java",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".c": "C", ".cpp": "C++", ".h": "C/C++", ".hpp": "C++",
    ".cs": "C#", ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
    ".r": "R", ".R": "R", ".lua": "Lua", ".ex": "Elixir",
    ".exs": "Elixir", ".clj": "Clojure", ".dart": "Dart",
    ".vue": "Vue", ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".sql": "SQL", ".sh": "Shell", ".ps1": "PowerShell",
    ".tf": "Terraform", ".hcl": "HCL", ".graphql": "GraphQL",
    ".proto": "Protobuf",
}

# Framework detection rules: (config_file_or_key, content_pattern, framework_name)
FRAMEWORK_RULES: list[dict[str, Any]] = [
    # Python frameworks
    {"file": "requirements.txt", "pattern": r"\bdjango\b", "name": "Django", "lang": "Python"},
    {"file": "requirements.txt", "pattern": r"\bfastapi\b", "name": "FastAPI", "lang": "Python"},
    {"file": "requirements.txt", "pattern": r"\bflask\b", "name": "Flask", "lang": "Python"},
    {"file": "requirements.txt", "pattern": r"\btorch\b|\bpytorch\b", "name": "PyTorch", "lang": "Python"},
    {"file": "requirements.txt", "pattern": r"\btensorflow\b", "name": "TensorFlow", "lang": "Python"},
    {"file": "requirements.txt", "pattern": r"\bcelery\b", "name": "Celery", "lang": "Python"},
    {"file": "requirements.txt", "pattern": r"\bsqlalchemy\b", "name": "SQLAlchemy", "lang": "Python"},
    {"file": "setup.py", "pattern": r"\bdjango\b", "name": "Django", "lang": "Python"},
    {"file": "pyproject.toml", "pattern": r"\bdjango\b", "name": "Django", "lang": "Python"},
    {"file": "pyproject.toml", "pattern": r"\bfastapi\b", "name": "FastAPI", "lang": "Python"},

    # JavaScript / Node frameworks
    {"file": "package.json", "pattern": r'"react"', "name": "React", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"next"', "name": "Next.js", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"vue"', "name": "Vue.js", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"@angular/core"', "name": "Angular", "lang": "TypeScript"},
    {"file": "package.json", "pattern": r'"express"', "name": "Express.js", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"svelte"', "name": "Svelte", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"nuxt"', "name": "Nuxt.js", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"tailwindcss"', "name": "Tailwind CSS", "lang": "CSS"},
    {"file": "package.json", "pattern": r'"bootstrap"', "name": "Bootstrap", "lang": "CSS"},
    {"file": "package.json", "pattern": r'"graphql"', "name": "GraphQL", "lang": "API"},
    {"file": "package.json", "pattern": r'"socket\.io"', "name": "Socket.IO", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"prisma"', "name": "Prisma", "lang": "JavaScript"},
    {"file": "package.json", "pattern": r'"@nestjs/core"', "name": "NestJS", "lang": "TypeScript"},

    # Java
    {"file": "pom.xml", "pattern": r"spring-boot", "name": "Spring Boot", "lang": "Java"},
    {"file": "build.gradle", "pattern": r"spring-boot", "name": "Spring Boot", "lang": "Java"},

    # Databases
    {"file": "requirements.txt", "pattern": r"\bpsycopg2\b|\bpsycopg\b", "name": "PostgreSQL", "lang": "Database"},
    {"file": "requirements.txt", "pattern": r"\bpymysql\b|\bmysqlclient\b", "name": "MySQL", "lang": "Database"},
    {"file": "requirements.txt", "pattern": r"\bmongodb\b|\bpymongo\b", "name": "MongoDB", "lang": "Database"},
    {"file": "requirements.txt", "pattern": r"\bredis\b", "name": "Redis", "lang": "Database"},
    {"file": "package.json", "pattern": r'"pg"\s*:|"postgres"', "name": "PostgreSQL", "lang": "Database"},
    {"file": "package.json", "pattern": r'"mongoose"', "name": "MongoDB", "lang": "Database"},
    {"file": "package.json", "pattern": r'"redis"', "name": "Redis", "lang": "Database"},

    # DevOps / Infrastructure
    {"file": "Dockerfile", "pattern": r".", "name": "Docker", "lang": "DevOps"},
    {"file": "docker-compose.yml", "pattern": r".", "name": "Docker Compose", "lang": "DevOps"},
    {"file": "docker-compose.yaml", "pattern": r".", "name": "Docker Compose", "lang": "DevOps"},
    {"file": "kubernetes.yml", "pattern": r".", "name": "Kubernetes", "lang": "DevOps"},
    {"file": "k8s", "pattern": None, "name": "Kubernetes", "lang": "DevOps"},
    {"file": ".github/workflows", "pattern": None, "name": "GitHub Actions", "lang": "DevOps"},
    {"file": "terraform", "pattern": None, "name": "Terraform", "lang": "DevOps"},

    # Auth / Security
    {"file": "requirements.txt", "pattern": r"\bjwt\b|\bpyjwt\b", "name": "JWT Auth", "lang": "Security"},
    {"file": "requirements.txt", "pattern": r"\boauth\b|\bauthlib\b", "name": "OAuth", "lang": "Security"},
    {"file": "package.json", "pattern": r'"jsonwebtoken"', "name": "JWT Auth", "lang": "Security"},
    {"file": "package.json", "pattern": r'"passport"', "name": "Passport.js", "lang": "Security"},

    # Testing
    {"file": "requirements.txt", "pattern": r"\bpytest\b", "name": "pytest", "lang": "Testing"},
    {"file": "package.json", "pattern": r'"jest"', "name": "Jest", "lang": "Testing"},
    {"file": "package.json", "pattern": r'"vitest"', "name": "Vitest", "lang": "Testing"},
    {"file": "package.json", "pattern": r'"cypress"', "name": "Cypress", "lang": "Testing"},
]

# Special directory detectors
DIR_RULES: list[dict[str, str]] = [
    {"dir": ".github/workflows", "name": "GitHub Actions", "lang": "DevOps"},
    {"dir": "k8s", "name": "Kubernetes", "lang": "DevOps"},
    {"dir": "terraform", "name": "Terraform", "lang": "DevOps"},
    {"dir": "charts", "name": "Helm Charts", "lang": "DevOps"},
]


def detect_technologies(repo_path: Path) -> dict:
    """
    Detect all technologies used in a repository.
    Returns a structured dictionary with languages, frameworks, and tools.
    """
    language_counts: dict[str, int] = {}
    frameworks: list[dict] = []
    detected_framework_names: set[str] = set()

    # Count language file extensions
    for file_path in walk_repo(repo_path):
        ext = file_path.suffix.lower()
        lang = EXTENSION_TO_LANGUAGE.get(ext)
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + 1

    # Framework detection via file content
    for rule in FRAMEWORK_RULES:
        config_file = repo_path / rule["file"]
        # Wrap in Path(_long_path(...)) to handle Windows path length limits
        lp_config = Path(_long_path(config_file))
        if not lp_config.exists():
            continue

        if rule.get("pattern") is None:
            # Just check existence (for directories)
            if lp_config.is_dir() and rule["name"] not in detected_framework_names:
                frameworks.append({"name": rule["name"], "category": rule["lang"]})
                detected_framework_names.add(rule["name"])
            continue

        if lp_config.is_dir():
            continue

        content = read_file_safe(config_file)
        if content and re.search(rule["pattern"], content, re.IGNORECASE):
            if rule["name"] not in detected_framework_names:
                frameworks.append({"name": rule["name"], "category": rule["lang"]})
                detected_framework_names.add(rule["name"])

    # Directory-based detection
    for rule in DIR_RULES:
        d = repo_path / rule["dir"]
        lp_d = Path(_long_path(d))
        if lp_d.exists() and rule["name"] not in detected_framework_names:
            frameworks.append({"name": rule["name"], "category": rule["lang"]})
            detected_framework_names.add(rule["name"])

    # Detect SQLite specifically by looking for .db or .sqlite files
    for f in repo_path.rglob("*.sqlite"):
        if "SQLite" not in detected_framework_names:
            frameworks.append({"name": "SQLite", "category": "Database"})
            detected_framework_names.add("SQLite")
        break

    # Build primary language (highest file count, excluding HTML/CSS/SQL)
    primary_languages = {
        k: v for k, v in language_counts.items()
        if k not in {"HTML", "CSS", "SCSS", "SQL", "Shell", "PowerShell"}
    }
    primary_language = max(primary_languages, key=primary_languages.get) if primary_languages else "Unknown"

    # Sort languages by file count
    sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    total_language_files = sum(count for _, count in sorted_languages) or 1

    # Language icons
    LANG_ICONS = {
        "Python": "🐍", "JavaScript": "🟨", "TypeScript": "🔷", "Java": "☕",
        "Go": "🐹", "Rust": "🦀", "Ruby": "💎", "PHP": "🐘",
        "C": "🔧", "C++": "🔧", "C/C++": "🔧", "C#": "🔵",
        "Swift": "🍎", "Kotlin": "🟣", "Scala": "🔴", "Dart": "🎯",
        "Vue": "💚", "HTML": "🌐", "CSS": "🎨", "SCSS": "🎨",
        "Shell": "💻", "PowerShell": "💻", "SQL": "🗃️",
        "Lua": "🌙", "Elixir": "💧", "Clojure": "🟢", "R": "📊",
    }

    # Framework icons
    FRAMEWORK_ICONS = {
        "React": "⚛️", "Next.js": "▲", "Vue.js": "💚", "Angular": "🅰️",
        "Django": "🎸", "FastAPI": "⚡", "Flask": "🌶️", "Express.js": "🚂",
        "Spring Boot": "🍃", "Docker": "🐳", "Docker Compose": "🐳",
        "Kubernetes": "☸️", "Tailwind CSS": "💨", "GitHub Actions": "🔄",
        "PostgreSQL": "🐘", "MongoDB": "🍃", "Redis": "🔴", "SQLite": "📦",
        "SQLAlchemy": "🗄️", "pytest": "🧪", "Jest": "🃏",
        "JWT Auth": "🔑", "GraphQL": "◆", "Prisma": "△",
    }

    # Add icons to frameworks
    for fw in frameworks:
        fw["icon"] = FRAMEWORK_ICONS.get(fw["name"], "⚙️")

    return {
        "primary_language": primary_language,
        "languages": [
            {
                "name": lang,
                "files": count,
                "percentage": round((count / total_language_files) * 100, 1),
                "icon": LANG_ICONS.get(lang, "📄"),
            }
            for lang, count in sorted_languages
        ],
        "frameworks": frameworks,
        "categories": _group_by_category(frameworks),
    }


def _group_by_category(frameworks: list[dict]) -> dict:
    """Group frameworks by category."""
    groups: dict[str, list[str]] = {}
    for f in frameworks:
        cat = f["category"]
        if cat not in groups:
            groups[cat] = []
        groups[cat].append(f["name"])
    return groups
