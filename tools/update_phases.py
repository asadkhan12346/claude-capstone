"""Maintenance script — update phases.json prompt paths to use consolidated commands.

Phases 1-7 → .claude/commands/run.md
Phase 8 (pr) → .claude/commands/pr.md

Run once: python tools/update_phases.py
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASES_PATH = ROOT / "sdlc" / "phases.json"


def main() -> None:
    data = json.loads(PHASES_PATH.read_text(encoding="utf-8"))

    for phase in data["phases"]:
        if phase["id"] == "pr":
            phase["prompt"] = ".claude/commands/pr.md"
        else:
            phase["prompt"] = ".claude/commands/run.md"

    # Atomic write (same pattern as orchestrator.py)
    tmp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=PHASES_PATH.parent, delete=False, newline="\n"
        ) as tmp:
            tmp_name = tmp.name
            json.dump(data, tmp, indent=2, ensure_ascii=False)
            tmp.write("\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, PHASES_PATH)
    finally:
        if tmp_name and os.path.exists(tmp_name):
            os.unlink(tmp_name)

    print("Updated sdlc/phases.json:")
    for phase in data["phases"]:
        print(f"  {phase['id']:15} prompt -> {phase['prompt']}")


if __name__ == "__main__":
    main()
