from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = (
    REPOSITORY_ROOT
    / "docs"
    / "project"
    / "research"
    / "data"
    / "extract_lockfile_inventory.py"
)
CHECKER = REPOSITORY_ROOT / "scripts" / "check_lockfile_inventories.py"
WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "docs-quality.yml"


class CheckLockfileInventoriesTest(unittest.TestCase):
    def test_ci_runs_upstream_provenance_check(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("python scripts/check_lockfile_inventories.py", workflow)

    def _run_extractor(self, source: Path, project: str, output_prefix: Path) -> None:
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
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_detects_committed_inventory_drift(self) -> None:
        lockfiles = {
            "tbd": """\
lockfileVersion: '9.0'
importers:
  packages/tbd:
    dependencies:
      alpha:
        version: 1.0.0
snapshots:
  alpha@1.0.0: {}
""",
            "qmd": """\
lockfileVersion: '9.0'
importers:
  .:
    dependencies:
      beta:
        version: 2.0.0
snapshots:
  beta@2.0.0: {}
""",
        }
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            sources = temporary / "sources"
            data = temporary / "data"
            sources.mkdir()
            data.mkdir()
            for project, contents in lockfiles.items():
                source = sources / f"{project}-pnpm-lock.yaml"
                source.write_text(contents, encoding="utf-8")
                self._run_extractor(source, project, data / f"{project}-lockfile")

            passing = subprocess.run(
                [
                    "python3",
                    str(CHECKER),
                    "--source-dir",
                    str(sources),
                    "--data-dir",
                    str(data),
                ],
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(passing.returncode, 0, passing.stderr)

            drifted = data / "qmd-lockfile-summary.json"
            drifted.write_text("{}\n", encoding="utf-8")
            failing = subprocess.run(
                [
                    "python3",
                    str(CHECKER),
                    "--source-dir",
                    str(sources),
                    "--data-dir",
                    str(data),
                ],
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(failing.returncode, 0)
            self.assertIn("qmd-lockfile-summary.json", failing.stderr)


if __name__ == "__main__":
    unittest.main()
