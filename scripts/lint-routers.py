#!/usr/bin/env python3
"""Agentic OS — Router Linter Script

Validates that all markdown links in CLAUDE.md and memory/*.md point to valid files.
Flags orphan files in vault/wiki/ and output/artifacts/ that are not indexed.
Outputs report to output/artifacts/lint-report.md and exits 1 if broken links exist.
"""

import os
import re
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

def parse_markdown_links(file_path: Path):
    """Extract (text, target_path) tuples from a markdown file."""
    if not file_path.is_file():
        return []
    content = file_path.read_text(encoding="utf-8")
    links = []
    for match in LINK_PATTERN.finditer(content):
        text = match.group(1)
        target = match.group(2).strip()
        # Skip external web URLs and anchors
        if target.startswith("http://") or target.startswith("https://") or target.startswith("#"):
            continue
        links.append((text, target))
    return links

def lint_routers():
    print(f"Linting routers for workspace: {WORKSPACE_ROOT}")
    broken_links = []
    indexed_targets = set()

    # Router files to check
    router_files = [WORKSPACE_ROOT / "CLAUDE.md"]
    memory_dir = WORKSPACE_ROOT / "memory"
    if memory_dir.is_dir():
        for mf in memory_dir.glob("*.md"):
            router_files.append(mf)

    for rf in router_files:
        if not rf.exists():
            broken_links.append((str(rf), "Self", "File does not exist"))
            continue
        links = parse_markdown_links(rf)
        for text, target in links:
            # Resolve relative to the router file's parent directory
            resolved = (rf.parent / target).resolve()
            indexed_targets.add(resolved)
            if not resolved.exists():
                broken_links.append((str(rf.relative_to(WORKSPACE_ROOT)), target, text))

    # Detect orphan files in vault/wiki and output/artifacts
    orphans = []
    scan_dirs = [WORKSPACE_ROOT / "vault" / "wiki", WORKSPACE_ROOT / "output" / "artifacts"]
    for sdir in scan_dirs:
        if sdir.is_dir():
            for f in sdir.glob("*"):
                if f.is_file() and f.name != "lint-report.md" and f.name != ".gitkeep":
                    if f.resolve() not in indexed_targets:
                        orphans.append(str(f.relative_to(WORKSPACE_ROOT)))

    # Generate Markdown report
    report_lines = [
        "# Router Linting Report",
        f"**Run Timestamp:** {os.popen('powershell -Command Get-Date -Format o').read().strip() if sys.platform == 'win32' else 'Timestamp'}",
        f"**Workspace:** `{WORKSPACE_ROOT}`",
        "",
        "## Summary",
        f"- **Router Files Scanned:** {len(router_files)}",
        f"- **Broken Links:** {len(broken_links)}",
        f"- **Unindexed Orphan Files:** {len(orphans)}",
        "",
        "## Broken Links",
    ]

    if broken_links:
        report_lines.append("| Source Router | Target Link | Text |")
        report_lines.append("| :--- | :--- | :--- |")
        for src, tgt, txt in broken_links:
            report_lines.append(f"| `{src}` | `{tgt}` | {txt} |")
    else:
        report_lines.append("No broken links found. All router pointers resolve cleanly.")

    report_lines.append("")
    report_lines.append("## Unindexed Orphan Files")
    if orphans:
        for o in orphans:
            report_lines.append(f"- `{o}`")
    else:
        report_lines.append("No unindexed orphan files found in monitored directories.")

    out_file = WORKSPACE_ROOT / "output" / "artifacts" / "lint-report.md"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report written to: {out_file.relative_to(WORKSPACE_ROOT)}")

    if broken_links:
        print(f"FAILED: Found {len(broken_links)} broken link(s).", file=sys.stderr)
        return 1

    print("SUCCESS: All router links verified.")
    return 0

if __name__ == "__main__":
    sys.exit(lint_routers())
