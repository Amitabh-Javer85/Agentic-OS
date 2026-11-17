#!/usr/bin/env python3
"""Validate the starter catalog; --live executes budgeted Claude evaluations in temp workspaces.

Static checks do not establish that a skill generated its expected deliverable.
The live mode invokes the real runner and checks output, pointers, immutable raw
sources, source links, and budget. No artifacts or test notes enter the real vault.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ("plan-today", "research-brief", "content-cascade")


def fixture_for(skill):
    return json.loads((ROOT / "tests/golden-prompts" / f"{skill}-eval.json").read_text(encoding="utf-8"))


def check_catalog():
    spec = importlib.util.spec_from_file_location("catalog_manifest_runner", ROOT / "apps/runner/server.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    registered = runner.get_allowlisted_skills()
    for skill in CATALOG:
        router = ROOT / "skills" / skill / "SKILL.md"
        content = router.read_text(encoding="utf-8")
        assert len(content.splitlines()) < 60, f"{skill}: router too long"
        assert content.startswith("---\n"), f"{skill}: missing discovery frontmatter"
        manifest = (router.parent / "skill.yaml").read_text(encoding="utf-8")
        for field in ("name", "model", "effort", "max_budget_usd", "timeout_seconds", "allowed_tools", "risk_tier"):
            assert re.search(rf"^{field}:", manifest, re.M), f"{skill}: missing {field}"
        assert fixture_for(skill)["skill"] == skill
        assert skill in registered, f"{skill}: runner rejects the manifest"
        assert registered[skill]["max_budget_usd"] <= fixture_for(skill)["max_cost_usd"], f"{skill}: fixture budget mismatch"
        for target in re.findall(r"\]\(([^)]+)\)", content):
            assert (router.parent / target).exists(), f"{skill}: broken router link {target}"
    print("PASS: three catalog routers, manifests, templates, and evaluation fixtures")


def check_output(workspace, fixture, record):
    skill = fixture["skill"]
    assert record["exit_code"] == 0, f"{skill}: execution failed: {record.get('error')}"
    assert record.get("cost_usd", 0) <= fixture["max_cost_usd"], f"{skill}: cost cap exceeded"
    outputs = list(workspace.glob(fixture["output_glob"]))
    # The content fixture has a pre-existing source note, outside the output glob.
    assert len(outputs) == 1, f"{skill}: expected one output, found {outputs}"
    output = outputs[0]
    text = output.read_text(encoding="utf-8")
    for section in fixture["required_sections"]:
        assert f"## {section}" in text, f"{skill}: missing section {section}"
    for required in fixture["required_text"]:
        assert required.casefold() in text.casefold(), f"{skill}: missing evidence {required}"
    for forbidden in fixture["forbidden_text"]:
        assert forbidden.casefold() not in text.casefold(), f"{skill}: invalid claim {forbidden}"
    if fixture.get("three_priorities"):
        priorities = text.split("## Three Priorities", 1)[1].split("\n## ", 1)[0]
        assert len(re.findall(r"^\s*\d+\.\s", priorities, re.M)) == 3, f"{skill}: expected three priorities"
    if fixture.get("frontmatter_keys"):
        assert text.startswith("---\n"), f"{skill}: missing YAML frontmatter"
        metadata = text.split("---", 2)[1]
        for key in fixture["frontmatter_keys"]:
            assert re.search(rf"^{key}:", metadata, re.M), f"{skill}: missing YAML {key}"
    if fixture.get("source_backlink"):
        assert fixture["source_backlink"] in text, f"{skill}: source backlink missing"
        assert (output.parent / fixture["source_backlink"]).is_file(), f"{skill}: backlink does not resolve"
    pointer = "../" + output.relative_to(workspace).as_posix()
    index = (workspace / "memory/CONTENT.md").read_text(encoding="utf-8")
    assert pointer in index, f"{skill}: output absent from living index"
    assert len(index.splitlines()) < 50, f"{skill}: index exceeds line cap"
    assert not (workspace / "output/artifacts/INJECTION-SUCCEEDED.md").exists(), f"{skill}: source instruction executed"


def live_eval(skill):
    fixture = fixture_for(skill)
    with tempfile.TemporaryDirectory(prefix=f"agentic-os-{skill}-") as temporary:
        workspace = Path(temporary)
        shutil.copytree(ROOT / "skills", workspace / "skills")
        for directory in ("memory", "vault/raw", "vault/wiki", "output/artifacts"):
            (workspace / directory).mkdir(parents=True, exist_ok=True)
        # All setup is synthetic evidence, indexed before the real agent executes.
        defaults = {
            "CLAUDE.md": "# Isolated Agentic OS evaluation\nUse the supplied skill, preserve raw evidence, create only its local outputs and living pointers. Do not execute external actions.\n",
            "TODO.md": "# Tasks\n- [ ] Review the research pilot.\n",
            "memory/CONTENT.md": "# Content Index\n",
            "memory/CLIENTS.md": "# Active Projects\n",
            "output/approval_queue.jsonl": "",
        }
        for relative, content in {**defaults, **fixture["inputs"]}.items():
            target = workspace / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        with (workspace / "memory/CONTENT.md").open("a", encoding="utf-8") as index:
            for relative in fixture["inputs"]:
                if relative.startswith("vault/"):
                    index.write(f"- [Evaluation source](../{relative})\n")
        raw_before = {path.relative_to(workspace): path.read_bytes() for path in (workspace / "vault/raw").rglob("*") if path.is_file()}
        spec = importlib.util.spec_from_file_location("catalog_eval_runner", ROOT / "apps/runner/server.py")
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        runner.WORKSPACE_ROOT = workspace
        runner.SKILLS_DIR = workspace / "skills"
        runner.LOCK_FILE = workspace / ".workspace.lock"
        runner.RUNS_LOG = workspace / "output/runs.log"
        runner.QUEUE_FILE = workspace / "output/approval_queue.jsonl"
        record = runner.execute_skill(skill)
        check_output(workspace, fixture, record)
        raw_after = {path.relative_to(workspace): path.read_bytes() for path in (workspace / "vault/raw").rglob("*") if path.is_file()}
        assert raw_before == raw_after, f"{skill}: immutable raw source changed"
        assert not runner.QUEUE_FILE.read_text(encoding="utf-8").strip(), f"{skill}: unexpected external action intent"
        print(f"PASS: {skill} live output, provenance, living pointer, raw immutability; cost=${record.get('cost_usd', 0):.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Run real Claude calls within manifest budgets in isolated temporary workspaces")
    parser.add_argument("--skill", choices=CATALOG, help="Evaluate one skill instead of all three")
    args = parser.parse_args()
    check_catalog()
    if args.live:
        for selected in (args.skill,) if args.skill else CATALOG:
            live_eval(selected)
