"""Run the real Bash routine in isolated workspaces with inert git/skill stubs."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def bash_executable():
    if os.name == "nt":
        for candidate in (
            Path("C:/Program Files/Git/bin/bash.exe"),
            Path("C:/Program Files/Git/usr/bin/bash.exe"),
        ):
            if candidate.is_file():
                return str(candidate)
    found = shutil.which("bash")
    if not found:
        raise RuntimeError("Routine acceptance checks require Bash (Git Bash on Windows).")
    return found


def bash_path(path):
    """Use POSIX paths for Bash while retaining spaces as single arguments."""
    path = Path(path).resolve()
    if os.name == "nt":
        return "/" + path.drive[0].lower() + path.as_posix()[2:]
    return str(path)


class RoutineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bash = bash_executable()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic routine tests ")
        self.workspace = Path(self.temporary.name)
        scripts = self.workspace / "scripts"
        scripts.mkdir()
        self.routine = scripts / "run-routine.sh"
        self.routine.write_text((ROOT / "scripts/run-routine.sh").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        self.bin = self.workspace / "test-bin"
        self.bin.mkdir()
        git = self.bin / "git"
        git.write_text('''#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$TEST_GIT_LOG"
case "$1" in
  status) if [[ "$TEST_DIRTY" == 1 ]]; then printf ' M tracked-file\\n'; fi ;;
  pull) exit "$TEST_PULL_STATUS" ;;
  *) echo 'Unexpected git mutation or command refused by test stub' >&2; exit 90 ;;
esac
''', encoding="utf-8", newline="\n")
        python = self.bin / "routine-python"
        python.write_text('''#!/usr/bin/env bash
if [[ "${2:-}" == trigger ]]; then
  printf '%s\\n' "$*" >> "$TEST_SKILL_LOG"
  exit "$TEST_SKILL_STATUS"
fi
exec "$TEST_REAL_PYTHON" "$@"
''', encoding="utf-8", newline="\n")
        git.chmod(0o755)
        python.chmod(0o755)
        self.git_log = self.workspace / "git-calls.log"
        self.skill_log = self.workspace / "skill-calls.log"
        self.queue = self.workspace / "output/approval_queue.jsonl"
        self.environment = os.environ.copy()
        self.environment.update({
            "TEST_BIN": bash_path(self.bin),
            "TEST_ROUTINE": bash_path(self.routine),
            "TEST_SKILL": "weekly-digest",
            "TEST_GIT_LOG": bash_path(self.git_log),
            "TEST_SKILL_LOG": bash_path(self.skill_log),
            "TEST_REAL_PYTHON": bash_path(sys.executable),
            "AGENTIC_OS_PYTHON": bash_path(python),
            "TEST_DIRTY": "0",
            "TEST_PULL_STATUS": "0",
            "TEST_SKILL_STATUS": "0",
        })

    def tearDown(self):
        self.temporary.cleanup()

    def run_routine(self, **environment):
        env = self.environment | environment
        # All changing values are environment variables, never interpolated shell code.
        return subprocess.run(
            [self.bash, "-c", 'export PATH="$TEST_BIN:$PATH"; exec bash "$TEST_ROUTINE" "$TEST_SKILL"'],
            env=env, cwd=self.workspace, shell=False, capture_output=True, text=True, timeout=20,
        )

    def git_calls(self):
        return self.git_log.read_text(encoding="utf-8").splitlines() if self.git_log.exists() else []

    def assert_not_executed(self):
        self.assertFalse(self.skill_log.exists(), "Failed preconditions must prevent skill execution")
        self.assertFalse(self.queue.exists(), "Failed runs must not queue publication")

    def test_bash_syntax(self):
        result = subprocess.run(
            [self.bash, "-n", bash_path(self.routine)], shell=False,
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dirty_checkout_refuses_execution(self):
        result = self.run_routine(TEST_DIRTY="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dirty checkout", result.stderr)
        self.assertEqual(self.git_calls(), ["status --porcelain"])
        self.assert_not_executed()

    def test_failed_pull_refuses_execution(self):
        result = self.run_routine(TEST_PULL_STATUS="23")
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(self.git_calls(), ["status --porcelain", "pull --ff-only"])
        self.assert_not_executed()

    def test_failed_skill_propagates_without_publish_queue(self):
        result = self.run_routine(TEST_SKILL_STATUS="17")
        self.assertEqual(result.returncode, 17, result.stderr)
        self.assertIn("trigger weekly-digest", self.skill_log.read_text(encoding="utf-8"))
        self.assertFalse(self.queue.exists())
        self.assertEqual(self.git_calls(), ["status --porcelain", "pull --ff-only"])

    def test_success_queues_publish_intent_without_git_mutations(self):
        result = self.run_routine()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("trigger weekly-digest", self.skill_log.read_text(encoding="utf-8"))
        records = [json.loads(line) for line in self.queue.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "pending")
        self.assertEqual(records[0]["action"], "publish")
        self.assertEqual(records[0]["skill"], "weekly-digest")
        self.assertTrue(records[0]["id"].startswith("publish-"))
        self.assertIn("manually", records[0]["payload"]["instruction"])
        self.assertEqual(self.git_calls(), ["status --porcelain", "pull --ff-only"])

    def test_invalid_skill_is_rejected_before_git(self):
        result = self.run_routine(TEST_SKILL="weekly-digest;echo unexpected")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.git_calls(), [])
        self.assert_not_executed()


if __name__ == "__main__":
    unittest.main(verbosity=2)
