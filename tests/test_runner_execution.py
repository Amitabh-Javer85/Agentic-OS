#!/usr/bin/env python3
"""Offline regression tests for skill execution boundaries; never invoke Claude."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("execution_test_runner", ROOT / "apps/runner/server.py")
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)

MANIFEST = """name: fixture-skill
model: haiku
effort: low
max_budget_usd: 0.17
timeout_seconds: 43
allowed_tools:
  - "Read(./skills/fixture-skill/**)"
  - "Edit(./output/artifacts/**)"
  - "Edit(./memory/CONTENT.md)"
risk_tier: internal_write
"""
SKILL_TEXT = "# Fixture skill\nWrite a factual local report and update its memory pointer.\n"


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic-os-runner-test-")
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)
        self.skill = self.workspace / "skills/fixture-skill"
        self.skill.mkdir(parents=True)
        self.manifest = self.skill / "skill.yaml"
        self.manifest.write_text(MANIFEST, encoding="utf-8")
        (self.skill / "SKILL.md").write_text(SKILL_TEXT, encoding="utf-8")
        overrides = {
            "WORKSPACE_ROOT": self.workspace,
            "SKILLS_DIR": self.workspace / "skills",
            "LOCK_FILE": self.workspace / ".workspace.lock",
            "RUNS_LOG": self.workspace / "output/runs.log",
            "QUEUE_FILE": self.workspace / "output/approval_queue.jsonl",
        }
        self.globals = patch.multiple(RUNNER, **overrides)
        self.globals.start()
        self.addCleanup(self.globals.stop)
        self.command = patch.object(RUNNER, "claude_command", return_value=["fixture-claude"])
        self.command.start()
        self.addCleanup(self.command.stop)
        self.process = patch.object(RUNNER.subprocess, "run")
        self.mock_run = self.process.start()
        self.addCleanup(self.process.stop)
        self.mock_run.return_value = subprocess.CompletedProcess([], 0, json.dumps({"total_cost_usd": 0.07, "is_error": False}), "")

    def test_manifest_preserves_scoped_permissions(self):
        config = RUNNER.get_allowlisted_skills()["fixture-skill"]
        self.assertEqual(config["allowed_tools"], ["Read(./skills/fixture-skill/**)", "Edit(./output/artifacts/**)", "Edit(./memory/CONTENT.md)"])
        self.assertEqual(config["max_budget_usd"], 0.17)
        self.assertEqual(config["timeout_seconds"], 43)

    def test_invalid_manifests_are_not_registered(self):
        invalid_variants = {
            "duplicate tool block": MANIFEST + 'allowed_tools:\n  - "Write"\n',
            "duplicate budget": MANIFEST + 'max_budget_usd: 999\n',
            "missing explicit timeout": MANIFEST.replace("timeout_seconds: 43\n", ""),
            "missing explicit budget": MANIFEST.replace("max_budget_usd: 0.17\n", ""),
            "tool flag injection": MANIFEST.replace("Read(./skills/fixture-skill/**)", "--dangerously-skip-permissions"),
            "nonmatching scoped write": MANIFEST.replace("Edit(./output/artifacts/**)", "Write(./output/artifacts/**)"),
            "mismatched name": MANIFEST.replace("name: fixture-skill", "name: other"),
            "invalid cost": MANIFEST.replace("0.17", "not-a-number"),
            "negative cost": MANIFEST.replace("0.17", "-1"),
            "zero cost": MANIFEST.replace("0.17", "0"),
            "nonfinite cost nan": MANIFEST.replace("0.17", "nan"),
            "nonfinite cost inf": MANIFEST.replace("0.17", "inf"),
            "invalid timeout": MANIFEST.replace("43", "601"),
            "invalid risk": MANIFEST.replace("internal_write", "anything"),
            "invalid effort": MANIFEST.replace("effort: low", "effort: turbo"),
            "inline tool list": MANIFEST.replace('allowed_tools:\n  - "Read(./skills/fixture-skill/**)"\n  - "Edit(./output/artifacts/**)"\n  - "Edit(./memory/CONTENT.md)"', 'allowed_tools: ["Read"]'),
            "empty tool list": MANIFEST.replace('  - "Read(./skills/fixture-skill/**)"\n  - "Edit(./output/artifacts/**)"\n  - "Edit(./memory/CONTENT.md)"\n', ""),
        }
        for name, manifest in invalid_variants.items():
            with self.subTest(name=name):
                self.manifest.write_text(manifest, encoding="utf-8")
                self.assertNotIn("fixture-skill", RUNNER.get_allowlisted_skills())
        self.mock_run.assert_not_called()

    def test_both_skill_files_required(self):
        self.manifest.unlink()
        self.assertNotIn("fixture-skill", RUNNER.get_allowlisted_skills())
        self.manifest.write_text(MANIFEST, encoding="utf-8")
        (self.skill / "SKILL.md").unlink()
        self.assertNotIn("fixture-skill", RUNNER.get_allowlisted_skills())

    def test_arbitrary_skill_never_reaches_subprocess(self):
        with self.assertRaises(ValueError):
            RUNNER.execute_skill("fixture-skill; shutdown")
        self.mock_run.assert_not_called()

    def test_execution_passes_real_prompt_scoped_tools_and_limits(self):
        result = RUNNER.execute_skill("fixture-skill")
        command = self.mock_run.call_args.args[0]
        options = self.mock_run.call_args.kwargs
        self.assertIs(options["shell"], False)
        self.assertEqual(options["cwd"], str(self.workspace))
        self.assertEqual(options["timeout"], 43)
        self.assertIn(SKILL_TEXT, options["input"])
        self.assertIn("skills/fixture-skill/", options["input"])
        self.assertEqual(command[command.index("--model") + 1], "haiku")
        self.assertEqual(command[command.index("--effort") + 1], "low")
        self.assertEqual(command[command.index("--max-budget-usd") + 1], "0.17")
        self.assertEqual(set(command[command.index("--tools") + 1].split(",")), {"Read", "Write", "Edit"})
        allow_start = command.index("--allowed-tools") + 1
        actual_allowlist = []
        for argument in command[allow_start:]:
            if argument.startswith("--"):
                break
            actual_allowlist.append(argument)
        self.assertEqual(actual_allowlist, RUNNER.get_allowlisted_skills()["fixture-skill"]["allowed_tools"])
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["cost_usd"], 0.07)
        audit = json.loads(RUNNER.RUNS_LOG.read_text(encoding="utf-8"))
        self.assertEqual(audit, result)
        self.assertFalse(RUNNER.LOCK_FILE.exists())

    def test_headless_runtime_excludes_unvetted_mcp_and_hooks(self):
        RUNNER.execute_skill("fixture-skill")
        command = self.mock_run.call_args.args[0]
        self.assertIn("--strict-mcp-config", command)
        self.assertEqual(json.loads(command[command.index("--mcp-config") + 1]), {"mcpServers": {}})
        self.assertEqual(command[command.index("--permission-mode") + 1], "dontAsk")
        self.assertEqual(command[command.index("--setting-sources") + 1], "")
        self.assertTrue(json.loads(command[command.index("--settings") + 1])["disableAllHooks"])
        self.assertIn("--no-session-persistence", command)
        self.assertNotIn("--dangerously-skip-permissions", command)

    def test_json_agent_errors_and_denials_fail_even_with_zero_process_exit(self):
        for payload in ({"is_error": True, "result": "Agent failed"}, {"permission_denials": [{"tool_name": "Write"}], "result": "Permission denied"}):
            with self.subTest(payload=payload):
                self.mock_run.return_value = subprocess.CompletedProcess([], 0, json.dumps(payload), "")
                result = RUNNER.execute_skill("fixture-skill")
                self.assertNotEqual(result["exit_code"], 0)
                self.assertTrue(result["error"])

    def test_invalid_json_is_failure(self):
        self.mock_run.return_value = subprocess.CompletedProcess([], 0, "not json", "")
        result = RUNNER.execute_skill("fixture-skill")
        self.assertNotEqual(result["exit_code"], 0)
        self.assertTrue(result["error"])

    def test_process_failure_is_preserved(self):
        self.mock_run.return_value = subprocess.CompletedProcess([], 7, "", "CLI unavailable")
        result = RUNNER.execute_skill("fixture-skill")
        self.assertEqual(result["exit_code"], 7)
        self.assertIn("CLI unavailable", result["error"])

    def test_failed_run_preserves_spend_and_json_error(self):
        self.mock_run.return_value = subprocess.CompletedProcess([], 7, json.dumps({"total_cost_usd": 0.11, "is_error": True, "result": "Budget exceeded"}), "")
        result = RUNNER.execute_skill("fixture-skill")
        self.assertEqual(result["exit_code"], 7)
        self.assertEqual(result["cost_usd"], 0.11)
        self.assertEqual(result["error"], "Budget exceeded")
        self.assertEqual(json.loads(RUNNER.RUNS_LOG.read_text(encoding="utf-8")), result)

    def test_timeout_releases_lock_and_is_audited(self):
        self.mock_run.side_effect = subprocess.TimeoutExpired("fixture-claude", 43)
        result = RUNNER.execute_skill("fixture-skill")
        self.assertEqual(result["exit_code"], 124)
        self.assertFalse(RUNNER.LOCK_FILE.exists())
        self.assertEqual(json.loads(RUNNER.RUNS_LOG.read_text(encoding="utf-8"))["exit_code"], 124)

    def test_mutex_exclusivity_does_not_remove_owner_lock(self):
        with RUNNER.WorkspaceLock():
            owner = RUNNER.LOCK_FILE.read_bytes()
            with self.assertRaises(BlockingIOError):
                with RUNNER.WorkspaceLock():
                    self.fail("A second owner acquired the mutex")
            result = RUNNER.execute_skill("fixture-skill")
            self.assertEqual(result["exit_code"], 423)
            self.assertEqual(RUNNER.LOCK_FILE.read_bytes(), owner)
            self.mock_run.assert_not_called()
        self.assertFalse(RUNNER.LOCK_FILE.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
