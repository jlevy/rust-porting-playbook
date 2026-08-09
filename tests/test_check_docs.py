from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import check_markdown_files, check_text_files


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "scripts" / "check_docs.py"


class CheckMarkdownFilesTest(unittest.TestCase):
    def test_cli_discovers_tracked_files_from_nested_directory(self) -> None:
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.md"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
        )
        expected_count = len([path for path in tracked.stdout.split(b"\0") if path])
        result = subprocess.run(
            ["python3", str(SCRIPT)],
            cwd=REPOSITORY_ROOT / "docs" / "project",
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"Markdown structure passed for {expected_count} file(s).", result.stdout
        )

    def test_cli_reports_unreadable_path_without_traceback(self) -> None:
        result = subprocess.run(
            ["python3", str(SCRIPT), "missing.md"],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_accepts_existing_relative_links_and_heading_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "README.md"
            guide = root / "guide.md"
            index.write_text("# Index\n\n[Guide](guide.md#details)\n", encoding="utf-8")
            guide.write_text("# Guide\n\n## Details\n", encoding="utf-8")

            findings = check_markdown_files(root, [index, guide])

            self.assertEqual(findings, [])

    def test_reports_missing_files_and_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / "README.md"
            guide = root / "guide.md"
            index.write_text(
                "# Index\n\n[Missing](missing.md)\n\n[Bad anchor](guide.md#missing)\n",
                encoding="utf-8",
            )
            guide.write_text("# Guide\n", encoding="utf-8")

            findings = check_markdown_files(root, [index, guide])

            self.assertEqual(len(findings), 2)
            self.assertIn("target does not exist", findings[0].message)
            self.assertIn("anchor does not exist", findings[1].message)

    def test_ignores_links_inside_fenced_code_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_text(
                "# Example\n\n```markdown\n[Placeholder](missing.md)\n```\n",
                encoding="utf-8",
            )

            findings = check_markdown_files(root, [document])

            self.assertEqual(findings, [])

    def test_ignores_links_inside_inline_code_and_footnote_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_text(
                "# Example\n\nUse `![alt](url)`.\n\n"
                "[^source]: [External](https://example.com)\n",
                encoding="utf-8",
            )

            findings = check_markdown_files(root, [document])

            self.assertEqual(findings, [])

    def test_reports_unclosed_fenced_code_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            document.write_text(
                "# Example\n\n```rust\nfn main() {}\n", encoding="utf-8"
            )

            findings = check_markdown_files(root, [document])

            self.assertEqual(len(findings), 1)
            self.assertIn("unclosed", findings[0].message)

    def test_reports_invisible_unicode_in_markdown_and_automation_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = root / "README.md"
            automation = root / "hooks.json"
            document.write_text(
                "# Example\n\n```text\nhidden\u200btext\n```\n\n"
                "visible text\n",
                encoding="utf-8",
            )
            automation.write_text(
                '{"command": "direction\u202eoverride"}\n', encoding="utf-8"
            )

            findings = check_text_files([document, automation])

            self.assertEqual(len(findings), 2)
            messages = [finding.message for finding in findings]
            self.assertTrue(
                any("U+200B (ZERO WIDTH SPACE)" in message for message in messages)
            )
            self.assertTrue(
                any(
                    "U+202E (RIGHT-TO-LEFT OVERRIDE)" in message
                    for message in messages
                )
            )


if __name__ == "__main__":
    unittest.main()
