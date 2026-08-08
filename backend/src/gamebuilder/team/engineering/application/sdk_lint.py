"""Static checks for LLM-authored SDK JavaScript (deny dangerous browser APIs)."""

from __future__ import annotations

import re

# Patterns that should never appear in sandboxed game JS.
_DENIED_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("eval", re.compile(r"\beval\s*\(")),
    ("Function constructor", re.compile(r"\bFunction\s*\(")),
    ("fetch", re.compile(r"\bfetch\s*\(")),
    ("XMLHttpRequest", re.compile(r"\bXMLHttpRequest\b")),
    ("WebSocket", re.compile(r"\bWebSocket\b")),
    ("Worker", re.compile(r"\bWorker\s*\(")),
    ("importScripts", re.compile(r"\bimportScripts\s*\(")),
    ("dynamic import", re.compile(r"\bimport\s*\(")),
    ("document.cookie", re.compile(r"document\.cookie")),
    ("localStorage", re.compile(r"\blocalStorage\b")),
    ("sessionStorage", re.compile(r"\bsessionStorage\b")),
    ("indexedDB", re.compile(r"\bindexedDB\b")),
    ("window.parent", re.compile(r"window\.parent")),
    ("window.top", re.compile(r"window\.top")),
    ("window.opener", re.compile(r"window\.opener")),
    ("postMessage outbound", re.compile(r"\.postMessage\s*\(")),
]


def lint_sdk_javascript(source: str, *, max_chars: int = 80_000) -> list[str]:
    """Return human-readable violation messages (empty = pass)."""
    issues: list[str] = []
    if not source or not source.strip():
        issues.append("SDK source is empty")
        return issues
    if len(source) > max_chars:
        issues.append(f"SDK source exceeds {max_chars} characters")
    if "Cyborg.boot" not in source and "Cyborg.boot(" not in source:
        issues.append("SDK source must call Cyborg.boot(...)")
    for label, pattern in _DENIED_PATTERNS:
        if pattern.search(source):
            issues.append(f"Forbidden API: {label}")
    return issues
