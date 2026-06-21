"""Fail when tracked repository content violates portfolio safety rules."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

MAX_TRACKED_BYTES = 5 * 1024 * 1024
FORBIDDEN_NAMES = {".env", ".env.local"}
FORBIDDEN_PARTS = {
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".venv",
}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".xlsx", ".xls"}
IGNORED_REPORTS = {"reports/local_sentiment_report.md"}
UNSUPPORTED_CLAIMS = re.compile(
    "|".join(
        (
            "production-ready " + "sentiment model",
            "guaranteed " + "accurate",
            "fully automated " + "business decisioning",
            "state-of-" + "the-art",
        )
    ),
    re.IGNORECASE,
)
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE = re.compile(r"(?<!\d)(?:\+?66|0)[689]\d{8}(?!\d)")
SECRET = re.compile(r"\b(?:sk|ghp|github_pat)_[A-Za-z0-9_-]{16,}\b")
TEXT_SUFFIXES = {".csv", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}
PII_DATA_SUFFIXES = {".csv", ".json"}
APPROVED_PUBLIC_DATA = {"data/raw/wisesight_source.json"}
APPROVED_SYNTHETIC_DATA = {
    "data/sample/sample_reviews.csv",
    "data/sample/synthetic_reviews.json",
}


def find_text_violations(files: dict[str, str]) -> list[str]:
    findings = []
    for path, text in sorted(files.items()):
        if UNSUPPORTED_CLAIMS.search(text):
            findings.append(f"{path}: unsupported-claim")
        if SECRET.search(text):
            findings.append(f"{path}: secret-like-value")
        suffix = Path(path).suffix.lower()
        if suffix in PII_DATA_SUFFIXES and path not in APPROVED_PUBLIC_DATA | APPROVED_SYNTHETIC_DATA:
            if EMAIL.search(text):
                findings.append(f"{path}: email-like-data")
            if PHONE.search(text):
                findings.append(f"{path}: phone-like-data")
    return findings


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    return [Path(path.decode()) for path in result.stdout.split(b"\0") if path]


def scan_repo() -> list[str]:
    findings = []
    text_files: dict[str, str] = {}
    for path in tracked_files():
        posix = path.as_posix()
        if path.name in FORBIDDEN_NAMES:
            findings.append(f"{posix}: forbidden-environment-file")
        if FORBIDDEN_PARTS.intersection(path.parts):
            findings.append(f"{posix}: generated-or-cache-path")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"{posix}: forbidden-data-artifact")
        if posix in IGNORED_REPORTS:
            findings.append(f"{posix}: ignored-generated-report")
        if path.is_file() and path.stat().st_size > MAX_TRACKED_BYTES:
            findings.append(f"{posix}: exceeds-5-MiB")
        if path.suffix.lower() == ".ipynb" and path.is_file():
            notebook = json.loads(path.read_text(encoding="utf-8"))
            if any(cell.get("outputs") for cell in notebook.get("cells", [])):
                findings.append(f"{posix}: notebook-has-outputs")
        if path.suffix.lower() in TEXT_SUFFIXES and path.is_file():
            text_files[posix] = path.read_text(encoding="utf-8", errors="replace")
    findings.extend(find_text_violations(text_files))
    return sorted(findings)


def main() -> None:
    findings = scan_repo()
    if findings:
        print("repository guardrails failed:")
        for finding in findings:
            print(f"- {finding}")
        raise SystemExit(1)
    print("repository guardrails passed")


if __name__ == "__main__":
    main()
