#!/usr/bin/env python3
"""Initialize gitignored local data after cloning; preserve every existing file."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION = """# Vault Constitution

1. `vault/raw/` is immutable source intake: never modify or delete its files.
2. Generated knowledge belongs in `vault/wiki/`; deliverables belong in
   `output/artifacts/`. Preserve source attribution and distinguish inference.
3. When creating, moving, or deleting a file, update its `memory/*.md` pointer
   in the same turn. Keep each domain index under 50 lines.
4. Headless external mutations, including send, spend, publish, and deletion,
   must become pending intents in `output/approval_queue.jsonl` for human review.
   Approval records do not themselves execute the external action.
5. Record significant automated runs in `output/runs.log` as JSONL.
6. Keep credentials and private vault content out of Git. Use the Claude Code
   runtime directly; do not add legacy infrastructure or shell execution.

Raw notes use YAML `title`, `source`, and `tags`; compiled notes retain source
backlinks and use lowercase kebab-case tags. Follow the root `CLAUDE.md` router
and the registered skill manifest's tool, cost, timeout, and write boundaries.
"""


def initialize(workspace: Path) -> list[str]:
    """Create only missing private data paths; never generate credentials."""
    for relative in ("vault/raw", "vault/wiki", "output/artifacts"):
        (workspace / relative).mkdir(parents=True, exist_ok=True)
    files = {
        "vault/AGENTS.md": CONSTITUTION,
        "output/runs.log": "",
        "output/approval_queue.jsonl": "",
        "output/artifacts/lint-report.md": "# Router Linting Report\n\nNot yet verified. Run `python scripts/lint-routers.py`.\n",
    }
    created = []
    for relative, content in files.items():
        try:
            with (workspace / relative).open("x", encoding="utf-8") as stream:
                stream.write(content)
        except FileExistsError:
            continue
        created.append(relative)
    return created


if __name__ == "__main__":
    created = initialize(ROOT)
    print(f"Local workspace ready; created {len(created)} missing data files. Existing files preserved.")
