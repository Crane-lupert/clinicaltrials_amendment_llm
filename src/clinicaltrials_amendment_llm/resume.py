"""Resume entry point.

Run: `python -m clinicaltrials_amendment_llm.resume`
- Reads manifest_global.json
- Prints current phase / next task / undone task list
- Used at start of every Claude session for re-anchoring (drift-watchdog Rule 25)

Graceful exits write RESUMABLE.md (next-action notes); ABANDONED.md is
written by the kill-gate path only (NOT here).
"""

from __future__ import annotations

import sys

from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    TASK_SEQUENCE,
    ensure_data_dir,
    read_global,
    undone_tasks,
)


def main() -> int:
    ensure_data_dir()
    state = read_global()
    undone = undone_tasks(state)

    print(f"=== F6 (clinicaltrials_amendment_llm) RESUME ===")
    print(f"Phase: {state['phase']}")
    print(f"Current task: {state.get('current_task')}")
    print(f"Done: {len(state.get('done', []))} / {len(TASK_SEQUENCE)}")
    print(f"Undone: {len(undone)}")
    print(f"Spend phase0: ${state.get('spend_phase0', 0.0):.2f} / $8 cap")
    print(f"Spend phase1: ${state.get('spend_phase1', 0.0):.2f} / $22 cap")
    print(f"Data dir: {DATA_DIR}")
    print()
    print("Next 5 undone tasks:")
    for t in undone[:5]:
        print(f"  - {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
