# -*- coding: utf-8 -*-
"""Fail if a relative Markdown link points at a missing file."""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)\)")
SKIP_DIRS = {".git", ".superpowers", "superpowers", "__pycache__", "node_modules"}


def markdown_files():
    for p in ROOT.rglob("*.md"):
        if not SKIP_DIRS & set(p.relative_to(ROOT).parts):
            yield p


def broken(path):
    text = path.read_text(encoding="utf-8")
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        rel = unquote(target.split("#", 1)[0])
        if rel and not (path.parent / rel).exists():
            yield target


def main():
    failures = 0
    for path in sorted(markdown_files()):
        for target in broken(path):
            failures += 1
            print(f"{path.relative_to(ROOT)}: missing {target}")
    if failures:
        print(f"{failures} broken link(s)")
        return 1
    print("all relative Markdown links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
