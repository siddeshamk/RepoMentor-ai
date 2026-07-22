"""
Code quality analyzer: identifies maintainability issues, large files,
long functions, dead code patterns, and technical debt.
"""
import ast
import re
from pathlib import Path
from typing import Any

from app.utils.file_utils import walk_repo, read_file_safe, get_relative_path
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Thresholds
MAX_FILE_LINES = 300
MAX_FUNCTION_LINES = 50
MAX_FUNCTION_PARAMS = 7
MAX_NESTING_DEPTH = 5


def analyze_quality(repo_path: Path) -> dict:
    """
    Analyze code quality across the entire repository.
    Returns a structured quality report.
    """
    large_files: list[dict] = []
    long_functions: list[dict] = []
    complex_functions: list[dict] = []
    all_todos: list[dict] = []
    all_fixmes: list[dict] = []
    duplicate_candidates: list[dict] = []
    unused_import_files: list[dict] = []
    total_files = 0
    total_lines = 0

    for file_path in walk_repo(repo_path, max_files=2000):
        content = read_file_safe(file_path)
        if content is None:
            continue

        total_files += 1
        rel_path = get_relative_path(file_path, repo_path)
        lines = content.splitlines()
        line_count = len(lines)
        total_lines += line_count

        # Large file detection
        if line_count > MAX_FILE_LINES:
            large_files.append({
                "file": rel_path,
                "lines": line_count,
                "severity": "high" if line_count > 600 else "medium",
                "message": f"File has {line_count} lines (threshold: {MAX_FILE_LINES}). Consider splitting it.",
            })

        # TODOs and FIXMEs
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if "TODO" in stripped or "todo" in stripped:
                all_todos.append({"file": rel_path, "line": i, "text": stripped[:200]})
            if "FIXME" in stripped or "HACK" in stripped:
                all_fixmes.append({"file": rel_path, "line": i, "text": stripped[:200]})

        # Python-specific analysis
        if file_path.suffix == ".py":
            _analyze_python_quality(
                content, rel_path, long_functions, complex_functions, unused_import_files
            )

        # JS/TS-specific
        elif file_path.suffix in {".js", ".jsx", ".ts", ".tsx"}:
            _analyze_js_quality(content, rel_path, long_functions)

    # Compute quality scores
    score_issues = (
        len(large_files) * 3 +
        len(long_functions) * 2 +
        len(complex_functions) * 4 +
        min(len(all_todos), 20) * 1 +
        min(len(all_fixmes), 20) * 2
    )
    maintainability_score = max(0, 100 - score_issues)

    return {
        "large_files": large_files[:50],
        "long_functions": long_functions[:50],
        "complex_functions": complex_functions[:30],
        "todos": all_todos[:100],
        "fixmes": all_fixmes[:50],
        "unused_imports": unused_import_files[:30],
        "summary": {
            "total_files": total_files,
            "total_lines": total_lines,
            "large_file_count": len(large_files),
            "long_function_count": len(long_functions),
            "todo_count": len(all_todos),
            "fixme_count": len(all_fixmes),
        },
        "maintainability_score": maintainability_score,
    }


def _analyze_python_quality(
    content: str,
    rel_path: str,
    long_functions: list,
    complex_functions: list,
    unused_imports: list,
):
    """Python AST-based quality analysis."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return

    lines = content.splitlines()

    # Analyze functions/methods
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            func_lines = end_line - start_line + 1

            # Long function
            if func_lines > MAX_FUNCTION_LINES:
                long_functions.append({
                    "file": rel_path,
                    "function": node.name,
                    "line": start_line,
                    "lines": func_lines,
                    "severity": "high" if func_lines > 100 else "medium",
                    "message": f"Function '{node.name}' has {func_lines} lines (threshold: {MAX_FUNCTION_LINES}).",
                })

            # Too many parameters
            param_count = len(node.args.args)
            if param_count > MAX_FUNCTION_PARAMS:
                complex_functions.append({
                    "file": rel_path,
                    "function": node.name,
                    "line": start_line,
                    "params": param_count,
                    "issue": "too_many_params",
                    "message": f"Function '{node.name}' has {param_count} parameters. Consider using a config object.",
                })

    # Unused imports (simple check: import name never used in file)
    imported_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.append((alias.asname or alias.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.append((alias.asname or alias.name, node.lineno))

    if imported_names:
        unused = []
        for name, lineno in imported_names:
            if name == "*":
                continue
            # Count occurrences in source (excluding import line)
            occurrences = content.count(name)
            if occurrences <= 1:  # Only on import line itself
                unused.append({"name": name, "line": lineno})

        if unused:
            unused_imports.append({
                "file": rel_path,
                "unused": unused[:10],
            })


def _analyze_js_quality(content: str, rel_path: str, long_functions: list):
    """JS/TS function length analysis via brace counting."""
    lines = content.splitlines()
    # Simple heuristic: find function declarations and estimate length
    func_starts: list[tuple[str, int]] = []

    func_pattern = re.compile(
        r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(|"
        r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>"
    )

    for i, line in enumerate(lines, 1):
        m = func_pattern.search(line)
        if m:
            name = m.group(1) or m.group(2) or "anonymous"
            func_starts.append((name, i))

    # Estimate function lengths (difference between consecutive start lines)
    for idx, (name, start) in enumerate(func_starts):
        if idx + 1 < len(func_starts):
            estimated_lines = func_starts[idx + 1][1] - start
        else:
            estimated_lines = len(lines) - start

        if estimated_lines > MAX_FUNCTION_LINES:
            long_functions.append({
                "file": rel_path,
                "function": name,
                "line": start,
                "lines": estimated_lines,
                "severity": "high" if estimated_lines > 100 else "medium",
                "message": f"Function '{name}' is approximately {estimated_lines} lines long.",
            })
