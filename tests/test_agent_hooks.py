from __future__ import annotations

import json
import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SESSION_SCRIPTS = (
    REPOSITORY_ROOT / ".claude" / "scripts" / "tbd-session.sh",
    REPOSITORY_ROOT / ".codex" / "tbd-session.sh",
)
CLOSING_SCRIPTS = (
    REPOSITORY_ROOT / ".claude" / "hooks" / "tbd-closing-reminder.sh",
    REPOSITORY_ROOT / ".codex" / "tbd-closing-reminder.sh",
)
ENSURE_GH_SCRIPTS = (
    REPOSITORY_ROOT / ".claude" / "scripts" / "ensure-gh-cli.sh",
    REPOSITORY_ROOT / ".codex" / "ensure-gh-cli.sh",
)
CLAUDE_SETTINGS = REPOSITORY_ROOT / ".claude" / "settings.json"
CODEX_HOOKS = REPOSITORY_ROOT / ".codex" / "hooks.json"
TBD_VERSION = "0.4.2"


class AgentHooksTest(unittest.TestCase):
    def _fake_environment(
        self,
        temporary: Path,
        *,
        tbd_version: str,
        npm_global: bool = False,
        npx_exit_code: int = 0,
    ) -> tuple[dict[str, str], Path]:
        bin_dir = temporary / ".local" / "bin"
        bin_dir.mkdir(parents=True)
        log = temporary / "commands.log"
        quoted_log = shlex.quote(str(log))
        tbd_bin_dir = bin_dir
        npm = bin_dir / "npm"
        if npm_global:
            npm_prefix = temporary / "npm-global"
            tbd_bin_dir = npm_prefix / "bin"
            tbd_bin_dir.mkdir(parents=True)
            npm_contents = f"#!/bin/bash\necho {shlex.quote(str(npm_prefix))}\n"
        else:
            npm_contents = "#!/bin/bash\nexit 1\n"
        npm.write_text(npm_contents, encoding="utf-8")
        npm.chmod(0o755)
        tbd = tbd_bin_dir / "tbd"
        tbd.write_text(
            "#!/bin/bash\n"
            'if [[ "$1" == "--version" ]]; then\n'
            f"  echo {tbd_version}\n"
            "else\n"
            '  if [[ "${TBD_TEST_LOG_CWD:-}" == "true" ]]; then\n'
            '    echo "cwd=$PWD tbd ignore_scripts=${NPM_CONFIG_IGNORE_SCRIPTS:-} $*" '
            f">> {quoted_log}\n"
            "  else\n"
            '    echo "tbd ignore_scripts=${NPM_CONFIG_IGNORE_SCRIPTS:-} $*" '
            f">> {quoted_log}\n"
            "  fi\n"
            "fi\n",
            encoding="utf-8",
        )
        npx = bin_dir / "npx"
        npx.write_text(
            "#!/bin/bash\n"
            'if [[ "${TBD_TEST_LOG_CWD:-}" == "true" ]]; then\n'
            '  echo "cwd=$PWD npx ignore_scripts=${NPM_CONFIG_IGNORE_SCRIPTS:-} $*" '
            f">> {quoted_log}\n"
            "else\n"
            '  echo "npx ignore_scripts=${NPM_CONFIG_IGNORE_SCRIPTS:-} $*" '
            f">> {quoted_log}\n"
            "fi\n"
            f"exit {npx_exit_code}\n",
            encoding="utf-8",
        )
        tbd.chmod(0o755)
        npx.chmod(0o755)
        environment = os.environ.copy()
        environment.pop("NPM_CONFIG_IGNORE_SCRIPTS", None)
        environment.update({"HOME": str(temporary), "PATH": "/usr/bin:/bin"})
        return environment, log

    def test_session_hooks_fall_back_when_global_tbd_version_is_stale(self) -> None:
        for script in SESSION_SCRIPTS:
            with (
                self.subTest(script=script),
                tempfile.TemporaryDirectory() as directory,
            ):
                environment, log = self._fake_environment(
                    Path(directory), tbd_version="0.3.0"
                )

                result = subprocess.run(
                    ["/bin/bash", str(script), "--brief"],
                    cwd=REPOSITORY_ROOT,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    log.read_text(encoding="utf-8"),
                    f"npx ignore_scripts=true --yes get-tbd@{TBD_VERSION} prime --brief\n",
                )

    def test_session_hooks_use_matching_local_tbd(self) -> None:
        for script in SESSION_SCRIPTS:
            with (
                self.subTest(script=script),
                tempfile.TemporaryDirectory() as directory,
            ):
                environment, log = self._fake_environment(
                    Path(directory), tbd_version=TBD_VERSION
                )

                result = subprocess.run(
                    ["/bin/bash", str(script), "--brief"],
                    cwd=REPOSITORY_ROOT,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    log.read_text(encoding="utf-8"),
                    "tbd ignore_scripts= prime --brief\n",
                )

    def test_session_hooks_find_matching_tbd_in_npm_global_prefix(self) -> None:
        for script in SESSION_SCRIPTS:
            with (
                self.subTest(script=script),
                tempfile.TemporaryDirectory() as directory,
            ):
                environment, log = self._fake_environment(
                    Path(directory), tbd_version=TBD_VERSION, npm_global=True
                )

                result = subprocess.run(
                    ["/bin/bash", str(script), "--brief"],
                    cwd=REPOSITORY_ROOT,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    log.read_text(encoding="utf-8"),
                    "tbd ignore_scripts= prime --brief\n",
                )

    def test_session_hooks_run_prime_from_repository_root(self) -> None:
        cases = (
            (TBD_VERSION, "tbd ignore_scripts= prime --brief"),
            (
                "0.3.0",
                f"npx ignore_scripts=true --yes get-tbd@{TBD_VERSION} prime --brief",
            ),
        )
        nested = REPOSITORY_ROOT / "docs" / "project"
        for tbd_version, expected_command in cases:
            for script in SESSION_SCRIPTS:
                with (
                    self.subTest(script=script, tbd_version=tbd_version),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    environment, log = self._fake_environment(
                        Path(directory), tbd_version=tbd_version
                    )
                    environment["TBD_TEST_LOG_CWD"] = "true"

                    result = subprocess.run(
                        ["/bin/bash", str(script), "--brief"],
                        cwd=nested,
                        env=environment,
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(
                        log.read_text(encoding="utf-8"),
                        f"cwd={REPOSITORY_ROOT} {expected_command}\n",
                    )

    def test_claude_precompact_hook_runs_from_nested_directory(self) -> None:
        hooks = json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))["hooks"]
        for entry in hooks["SessionStart"]:
            self.assertIn("$CLAUDE_PROJECT_DIR", entry["hooks"][0]["command"])
        command = hooks["PreCompact"][0]["hooks"][0]["command"]
        nested = REPOSITORY_ROOT / "docs" / "project"
        with tempfile.TemporaryDirectory() as directory:
            environment, log = self._fake_environment(
                Path(directory), tbd_version=TBD_VERSION
            )
            environment["CLAUDE_PROJECT_DIR"] = str(REPOSITORY_ROOT)

            result = subprocess.run(
                command,
                cwd=nested,
                env=environment,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                log.read_text(encoding="utf-8"),
                "tbd ignore_scripts= prime --brief\n",
            )

    def test_closing_reminders_warn_when_fallback_fails(self) -> None:
        for script in CLOSING_SCRIPTS:
            with (
                self.subTest(script=script),
                tempfile.TemporaryDirectory() as directory,
            ):
                environment, _ = self._fake_environment(
                    Path(directory), tbd_version="0.3.0", npx_exit_code=1
                )

                result = subprocess.run(
                    ["/bin/bash", str(script)],
                    cwd=REPOSITORY_ROOT,
                    env=environment,
                    input='{"tool_input":{"command":"git push origin HEAD"}}',
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Closing reminder skipped", result.stderr)

    def test_closing_reminders_run_from_repository_root_outside_worktree(self) -> None:
        for script in CLOSING_SCRIPTS:
            with (
                self.subTest(script=script),
                tempfile.TemporaryDirectory() as directory,
            ):
                temporary = Path(directory)
                outside_worktree = temporary / "outside-worktree"
                outside_worktree.mkdir()
                environment, log = self._fake_environment(
                    temporary, tbd_version=TBD_VERSION
                )
                environment["TBD_TEST_LOG_CWD"] = "true"

                result = subprocess.run(
                    ["/bin/bash", str(script)],
                    cwd=outside_worktree,
                    env=environment,
                    input='{"tool_input":{"command":"git push origin HEAD"}}',
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    log.read_text(encoding="utf-8"),
                    f"cwd={REPOSITORY_ROOT} tbd ignore_scripts= closing\n",
                )

    def test_closing_reminders_detect_git_global_options(self) -> None:
        cases = (
            ("git -C /tmp push origin HEAD", True),
            ("cd /tmp && git --no-pager -C /tmp push origin HEAD", True),
            ("git -C '/tmp/path with spaces' push origin HEAD", True),
            ("git add push", False),
            ("echo git -C /tmp push origin HEAD", False),
        )
        for script in CLOSING_SCRIPTS:
            for command, should_remind in cases:
                with (
                    self.subTest(script=script, command=command),
                    tempfile.TemporaryDirectory() as directory,
                ):
                    environment, log = self._fake_environment(
                        Path(directory), tbd_version=TBD_VERSION
                    )

                    result = subprocess.run(
                        ["/bin/bash", str(script)],
                        cwd=REPOSITORY_ROOT,
                        env=environment,
                        input=json.dumps({"tool_input": {"command": command}}),
                        check=False,
                        capture_output=True,
                        text=True,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)
                    if should_remind:
                        self.assertEqual(
                            log.read_text(encoding="utf-8"),
                            "tbd ignore_scripts= closing\n",
                        )
                    else:
                        self.assertFalse(log.exists())

    def test_gh_setup_is_best_effort_on_unsupported_platform(self) -> None:
        for script in ENSURE_GH_SCRIPTS:
            with (
                self.subTest(script=script),
                tempfile.TemporaryDirectory() as directory,
            ):
                temporary = Path(directory)
                bin_dir = temporary / ".local" / "bin"
                bin_dir.mkdir(parents=True)
                uname = bin_dir / "uname"
                uname.write_text(
                    "#!/bin/bash\n"
                    'if [[ "$1" == "-s" ]]; then\n'
                    "  echo windows\n"
                    "else\n"
                    "  echo x86_64\n"
                    "fi\n",
                    encoding="utf-8",
                )
                tr = bin_dir / "tr"
                tr.write_text('#!/bin/bash\nexec /usr/bin/tr "$@"\n', encoding="utf-8")
                uname.chmod(0o755)
                tr.chmod(0o755)
                environment = os.environ.copy()
                environment.update({"HOME": str(temporary), "PATH": str(bin_dir)})

                result = subprocess.run(
                    ["/bin/bash", str(script)],
                    cwd=REPOSITORY_ROOT,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("No pinned checksum", result.stderr)
                self.assertIn("Continuing without gh", result.stderr)

    def test_gh_setup_scripts_share_the_reviewed_pin_and_checksums(self) -> None:
        expected_fragments = (
            'GH_VERSION="2.96.0"',
            'mktemp -d "${TMPDIR:-/tmp}/gh-install.XXXXXX"',
            "83d5c2ccad5498f58bf6368acb1ab32588cf43ab3a4b1c301bf36328b1c8bd60",
            "06f86ec7103d41993b76cd78072f43595c34aaa56506d971d9860e67140bf909",
            "4bd449df9ad639391bc62b8032546f0fe9edcd8526e06682a4f88abd8c5d163c",
            "f23a0c37d963aacc3bed703ccbd59b41c5ca22101fab7f00eb2b7cad23aba463",
        )
        script_contents = [
            script.read_text(encoding="utf-8") for script in ENSURE_GH_SCRIPTS
        ]

        self.assertEqual(script_contents[0], script_contents[1])
        self.assertNotIn('"/tmp/${ASSET}"', script_contents[0])
        for fragment in expected_fragments:
            self.assertIn(fragment, script_contents[0])

    def test_codex_provisions_gh_before_running_tbd(self) -> None:
        hooks = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))["hooks"]
        commands = [entry["hooks"][0]["command"] for entry in hooks["SessionStart"]]

        self.assertIn("ensure-gh-cli.sh", commands[0])
        self.assertIn("tbd-session.sh", commands[1])

    def test_codex_closing_reminder_runs_from_nested_directory(self) -> None:
        hooks = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))["hooks"]
        command = hooks["PostToolUse"][0]["hooks"][0]["command"]
        nested = REPOSITORY_ROOT / "docs" / "project"
        with tempfile.TemporaryDirectory() as directory:
            environment, log = self._fake_environment(
                Path(directory), tbd_version=TBD_VERSION
            )

            result = subprocess.run(
                command,
                cwd=nested,
                env=environment,
                input='{"tool_input":{"command":"git push origin HEAD"}}',
                shell=True,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                log.read_text(encoding="utf-8"),
                "tbd ignore_scripts= closing\n",
            )


if __name__ == "__main__":
    unittest.main()
