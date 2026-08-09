from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "docs-quality.yml"
CODEOWNERS = REPOSITORY_ROOT / ".github" / "CODEOWNERS"


class WorkflowSecurityTest(unittest.TestCase):
    def test_workflow_uses_only_reviewed_immutable_action_pins(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        action_references = re.findall(r"^\s*- uses:\s*(\S+)", workflow, re.MULTILINE)

        self.assertEqual(
            action_references,
            [
                "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97",
                "astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9",
            ],
        )

    def test_pull_request_validation_has_no_privileged_or_persistent_state(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertNotIn("pull_request_target", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("enable-cache: false", workflow)
        self.assertNotIn("cache-dependency-glob:", workflow)

    def test_codeowners_covers_execution_and_instruction_surfaces(self) -> None:
        codeowners = CODEOWNERS.read_text(encoding="utf-8")
        required_patterns = (
            "/.github/ ",
            "/.agents/ ",
            "/.claude/ ",
            "/.codex/ ",
            "/.tbd/ ",
            "/.vscode/ ",
            "/.devcontainer/ ",
            "/.mcp.json ",
            "/AGENTS.md ",
            "/CLAUDE.md ",
            "/.cursorrules ",
            "/SUPPLY-CHAIN-SECURITY.md ",
            "/SUPPLY-CHAIN-AUDIT-LOG.md ",
            "/scripts/ ",
            "/tests/ ",
            "/docs/project/research/data/*.py ",
            "/docs/project/research/data/*.lock ",
        )

        for pattern in required_patterns:
            self.assertIn(pattern, codeowners)


if __name__ == "__main__":
    unittest.main()
