"""
File analyzer: extracts imports, functions, classes, and generates
a structural summary for each source file using AST parsing.
"""
import ast
import os
import re
from pathlib import Path
from typing import Any

from app.utils.file_utils import read_file_safe, get_relative_path, count_lines, _long_path
from app.utils.logger import get_logger

logger = get_logger(__name__)


def analyze_file(file_path: Path, repo_path: Path) -> dict[str, Any]:
    """
    Analyze a single file: extract structure, imports, classes, functions.
    Returns a dict with all extracted information.
    """
    rel_path = get_relative_path(file_path, repo_path)
    content = read_file_safe(file_path)

    if content is None:
        return _empty_analysis(rel_path, "File too large or unreadable")

    ext = file_path.suffix.lower()
    line_count = len(content.splitlines())
    non_empty_lines = count_lines(content)

    result: dict[str, Any] = {
        "path": rel_path,
        "extension": ext,
        "line_count": line_count,
        "non_empty_lines": non_empty_lines,
        "size_bytes": os.path.getsize(_long_path(file_path)) if "os" in globals() or __import__("os") else file_path.stat().st_size,
        "imports": [],
        "classes": [],
        "functions": [],
        "exports": [],
        "todos": [],
        "fixmes": [],
        "purpose": "",
        "dependencies": [],
    }

    # Language-specific analysis
    if ext == ".py":
        _analyze_python(content, result)
    elif ext in {".js", ".jsx", ".ts", ".tsx"}:
        _analyze_javascript(content, result)
    elif ext == ".java":
        _analyze_java(content, result)
    elif ext == ".go":
        _analyze_go(content, result)
    else:
        # Generic: just extract todos and fixmes
        pass

    # Universal: extract TODOs and FIXMEs
    result["todos"] = _extract_todos(content)
    result["fixmes"] = _extract_fixmes(content)

    # Infer file purpose from its path and content
    result["purpose"] = _infer_purpose(rel_path, content, result)

    return result


