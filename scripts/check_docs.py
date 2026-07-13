#!/usr/bin/env python3
"""Validate tracked Markdown links, anchors, and fenced code blocks."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


FENCE_RE = re.compile(r"^ {0,3}(?P<fence>`{3,}|~{3,})")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}\s+(?P<heading>.+?)\s*#*\s*$")
EXPLICIT_ANCHOR_RE = re.compile(
    r"<a\s+(?:[^>]*?\s)?(?:id|name)=[\"'](?P<anchor>[^\"']+)[\"']",
    re.IGNORECASE,
)
INLINE_LINK_RE = re.compile(
    r"!?\[[^\]]*\]\(\s*(?P<destination><[^>\n]+>|[^\s)]+)",
)
REFERENCE_LINK_RE = re.compile(
    r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(?P<destination><[^>\n]+>|\S+)",
)
INLINE_CODE_RE = re.compile(r"(`+).*?\1")
MARKDOWN_LINK_TEXT_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
HTML_TAG_RE = re.compile(r"<[^>]+>")
MARKDOWN_FORMATTING_RE = re.compile(r"[`*_~]")
TEMPLATED_DESTINATION_CHARS = frozenset("<>{}$")


@dataclass(frozen=True, order=True)
class Finding:
    """One actionable Markdown validation failure."""

    path: Path
    line: int
    message: str


def _content_lines(path: Path) -> tuple[list[tuple[int, str]], Finding | None]:
    """Return lines outside code fences and an unclosed-fence finding, if any."""
    content_lines: list[tuple[int, str]] = []
    opening_fence: tuple[str, int, int] | None = None
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = FENCE_RE.match(line)
        if match:
            fence = match.group("fence")
            if opening_fence is None:
                opening_fence = (fence[0], len(fence), line_number)
                continue
            fence_character, minimum_length, _ = opening_fence
            remainder = line[match.end() :]
            if (
                fence[0] == fence_character
                and len(fence) >= minimum_length
                and not remainder.strip()
            ):
                opening_fence = None
            continue
        if opening_fence is None:
            content_lines.append((line_number, line))

    if opening_fence is None:
        return content_lines, None
    _, _, line_number = opening_fence
    return content_lines, Finding(path, line_number, "unclosed fenced code block")


def _slugify_heading(heading: str) -> str:
    """Approximate GitHub's heading-slug algorithm for repository link checks."""
    heading = MARKDOWN_LINK_TEXT_RE.sub(r"\1", heading)
    heading = HTML_TAG_RE.sub("", heading)
    heading = MARKDOWN_FORMATTING_RE.sub("", heading)
    heading = heading.lower().strip()
    heading = re.sub(r"[^\w\- ]", "", heading)
    return heading.replace(" ", "-")


def _anchors(path: Path) -> set[str]:
    """Return GitHub-style heading anchors and explicit HTML anchors in a document."""
    content_lines, _ = _content_lines(path)
    anchors: set[str] = set()
    slug_counts: defaultdict[str, int] = defaultdict(int)
    for _, line in content_lines:
        for explicit_match in EXPLICIT_ANCHOR_RE.finditer(line):
            anchors.add(explicit_match.group("anchor"))
        heading_match = HEADING_RE.match(line)
        if heading_match is None:
            continue
        base_slug = _slugify_heading(heading_match.group("heading"))
        duplicate_number = slug_counts[base_slug]
        slug_counts[base_slug] += 1
        slug = base_slug if duplicate_number == 0 else f"{base_slug}-{duplicate_number}"
        anchors.add(slug)
    return anchors


def _destinations(line: str) -> list[str]:
    """Extract inline and reference-style Markdown link destinations from one line."""
    line = INLINE_CODE_RE.sub("", line)
    destinations = [match.group("destination") for match in INLINE_LINK_RE.finditer(line)]
    reference_match = REFERENCE_LINK_RE.match(line)
    if reference_match is not None:
        destinations.append(reference_match.group("destination"))
    return destinations


def _normalize_destination(destination: str) -> str:
    destination = destination.strip()
    if destination.startswith("<") and destination.endswith(">"):
        destination = destination[1:-1]
    return unquote(destination)


def _is_local_destination(destination: str) -> bool:
    if not destination or destination.startswith("/"):
        return False
    if any(character in destination for character in TEMPLATED_DESTINATION_CHARS):
        return False
    return not urlsplit(destination).scheme


def check_markdown_files(root: Path, paths: list[Path]) -> list[Finding]:
    """Validate relative links, anchors, and fences in the supplied Markdown files."""
    root = root.resolve()
    findings: list[Finding] = []
    anchor_cache: dict[Path, set[str]] = {}

    for path in paths:
        path = path.resolve()
        content_lines, fence_finding = _content_lines(path)
        if fence_finding is not None:
            findings.append(fence_finding)
        for line_number, line in content_lines:
            for raw_destination in _destinations(line):
                destination = _normalize_destination(raw_destination)
                if not _is_local_destination(destination):
                    continue
                split_destination = urlsplit(destination)
                relative_path = split_destination.path
                target = path if not relative_path else (path.parent / relative_path)
                target = target.resolve()
                if not target.exists():
                    findings.append(
                        Finding(
                            path,
                            line_number,
                            f"link target does not exist: {raw_destination}",
                        )
                    )
                    continue
                fragment = split_destination.fragment
                if not fragment:
                    continue
                anchor_target = target / "README.md" if target.is_dir() else target
                if anchor_target.suffix.lower() != ".md" or not anchor_target.is_file():
                    continue
                target_anchors = anchor_cache.setdefault(
                    anchor_target, _anchors(anchor_target)
                )
                if fragment not in target_anchors:
                    findings.append(
                        Finding(
                            path,
                            line_number,
                            f"link anchor does not exist: {raw_destination}",
                        )
                    )

    return sorted(findings)


def _tracked_markdown_files(root: Path) -> list[Path]:
    """List Markdown files in Git's index so ignored caches and local drafts stay out."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [root / path.decode() for path in result.stdout.split(b"\0") if path]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Markdown files to validate (default: all tracked Markdown files)",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    root = Path.cwd().resolve()
    paths = [path if path.is_absolute() else root / path for path in args.paths]
    if not paths:
        paths = _tracked_markdown_files(root)
    findings = check_markdown_files(root, paths)
    for finding in findings:
        try:
            display_path = finding.path.relative_to(root)
        except ValueError:
            display_path = finding.path
        print(f"{display_path}:{finding.line}: {finding.message}")
    if findings:
        print(f"Markdown validation failed with {len(findings)} finding(s).")
        return 1
    print(f"Markdown validation passed for {len(paths)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
