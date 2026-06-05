#!/usr/bin/env python3
"""Check that relative Markdown links resolve to files in the repository.

This is a minimal, dependency-free link checker for continuous integration.
It only checks *relative* links and image paths. External links (http, https,
mailto) and pure in-page anchors (``#section``) are intentionally skipped so
the check stays fast and reliable and does not require network access.

Usage:
  python .github/scripts/check_markdown_links.py

Exit status:
  0 if all relative links resolve, non-zero otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Repository root is two levels up from this file (.github/scripts/<file>).
REPO_ROOT = Path(__file__).resolve().parents[2]

# Markdown inline link / image syntax: [text](target) and ![alt](target).
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")

# Directories we do not scan.
SKIP_DIRS = {".git", ".lean-ctx", "node_modules"}


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for path in REPO_ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(REPO_ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def extract_targets(text: str) -> list[str]:
    return [m.group(1).strip() for m in LINK_RE.finditer(text)]


def normalize_target(target: str) -> str:
    # Drop any in-page anchor fragment and surrounding angle brackets/quotes.
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    # A link may be "path "title"" - keep only the path portion.
    if " " in target and not target.startswith("#"):
        target = target.split(" ", 1)[0]
    target = target.split("#", 1)[0]
    return target


def main() -> int:
    problems: list[str] = []
    md_files = iter_markdown_files()

    for md in md_files:
        text = md.read_text(encoding="utf-8")
        for raw_target in extract_targets(text):
            if raw_target.startswith(SKIP_PREFIXES):
                continue
            target = normalize_target(raw_target)
            if not target or target.startswith(SKIP_PREFIXES):
                continue
            resolved = (md.parent / target).resolve()
            if not resolved.exists():
                rel = md.relative_to(REPO_ROOT)
                problems.append(f"{rel}: broken relative link -> '{raw_target}'")

    if problems:
        print("Markdown link check FAILED:")
        for problem in problems:
            print(f"  - {problem}")
        print(f"\n{len(problems)} broken link(s) found.")
        return 1

    print(f"Markdown link check PASSED. Scanned {len(md_files)} file(s); "
          f"all relative links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
