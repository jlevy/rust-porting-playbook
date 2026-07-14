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
CODEX_HOOKS = REPOSITORY_ROOT / ".codex" / "hooks.json"


class AgentHooksTest(unittest.TestCase):
    def _fake_environment(
        self, temporary: Path, *, tbd_version: str
    ) -> tuple[dict[str, str], Path]:
        bin_dir = temporary / ".local" / "bin"
        bin_dir.mkdir(parents=True)
        log = temporary / "commands.log"
        quoted_log = shlex.quote(str(log))
        tbd = bin_dir / "tbd"
        tbd.write_text(
            "#!/bin/bash\n"
            'if [[ "$1" == "--version" ]]; then\n'
            f"  echo {tbd_version}\n"
            "else\n"
            '  echo "tbd ignore_scripts=${NPM_CONFIG_IGNORE_SCRIPTS:-} $*" '
            f">> {quoted_log}\n"
            "fi\n",
            encoding="utf-8",
        )
        npx = bin_dir / "npx"
        npx.write_text(
            "#!/bin/bash\n"
            'echo "npx ignore_scripts=${NPM_CONFIG_IGNORE_SCRIPTS:-} $*" '
            f">> {quoted_log}\n",
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
                    "npx ignore_scripts=true --yes get-tbd@0.4.0 prime --brief\n",
                )

    def test_session_hooks_use_matching_local_tbd(self) -> None:
        for script in SESSION_SCRIPTS:
            with (
                self.subTest(script=script),
                tempfile.TemporaryDirectory() as directory,
            ):
                environment, log = self._fake_environment(
                    Path(directory), tbd_version="0.4.0"
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
                Path(directory), tbd_version="0.4.0"
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