def _analyze_python(content: str, result: dict):
    """Parse Python AST to extract structure."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    imports = []
    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split(".")[0])

        elif isinstance(node, ast.ClassDef):
            methods = [
                m.name for m in ast.walk(node)
                if isinstance(m, ast.FunctionDef) and m != node
            ]
            bases = [
                ast.unparse(b) if hasattr(ast, 'unparse') else getattr(b, 'id', '?')
                for b in node.bases
            ]
            docstring = ast.get_docstring(node) or ""
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "methods": methods[:20],
                "bases": bases,
                "docstring": docstring[:200],
            })

        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            # Only top-level functions (not methods inside classes)
            pass

    # Re-walk for top-level functions only
    for node in ast.iter_child_nodes(ast.parse(content)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node) or ""
            args = [a.arg for a in node.args.args]
            is_async = isinstance(node, ast.AsyncFunctionDef)
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "args": args,
                "is_async": is_async,
                "docstring": docstring[:200],
                "is_private": node.name.startswith("_"),
            })

    result["imports"] = list(dict.fromkeys(imports))  # deduplicate, preserve order
    result["classes"] = classes
    result["functions"] = functions
    result["dependencies"] = [i for i in imports if not _is_stdlib(i)]


def _is_stdlib(module: str) -> bool:
    """Rough check if a module is from Python stdlib."""
    STDLIB = {
        "os", "sys", "re", "json", "math", "time", "datetime", "typing",
        "pathlib", "shutil", "collections", "itertools", "functools",
        "io", "abc", "enum", "dataclasses", "contextlib", "asyncio",
        "threading", "multiprocessing", "subprocess", "socket", "http",
        "urllib", "hashlib", "hmac", "secrets", "random", "string",
        "struct", "copy", "weakref", "gc", "inspect", "traceback",
        "logging", "warnings", "unittest", "tempfile", "glob", "fnmatch",
        "csv", "xml", "html", "ast", "dis", "code", "pprint", "textwrap",
        "base64", "binascii", "uuid", "heapq", "bisect", "array",
        "queue", "signal", "platform", "argparse", "configparser",
        "__future__", "builtins",
    }
    return module in STDLIB


def _analyze_javascript(content: str, result: dict):
    """Parse JS/TS files using regex to extract imports, exports, functions, classes."""
    # Imports: import X from 'y' or require('y')
    import_patterns = [
        r"(?:import\s+.*?\s+from\s+)['\"]([^'\"]+)['\"]",
        r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
    ]
    imports = []
    for pat in import_patterns:
        imports.extend(re.findall(pat, content))

    # Filter to only external packages (no relative paths)
    external = [i for i in imports if not i.startswith(".") and not i.startswith("/")]
    # Strip scope prefix for display: @scope/pkg → scope/pkg
    result["imports"] = list(dict.fromkeys(external))
    result["dependencies"] = list(dict.fromkeys(external))

    # Exports
    exports = re.findall(r"export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)", content)
    result["exports"] = exports

    # Functions (arrow and traditional)
    func_patterns = [
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(",
        r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>",
        r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function",
    ]
    functions = []
    for pat in func_patterns:
        functions.extend(re.findall(pat, content))
    result["functions"] = [{"name": f, "line": 0, "is_async": False} for f in dict.fromkeys(functions)]

    # Classes
    class_matches = re.findall(r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?", content)
    result["classes"] = [
        {"name": m[0], "bases": [m[1]] if m[1] else [], "line": 0}
        for m in class_matches
    ]


def _analyze_java(content: str, result: dict):
    """Extract Java imports and class structure via regex."""
    imports = re.findall(r"import\s+([\w.]+)\s*;", content)
    result["imports"] = imports
    result["dependencies"] = [i.split(".")[0] for i in imports if not i.startswith("java.")]

    classes = re.findall(r"(?:public\s+)?(?:abstract\s+)?class\s+(\w+)", content)
    result["classes"] = [{"name": c, "line": 0} for c in classes]

    methods = re.findall(
        r"(?:public|private|protected|static|final|void|async)[\s\w<>[\],]+\s+(\w+)\s*\(", content
    )
    result["functions"] = [{"name": m, "line": 0} for m in methods[:30]]


def _analyze_go(content: str, result: dict):
    """Extract Go imports and function structure via regex."""
    # Single imports
    imports = re.findall(r'import\s+"([^"]+)"', content)
    # Block imports
    block = re.findall(r'"([^"]+)"', content)
    all_imports = list(dict.fromkeys(imports + block))
    result["imports"] = all_imports
    result["dependencies"] = [i for i in all_imports if "/" in i]

    funcs = re.findall(r"func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(", content)
    result["functions"] = [{"name": f, "line": 0} for f in funcs]


def _extract_todos(content: str) -> list[dict]:
    """Extract TODO comments from file."""
    todos = []
    for i, line in enumerate(content.splitlines(), 1):
        if "TODO" in line:
            stripped = line.strip().lstrip("#").lstrip("//").lstrip("*").strip()
            todos.append({"line": i, "text": stripped[:200]})
    return todos[:20]  # Cap at 20


def _extract_fixmes(content: str) -> list[dict]:
    """Extract FIXME comments from file."""
    fixmes = []
    for i, line in enumerate(content.splitlines(), 1):
        if "FIXME" in line or "HACK" in line or "XXX" in line:
            stripped = line.strip().lstrip("#").lstrip("//").lstrip("*").strip()
            fixmes.append({"line": i, "text": stripped[:200]})
    return fixmes[:20]


def _infer_purpose(rel_path: str, content: str, result: dict) -> str:
    """Infer the purpose of a file from its name, path, and content."""
    name = Path(rel_path).name.lower()
    parts = rel_path.lower().split("/")

    # Config files
    if name in {"package.json", "pyproject.toml", "cargo.toml", "pom.xml"}:
        return "Project configuration and dependency manifest"
    if name in {".env", ".env.example", ".env.local"}:
        return "Environment variable configuration"
    if name in {"dockerfile"}:
        return "Docker container build instructions"
    if name in {"docker-compose.yml", "docker-compose.yaml"}:
        return "Docker multi-service orchestration"
    if name in {"readme.md", "readme.txt", "readme.rst"}:
        return "Project documentation and overview"
    if name in {".gitignore", ".dockerignore"}:
        return "Version control ignore rules"
    if name in {"makefile"}:
        return "Build automation commands"

    # By path component
    if "test" in parts or "spec" in parts or "__tests__" in parts or name.startswith("test_"):
        return "Test suite"
    if "migration" in parts or "migrations" in parts:
        return "Database migration script"
    if "model" in parts or "models" in parts:
        return "Data model definition"
    if "view" in parts or "views" in parts:
        return "View/template handler"
    if "controller" in parts or "controllers" in parts:
        return "Request controller"
    if "route" in parts or "routes" in parts:
        return "URL route definitions"
    if "service" in parts or "services" in parts:
        return "Business logic service"
    if "middleware" in parts or "middlewares" in parts:
        return "Request middleware"
    if "util" in parts or "utils" in parts or "helper" in parts or "helpers" in parts:
        return "Utility/helper functions"
    if "config" in parts or "settings" in parts:
        return "Configuration module"
    if "auth" in parts or "security" in parts:
        return "Authentication and authorization"
    if "component" in parts or "components" in parts:
        return "Reusable UI component"
    if "page" in parts or "pages" in parts:
        return "Application page"
    if "hook" in parts or "hooks" in parts:
        return "Custom hook"
    if "store" in parts or "context" in parts:
        return "State management"
    if "api" in parts:
        return "API endpoint handler"

    # By name
    if "main" in name or "index" in name or "app" in name or "server" in name:
        return "Application entry point"
    if "init" in name:
        return "Package/module initializer"
    if "schema" in name:
        return "Data schema definition"
    if "seed" in name:
        return "Database seed data"

    return f"Source file ({Path(rel_path).suffix.lstrip('.').upper()} module)"


def _empty_analysis(path: str, reason: str) -> dict:
    return {
        "path": path,
        "extension": Path(path).suffix.lower(),
        "line_count": 0,
        "non_empty_lines": 0,
        "size_bytes": 0,
        "imports": [],
        "classes": [],
        "functions": [],
        "exports": [],
        "todos": [],
        "fixmes": [],
        "purpose": reason,
        "dependencies": [],
    }
