from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_docs import check_markdown_files


class CheckMarkdownFilesTest(unittest.TestCase):
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
            document.write_text("# Example\n\n```rust\nfn main() {}\n", encoding="utf-8")

            findings = check_markdown_files(root, [document])

            self.assertEqual(len(findings), 1)
            self.assertIn("unclosed", findings[0].message)


if __name__ == "__main__":
    unittest.main()
