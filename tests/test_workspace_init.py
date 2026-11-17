#!/usr/bin/env python3
"""Verify clean-checkout initialization without touching the user's private data."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("workspace_initializer", ROOT / "scripts/init-workspace.py")
INITIALIZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INITIALIZER)


class WorkspaceInitializationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="agentic-os-clean-checkout-")
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name)

    def test_creates_private_layout_and_no_credentials(self):
        created = INITIALIZER.initialize(self.workspace)
        self.assertEqual(len(created), 4)
        for relative in ("vault/raw", "vault/wiki", "output/artifacts"):
            self.assertTrue((self.workspace / relative).is_dir())
        for relative in ("output/runs.log", "output/approval_queue.jsonl"):
            self.assertEqual((self.workspace / relative).read_bytes(), b"")
        constitution = (self.workspace / "vault/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("immutable", constitution)
        self.assertIn("output/approval_queue.jsonl", constitution)
        self.assertFalse((self.workspace / ".local-token").exists())
        self.assertFalse((self.workspace / ".env").exists())

    def test_repeat_initialization_preserves_existing_private_files(self):
        INITIALIZER.initialize(self.workspace)
        examples = {
            "vault/AGENTS.md": b"# Personal constitution\n",
            "vault/raw/private.md": b"Immutable private evidence\n",
            "vault/wiki/private.md": b"Existing knowledge\n",
            "output/runs.log": b'{"run_id":"existing"}\n',
            "output/approval_queue.jsonl": b'{"id":"existing","status":"pending"}\n',
            "output/artifacts/lint-report.md": b"# Existing verification report\n",
        }
        for relative, content in examples.items():
            (self.workspace / relative).write_bytes(content)
        before = {relative: (self.workspace / relative).stat().st_mtime_ns for relative in examples}
        self.assertEqual(INITIALIZER.initialize(self.workspace), [])
        for relative, content in examples.items():
            with self.subTest(path=relative):
                self.assertEqual((self.workspace / relative).read_bytes(), content)
                self.assertEqual((self.workspace / relative).stat().st_mtime_ns, before[relative])

    def test_synthetic_clean_checkout_lints_after_first_initialization(self):
        scripts = self.workspace / "scripts"
        scripts.mkdir()
        for name in ("init-workspace.py", "lint-routers.py"):
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        (self.workspace / "memory").mkdir()
        (self.workspace / "CLAUDE.md").write_text("# Router\n[Constitution](vault/AGENTS.md)\n[Content](memory/CONTENT.md)\n", encoding="utf-8")
        (self.workspace / "memory/CONTENT.md").write_text(
            "# Content\n[Raw](../vault/raw/)\n[Wiki](../vault/wiki/)\n"
            "[Audit](../output/runs.log)\n[Queue](../output/approval_queue.jsonl)\n"
            "[Lint report](../output/artifacts/lint-report.md)\n", encoding="utf-8")
        # Invoke the copied CLI from another cwd to verify script-relative roots.
        initialized = subprocess.run([sys.executable, str(scripts / "init-workspace.py")], cwd=ROOT, capture_output=True, text=True, shell=False)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        checked = subprocess.run([sys.executable, str(scripts / "lint-routers.py")], cwd=self.workspace, capture_output=True, text=True, shell=False)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        report = (self.workspace / "output/artifacts/lint-report.md").read_text(encoding="utf-8")
        self.assertIn("**Broken Links:** 0", report)
        self.assertIn("**Unindexed Orphan Files:** 0", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
