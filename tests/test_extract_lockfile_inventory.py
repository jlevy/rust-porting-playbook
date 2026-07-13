from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    REPOSITORY_ROOT
    / "docs"
    / "project"
    / "research"
    / "data"
    / "extract_lockfile_inventory.py"
)


class ExtractLockfileInventoryTest(unittest.TestCase):
    def test_help_is_available_without_positional_arguments(self) -> None:
        result = subprocess.run(
            [
                "uv",
                "--no-config",
                "run",
                "--locked",
                "--script",
                str(SCRIPT),
                "--help",
            ],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pnpm lockfile", result.stdout)

    def test_generates_deterministic_inventory_files(self) -> None:
        lockfile = """\
lockfileVersion: '9.0'
importers:
  .:
    dependencies:
      alpha:
        version: 1.0.0
snapshots:
  alpha@1.0.0:
    dependencies:
      beta: 2.0.0
  beta@2.0.0: {}
"""
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            lock_path = temporary / "pnpm-lock.yaml"
            output_prefix = temporary / "inventory"
            lock_path.write_text(lockfile, encoding="utf-8")

            result = subprocess.run(
                [
                    "uv",
                    "--no-config",
                    "run",
                    "--locked",
                    "--script",
                    str(SCRIPT),
                    str(lock_path),
                    "qmd",
                    str(output_prefix),
                ],
                cwd=REPOSITORY_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["lock_entries"], 2)
            self.assertEqual(summary["direct_manifest_entries"], 1)
            self.assertEqual(
                summary["action_counts"],
                {
                    "covered-in-direct-plan": 1,
                    "replace-through-runtime-owner": 1,
                },
            )
            self.assertEqual(
                (temporary / "inventory-package-inventory.tsv").read_text(
                    encoding="utf-8"
                ),
                "lock_key\tname\tversion\tis_direct_name\towner_count\towners\towner_groups\taction\n"
                "alpha@1.0.0\talpha\t1.0.0\ttrue\t1\talpha\truntime\tcovered-in-direct-plan\n"
                "beta@2.0.0\tbeta\t2.0.0\tfalse\t1\talpha\truntime\treplace-through-runtime-owner\n",
            )


if __name__ == "__main__":
    unittest.main()
