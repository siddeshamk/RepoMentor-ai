"""
Security analyzer: scans repository files for hardcoded secrets,
insecure patterns, and potential vulnerabilities.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from app.utils.file_utils import walk_repo, read_file_safe, get_relative_path
from app.utils.logger import get_logger

logger = get_logger(__name__)

Severity = Literal["critical", "high", "medium", "low", "info"]


@dataclass
class SecurityFinding:
    file: str
    line: int
    severity: Severity
    category: str
    title: str
    description: str
    snippet: str = ""


# Patterns: (regex, severity, category, title, description)
SECRET_PATTERNS: list[tuple] = [
    # High-entropy secrets / API keys
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?',
     "critical", "Hardcoded Secret", "API Key Exposed",
     "A hardcoded API key was found. Store secrets in environment variables."),

    (r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*["\']?([A-Za-z0-9_\-]{16,})["\']?',
     "critical", "Hardcoded Secret", "Secret Key Exposed",
     "A hardcoded secret key was found. Use environment variables or a secrets manager."),

    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']',
     "critical", "Hardcoded Secret", "Hardcoded Password",
     "A hardcoded password was found. Never commit passwords to source code."),

    (r'(?i)(access[_-]?token|auth[_-]?token|bearer[_-]?token)\s*[=:]\s*["\']([A-Za-z0-9_\-\.]{20,})["\']',
     "critical", "Hardcoded Secret", "Access Token Exposed",
     "A hardcoded access token was found. Store tokens in environment variables."),

    (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[=:]\s*["\']?([A-Z0-9]{20})["\']?',
     "critical", "Cloud Credentials", "AWS Access Key ID Exposed",
     "AWS Access Key ID detected. Rotate immediately and remove from codebase."),

    (r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\']?([A-Za-z0-9+/]{40})["\']?',
     "critical", "Cloud Credentials", "AWS Secret Access Key Exposed",
     "AWS Secret Access Key detected. Rotate immediately."),

    (r'(?i)(private[_-]?key|rsa[_-]?key)\s*[=:]\s*["\']([A-Za-z0-9+/=]{40,})["\']',
     "critical", "Hardcoded Secret", "Private Key Exposed",
     "A private key was found in source code. Remove immediately."),

    (r'-----BEGIN (RSA|EC|DSA|OPENSSH|PGP) PRIVATE KEY-----',
     "critical", "Hardcoded Secret", "Private Key in Source Code",
     "A PEM-encoded private key was found in source code. Never commit private keys."),

    (r'(?i)(database[_-]?url|db[_-]?url|connection[_-]?string)\s*[=:]\s*["\']([^"\']+://[^"\']+)["\']',
     "high", "Database Credentials", "Database Connection String Exposed",
     "A database connection string with credentials may be exposed."),

    (r'(?i)(github[_-]?token|ghp_[A-Za-z0-9]{36})',
     "critical", "Cloud Credentials", "GitHub Token Exposed",
     "A GitHub personal access token was found. Revoke and regenerate immediately."),

    (r'(?i)(stripe[_-]?secret|sk_live_[A-Za-z0-9]+)',
     "critical", "Payment Credentials", "Stripe Secret Key Exposed",
     "A Stripe secret key was found. Revoke immediately at dashboard.stripe.com."),

    # SQL Injection
    (r'(?i)(?:execute|query|cursor\.execute)\s*\(\s*["\']?\s*(?:SELECT|INSERT|UPDATE|DELETE).*?%s',
     "high", "SQL Injection", "Potential SQL Injection",
     "String formatting used in SQL query. Use parameterized queries instead."),

    (r'(?i)(?:execute|query)\s*\(\s*f["\'].*?(?:SELECT|INSERT|UPDATE|DELETE)',
     "high", "SQL Injection", "F-String in SQL Query",
     "F-string interpolation in SQL is dangerous. Use parameterized queries."),

    # Unsafe patterns
    (r'(?i)eval\s*\(',
     "medium", "Code Injection", "Use of eval()",
     "eval() can execute arbitrary code. Use safer alternatives."),

    (r'(?i)exec\s*\(',
     "medium", "Code Injection", "Use of exec()",
     "exec() can execute arbitrary code strings. Avoid unless absolutely necessary."),

    (r'(?i)subprocess\.call\s*\(\s*shell\s*=\s*True',
     "high", "Command Injection", "shell=True in subprocess",
     "Using shell=True is a command injection risk. Pass arguments as a list instead."),

    (r'(?i)os\.system\s*\(',
     "medium", "Command Injection", "Use of os.system()",
     "os.system() is vulnerable to command injection. Use subprocess with a list instead."),

    # Weak crypto
    (r'(?i)hashlib\.md5\s*\(|hashlib\.sha1\s*\(',
     "medium", "Weak Cryptography", "Weak Hashing Algorithm",
     "MD5 and SHA1 are cryptographically broken. Use SHA-256 or better."),

    (r'(?i)random\.random\s*\(\s*\)|random\.randint',
     "low", "Weak Cryptography", "Non-Cryptographic Random",
     "Python's random module is not cryptographically secure. Use secrets module for security-sensitive randomness."),

    # Debug / info disclosure
    (r'(?i)debug\s*=\s*True',
     "medium", "Information Disclosure", "Debug Mode Enabled",
     "Debug mode exposes stack traces and sensitive info. Disable in production."),

    (r'(?i)print\s*\(.*(?:password|secret|token|key)',
     "low", "Information Disclosure", "Sensitive Data Printed",
     "Printing sensitive data to console may expose it in logs."),

    # Missing auth
    (r'(?i)@app\.route\s*\(.*\)\s*\n(?:.*\n)*?def\s+\w+',
     "info", "Authentication", "Unauthenticated Route",
     "This route may be missing authentication decorators. Verify access control."),
]


def analyze_security(repo_path: Path) -> dict:
    """
    Scan all text files in the repository for security issues.
    Returns a structured report with findings by severity.
    """
    findings: list[dict] = []
    skipped_files: list[str] = []

    # Skip files that are unlikely to have issues
    SKIP_EXTENSIONS = {".md", ".txt", ".rst", ".lock", ".log", ".map"}
    # Skip test files for some patterns (reduce false positives)
    TEST_DIRS = {"test", "tests", "spec", "__tests__", "mocks", "fixtures"}

    for file_path in walk_repo(repo_path, max_files=2000):
        if file_path.suffix.lower() in SKIP_EXTENSIONS:
            continue

        # Skip lock files and minified files
        name = file_path.name.lower()
        if name.endswith((".lock", ".min.js", ".min.css")):
            continue

        content = read_file_safe(file_path)
        if content is None:
            skipped_files.append(str(file_path))
            continue

        rel_path = get_relative_path(file_path, repo_path)
        is_test_file = any(p in rel_path.lower().split("/") for p in TEST_DIRS)

        lines = content.splitlines()
        for pattern, severity, category, title, description in SECRET_PATTERNS:
            # Reduce false positives: skip some patterns in test files
            if is_test_file and category in {"Authentication"}:
                continue

            for i, line in enumerate(lines, 1):
                # Skip commented-out lines
                stripped = line.strip()
                if stripped.startswith(("#", "//", "*", "<!--")):
                    continue

                if re.search(pattern, line):
                    snippet = line.strip()[:150]
                    # Mask the actual secret in the snippet
                    snippet = re.sub(
                        r'(["\'])[A-Za-z0-9+/=_\-]{12,}(["\'])',
                        r'\1***REDACTED***\2',
                        snippet
                    )
                    findings.append({
                        "file": rel_path,
                        "line": i,
                        "severity": severity,
                        "category": category,
                        "title": title,
                        "description": description,
                        "snippet": snippet,
                    })
                    break  # One finding per pattern per file

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda f: severity_order.get(f["severity"], 5))

    # Count by severity
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    # Compute security score (0-100, higher = safer)
    score = 100
    score -= counts.get("critical", 0) * 25
    score -= counts.get("high", 0) * 15
    score -= counts.get("medium", 0) * 8
    score -= counts.get("low", 0) * 3
    score = max(0, score)

    return {
        "findings": findings,
        "summary": counts,
        "total": len(findings),
        "score": score,
        "risk_level": _risk_level(score),
    }


def _risk_level(score: int) -> str:
    if score >= 90:
        return "Low Risk"
    elif score >= 70:
        return "Moderate Risk"
    elif score >= 50:
        return "High Risk"
    else:
        return "Critical Risk"
