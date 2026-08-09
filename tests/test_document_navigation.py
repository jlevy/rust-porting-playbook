from __future__ import annotations

import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PROJECT_SPECS_ROOT = REPOSITORY_ROOT / "docs" / "project" / "specs"


class DocumentNavigationTest(unittest.TestCase):
    def test_root_readme_routes_to_durable_indexes_not_plan_records(self) -> None:
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("](docs/README.md)", readme)
        self.assertIn("](_meta/README.md)", readme)
        for transient_prefix in (
            "docs/project/specs/active/",
            "docs/project/specs/done/",
            "_meta/plans/active/",
            "_meta/plans/done/",
        ):
            with self.subTest(transient_prefix=transient_prefix):
                self.assertNotIn(f"]({transient_prefix}", readme)

    def test_meta_readme_routes_to_its_plan_index_not_plan_records(self) -> None:
        readme = (REPOSITORY_ROOT / "_meta" / "README.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("](plans/README.md)", readme)
        self.assertNotIn("](plans/active/", readme)
        self.assertNotIn("](plans/done/", readme)

    def test_document_indexes_form_a_durable_navigation_chain(self) -> None:
        docs_index = (REPOSITORY_ROOT / "docs" / "README.md").read_text(
            encoding="utf-8"
        )
        project_index = (
            REPOSITORY_ROOT / "docs" / "project" / "README.md"
        ).read_text(encoding="utf-8")

        self.assertIn("](project/README.md)", docs_index)
        self.assertIn("](reviews/)", docs_index)
        self.assertIn("](specs/README.md)", project_index)

    def test_specs_index_lists_active_and_completed_plan_records(self) -> None:
        specs_index = (PROJECT_SPECS_ROOT / "README.md").read_text(encoding="utf-8")

        for lifecycle in ("active", "done"):
            for plan in sorted((PROJECT_SPECS_ROOT / lifecycle).glob("plan-*.md")):
                with self.subTest(plan=plan.name):
                    self.assertIn(f"]({lifecycle}/{plan.name})", specs_index)

    def test_completed_rust_reorganization_plan_is_archived(self) -> None:
        plan_name = "plan-2026-08-08-rust-guideline-reorganization.md"

        self.assertFalse((PROJECT_SPECS_ROOT / "active" / plan_name).exists())
        self.assertTrue((PROJECT_SPECS_ROOT / "done" / plan_name).is_file())


if __name__ == "__main__":
    unittest.main()
