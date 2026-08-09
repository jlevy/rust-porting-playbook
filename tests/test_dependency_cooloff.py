from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.check_dependency_cooloff import check_lockfiles


NOW = datetime(2026, 8, 8, 12, tzinfo=timezone.utc)
CHECKER = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "check_dependency_cooloff.py"
)


def _write_lockfile(directory: Path, artifact_lines: str) -> Path:
    lockfile = directory / "example.py.lock"
    lockfile.write_text(
        "version = 1\n\n"
        "[[package]]\n"
        'name = "example"\n'
        'version = "1.2.3"\n'
        'source = { registry = "https://pypi.org/simple" }\n'
        f"{artifact_lines}\n",
        encoding="utf-8",
    )
    return lockfile


class DependencyCooloffTest(unittest.TestCase):
    def test_artifact_at_fourteen_day_boundary_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = _write_lockfile(
                Path(directory),
                'sdist = { upload-time = "2026-07-25T12:00:00Z" }',
            )

            self.assertEqual(check_lockfiles([path], now=NOW), [])

    def test_too_recent_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = _write_lockfile(
                Path(directory),
                'sdist = { upload-time = "2026-07-30T12:00:00Z" }',
            )

            findings = check_lockfiles([path], now=NOW)

            self.assertEqual(len(findings), 1)
            self.assertIn("only 9 day(s) old", findings[0].message)

    def test_newest_locked_artifact_controls_age(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = _write_lockfile(
                Path(directory),
                'sdist = { upload-time = "2026-06-01T12:00:00Z" }\n'
                "wheels = [\n"
                '    { upload-time = "2026-07-30T12:00:00Z" },\n'
                "]",
            )

            findings = check_lockfiles([path], now=NOW)

            self.assertEqual(len(findings), 1)
            self.assertIn("only 9 day(s) old", findings[0].message)

    def test_missing_upload_time_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = _write_lockfile(Path(directory), 'sdist = { url = "example" }')

            findings = check_lockfiles([path], now=NOW)

            self.assertEqual(len(findings), 1)
            self.assertIn("no verifiable upload time", findings[0].message)

    def test_cli_reports_violation_and_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = _write_lockfile(
                Path(directory),
                'sdist = { upload-time = "2099-01-01T00:00:00Z" }',
            )

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Dependency cool-off violations", result.stderr)
            self.assertIn("example==1.2.3", result.stderr)


if __name__ == "__main__":
    unittest.main()
