#!/usr/bin/env python3
"""Regenerate committed lockfile inventories from pinned upstream lockfiles."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_DIRECTORY = REPOSITORY_ROOT / "docs" / "project" / "research" / "data"
EXTRACTOR = DATA_DIRECTORY / "extract_lockfile_inventory.py"
ARTIFACT_SUFFIXES = (
    "package-inventory.tsv",
    "summary.json",
    "top-owners.json",
)
DOWNLOAD_ATTEMPTS = 3
DOWNLOAD_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class UpstreamSource:
    """Immutable source and integrity metadata for one research inventory."""

    project: str
    repository: str
    commit: str
    sha256: str

    @property
    def url(self) -> str:
        return (
            "https://raw.githubusercontent.com/"
            f"{self.repository}/{self.commit}/pnpm-lock.yaml"
        )


UPSTREAM_SOURCES = (
    UpstreamSource(
        project="tbd",
        repository="jlevy/tbd",
        commit="395052437464a9e62ce209220dcc01096fa06f7e",
        sha256="8dccc48e13afff544d26a704057e1beb147b543e97d8c67fee512a87b274945b",
    ),
    UpstreamSource(
        project="qmd",
        repository="tobi/qmd",
        commit="443760f4d5a17550d77a0e3146b5b8f08452991f",
        sha256="3d2312e5d7b5065f8e95272d604478a98ba2bd1d089337461a6156dd55768cbb",
    ),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate committed tbd and qmd lockfile inventories and fail on drift."
        )
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help=(
            "use local <project>-pnpm-lock.yaml files instead of downloading the "
            "pinned upstream sources (intended for tests)"
        ),
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIRECTORY,
        help="directory containing the committed inventory artifacts",
    )
    return parser.parse_args()


def _download(source: UpstreamSource, destination: Path) -> None:
    request = urllib.request.Request(
        source.url,
        headers={"User-Agent": "rust-porting-playbook-lockfile-check/1"},
    )
    last_error: Exception | None = None
    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(
                request, timeout=DOWNLOAD_TIMEOUT_SECONDS
            ) as response:
                contents = response.read()
            digest = hashlib.sha256(contents).hexdigest()
            if digest != source.sha256:
                raise RuntimeError(
                    f"SHA-256 mismatch for {source.url}: expected {source.sha256}, "
                    f"received {digest}"
                )
            destination.write_bytes(contents)
            return
        except (OSError, TimeoutError, urllib.error.URLError) as error:
            last_error = error
            if attempt < DOWNLOAD_ATTEMPTS:
                time.sleep(attempt)
    raise RuntimeError(
        f"Unable to download {source.url} after {DOWNLOAD_ATTEMPTS} attempts: "
        f"{last_error}"
    )


def _run_extractor(source: Path, project: str, output_prefix: Path) -> None:
    environment = os.environ.copy()
    environment.pop("UV_EXCLUDE_NEWER", None)
    environment["UV_NO_BUILD"] = "1"
    result = subprocess.run(
        [
            "uv",
            "--no-config",
            "run",
            "--locked",
            "--script",
            str(EXTRACTOR),
            str(source),
            project,
            str(output_prefix),
        ],
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        env=environment,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Inventory extraction failed for {project}: {detail}")


def _validate(source_directory: Path | None, data_directory: Path) -> list[Path]:
    drifted: list[Path] = []
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory)
        for source in UPSTREAM_SOURCES:
            if source_directory is None:
                lockfile = temporary / f"{source.project}-pnpm-lock.yaml"
                _download(source, lockfile)
            else:
                lockfile = source_directory / f"{source.project}-pnpm-lock.yaml"
                if not lockfile.is_file():
                    raise RuntimeError(f"Source lockfile does not exist: {lockfile}")

            output_prefix = temporary / f"{source.project}-lockfile"
            _run_extractor(lockfile, source.project, output_prefix)
            for suffix in ARTIFACT_SUFFIXES:
                generated = Path(f"{output_prefix}-{suffix}")
                committed = data_directory / f"{source.project}-lockfile-{suffix}"
                if (
                    not committed.is_file()
                    or generated.read_bytes() != committed.read_bytes()
                ):
                    drifted.append(committed)
    return drifted


def main() -> int:
    args = _parse_args()
    try:
        drifted = _validate(args.source_dir, args.data_dir)
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if drifted:
        print("Lockfile inventory artifacts are stale:", file=sys.stderr)
        for path in drifted:
            print(f"- {path}", file=sys.stderr)
        print(
            "Regenerate the artifacts with the pinned sources before committing.",
            file=sys.stderr,
        )
        return 1

    print("Lockfile inventory artifacts match the pinned upstream sources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
