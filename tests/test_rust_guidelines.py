from __future__ import annotations

import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GUIDELINES_ROOT = REPOSITORY_ROOT / "guidelines"
RUST_GUIDELINES = (
    "rust-rules.md",
    "rust-project-setup.md",
    "rust-cli-rules.md",
    "rust-filesystem-rules.md",
    "rust-testing-rules.md",
    "rust-release-rules.md",
    "rust-code-review-rules.md",
)
COMMON_FOOTER = (
    "<!-- This document follows common-doc-guidelines.md.\n"
    "See github.com/jlevy/practical-prose and review guidelines before editing.\n"
    "-->\n"
)


class RustGuidelineStructureTest(unittest.TestCase):
    def test_reusable_guidelines_have_tbd_compatible_structure(self) -> None:
        for filename in RUST_GUIDELINES:
            with self.subTest(filename=filename):
                text = (GUIDELINES_ROOT / filename).read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                _, frontmatter, body = text.split("---\n", maxsplit=2)
                self.assertRegex(frontmatter, r"(?m)^title: .+$")
                self.assertRegex(frontmatter, r"(?m)^description: .+$")
                self.assertRegex(frontmatter, r"(?m)^category: rust$")
                self.assertRegex(body, r"(?m)^# .+$")
                self.assertIn("\n## Related Guidelines\n", body)
                self.assertTrue(text.endswith(COMMON_FOOTER))

    def test_index_lists_every_reusable_guideline(self) -> None:
        index = (GUIDELINES_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## General Rust Guidelines", index)
        self.assertIn("## Porting Guidelines", index)
        for filename in RUST_GUIDELINES:
            with self.subTest(filename=filename):
                self.assertIn(f"]({filename})", index)

    def test_legacy_paths_route_to_authoritative_guidelines(self) -> None:
        routes = {
            GUIDELINES_ROOT / "rust-general-rules.md": "rust-rules.md",
            REPOSITORY_ROOT
            / "references"
            / "rust-cli-app-patterns.md": "../guidelines/rust-cli-rules.md",
            REPOSITORY_ROOT
            / "references"
            / "rust-code-review-checklist.md": (
                "../guidelines/rust-code-review-rules.md"
            ),
        }

        for path, destination in routes.items():
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIsNotNone(
                    re.search(rf"\]\({re.escape(destination)}(?:#[^)]+)?\)", text)
                )


if __name__ == "__main__":
    unittest.main()
