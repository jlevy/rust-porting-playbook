#!/usr/bin/env python3
"""Reject too-recent artifacts in tracked PEP 723 uv lockfiles."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


COOL_OFF_DAYS = 14


@dataclass(frozen=True)
class Finding:
    """One dependency cool-off policy violation."""

    path: Path
    package: str
    message: str


def _parse_upload_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"upload time has no timezone: {value}")
    return parsed.astimezone(timezone.utc)


def _package_artifacts(package: dict[str, object]) -> list[dict[str, object]]:
    artifacts: list[dict[str, object]] = []
    sdist = package.get("sdist")
    if isinstance(sdist, dict):
        artifacts.append(sdist)
    wheels = package.get("wheels")
    if isinstance(wheels, list):
        artifacts.extend(wheel for wheel in wheels if isinstance(wheel, dict))
    return artifacts


def check_lockfiles(
    paths: list[Path], *, now: datetime | None = None
) -> list[Finding]:
    """
    Return cool-off violations from registry packages in uv lockfiles.

    The newest locked artifact controls eligibility because any wheel or source archive
    in the lockfile can become executable on a matching platform.
    """

    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("now must include a timezone")
    current_time = current_time.astimezone(timezone.utc)
    cutoff = current_time - timedelta(days=COOL_OFF_DAYS)
    findings: list[Finding] = []

    for path in paths:
        contents = tomllib.loads(path.read_text(encoding="utf-8"))
        packages = contents.get("package", [])
        if not isinstance(packages, list):
            raise ValueError(f"{path}: package must be an array")

        for package in packages:
            if not isinstance(package, dict):
                continue
            source = package.get("source")
            if not isinstance(source, dict) or "registry" not in source:
                continue

            name = str(package.get("name", "<unnamed>"))
            version = str(package.get("version", "<unknown>"))
            identity = f"{name}=={version}"
            artifacts = _package_artifacts(package)
            raw_times = [artifact.get("upload-time") for artifact in artifacts]
            has_missing_time = any(
                not isinstance(value, str) for value in raw_times
            )
            if not artifacts or has_missing_time:
                findings.append(
                    Finding(
                        path,
                        identity,
                        "has locked registry artifacts with no verifiable upload time",
                    )
                )
                continue

            try:
                upload_times = [
                    _parse_upload_time(value)
                    for value in raw_times
                    if isinstance(value, str)
                ]
            except ValueError as error:
                findings.append(Finding(path, identity, str(error)))
                continue

            newest = max(upload_times)
            if newest > cutoff:
                age = current_time - newest
                findings.append(
                    Finding(
                        path,
                        identity,
                        f"newest artifact is only {age.days} day(s) old "
                        f"({newest.isoformat()}); requires {COOL_OFF_DAYS}",
                    )
                )

    return sorted(
        findings,
        key=lambda finding: (str(finding.path), finding.package, finding.message),
    )


def _repository_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip())


def _tracked_lockfiles(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.py.lock"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [root / path.decode() for path in result.stdout.split(b"\0") if path]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that registry artifacts in PEP 723 uv lockfiles are at least "
            f"{COOL_OFF_DAYS} days old."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="lockfiles to check; defaults to tracked *.py.lock files",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        paths = args.paths or _tracked_lockfiles(_repository_root())
        findings = check_lockfiles(paths)
    except (
        OSError,
        subprocess.CalledProcessError,
        tomllib.TOMLDecodeError,
        ValueError,
    ) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if findings:
        print("Dependency cool-off violations:", file=sys.stderr)
        for finding in findings:
            print(
                f"- {finding.path}: {finding.package}: {finding.message}",
                file=sys.stderr,
            )
        return 1

    print(f"All registry artifacts satisfy the {COOL_OFF_DAYS}-day cool-off.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
