"""F6 manifest helpers - thin wrapper around shared_utils.atomic_io.

Manifests:
- manifest_global.json - phase / current_task / last_synced
- manifest_amendment_fetch.jsonl - per-(NCT, version) fetch status
- manifest_pdf_parse.jsonl - per-amendment PDF parse status
- manifest_pdf_parse_audit.jsonl - 5-bin yield distribution (F6 special)
- manifest_axis_classify.jsonl - per-(amendment, model) LLM 3-axis label
- manifest_sponsor_map.jsonl - NCT -> sponsor -> ticker
- manifest_phase_transition.jsonl - phase transition outcome join
- manifest_car.jsonl - per-(event, horizon) forward CAR
- manifest_oracle_kappa.json - n=20 oracle 3-vendor Fleiss kappa
- manifest_ctp_llm_baseline.jsonl - CTP-LLM phase transition replication
- manifest_incremental_sharpe.jsonl - delta Sharpe measurement
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Iterable

from filelock import FileLock
from shared_utils.atomic_io import atomic_write_json

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"

MANIFEST_GLOBAL = DATA_DIR / "manifest_global.json"
MANIFEST_AMENDMENT_FETCH = DATA_DIR / "manifest_amendment_fetch.jsonl"
MANIFEST_PDF_PARSE = DATA_DIR / "manifest_pdf_parse.jsonl"
MANIFEST_PDF_PARSE_AUDIT = DATA_DIR / "manifest_pdf_parse_audit.jsonl"
MANIFEST_AXIS_CLASSIFY = DATA_DIR / "manifest_axis_classify.jsonl"
MANIFEST_SPONSOR_MAP = DATA_DIR / "manifest_sponsor_map.jsonl"
MANIFEST_PHASE_TRANSITION = DATA_DIR / "manifest_phase_transition.jsonl"
MANIFEST_CAR = DATA_DIR / "manifest_car.jsonl"
MANIFEST_ORACLE_KAPPA = DATA_DIR / "manifest_oracle_kappa.json"
MANIFEST_CTP_LLM_BASELINE = DATA_DIR / "manifest_ctp_llm_baseline.jsonl"
MANIFEST_INCREMENTAL_SHARPE = DATA_DIR / "manifest_incremental_sharpe.jsonl"

# Ordered Day 1..21 task slugs - resume.py reads this and the global manifest
# `done` set to compute the next undone task.
TASK_SEQUENCE: list[str] = [
    # Day 1
    "day1_git_init",
    "day1_pyproject_skeleton",
    "day1_manifest_resume_skeleton",
    "day1_ctgov_client_skeleton",
    "day1_pdf_parser_skeleton",
    "day1_ctp_llm_baseline_spec",
    "day1_arxiv_scoop_check",
    "day1_openrouter_register",
    "day1_daily_checkpoint",
    "day1_self_audit",
    # Day 2
    "day2_biotech_universe_filter",
    "day2_amendment_fetch_first",
    "day2_sponsor_ticker_skeleton",
    "day2_self_audit",
    # Day 3-5: PDF parser dry-run + n=10 + n=20 oracle
    "day3_pdf_parser_dry_run",
    "day4_n10_dry_run_start",
    "day4_n20_oracle_start",
    "day5_n10_dry_run_complete",
    "day5_pdf_parsing_yield_first",
    "day5_n20_oracle_complete",
    "day5_self_audit_trigger1",
    # Day 6-7: kappa + kill gate
    "day6_n10_dry_run_second",
    "day6_oracle_kappa_measure",
    "day6_pdf_parsing_yield_second",
    "day7_phase0_kill_gate",
    "day7_self_audit_phase0_transition",
    # Phase 1
    "day8_full_sample_inference_start",
    "day11_sponsor_ticker_full",
    "day12_phase_transition_join",
    "day13_ctp_llm_baseline_replication",
    "day14_phase1_mid_checkpoint",
    "day15_cross_section_car",
    "day16_vaccine_cohort_stratum",
    "day17_ctp_llm_incremental_sharpe",
    "day18_self_audit_trigger2",
    "day19_rigor_pass",
    "day20_writeup_dashboard",
    "day21_phase1_hard_cap",
]


def _now_iso() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).isoformat()


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cache").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cache" / "llm_responses").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "cache" / "parsed").mkdir(parents=True, exist_ok=True)


def read_global() -> dict[str, Any]:
    if not MANIFEST_GLOBAL.exists():
        return {
            "phase": "phase0",
            "current_task": TASK_SEQUENCE[0],
            "done": [],
            "last_synced": _now_iso(),
            "spend_phase0": 0.0,
            "spend_phase1": 0.0,
        }
    with MANIFEST_GLOBAL.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_global(state: dict[str, Any]) -> None:
    ensure_data_dir()
    state["last_synced"] = _now_iso()
    atomic_write_json(MANIFEST_GLOBAL, state)


def mark_done(task: str) -> dict[str, Any]:
    """Mark a task as completed and advance current_task."""
    state = read_global()
    if task not in state["done"]:
        state["done"].append(task)
    remaining = [t for t in TASK_SEQUENCE if t not in state["done"]]
    state["current_task"] = remaining[0] if remaining else None
    if state["current_task"] and state["current_task"].startswith("day8") and state["phase"] == "phase0":
        state["phase"] = "phase1"
    write_global(state)
    return state


def undone_tasks(state: dict[str, Any] | None = None) -> list[str]:
    state = state or read_global()
    return [t for t in TASK_SEQUENCE if t not in state.get("done", [])]


def _lock_path(path: Path) -> Path:
    return path.with_suffix(path.suffix + ".lock")


def append_manifest(path: Path, record: dict[str, Any]) -> None:
    """Append-only JSONL manifest write under a per-file FileLock.

    JSONL is line-atomic on POSIX/Windows when the write fits in a single
    write() call. The FileLock guards multi-process append from
    interleaving (race fix from F1 wave).
    """
    ensure_data_dir()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {**record, "_ts": _now_iso()}
    line = json.dumps(record, ensure_ascii=False, default=str) + "\n"
    with FileLock(str(_lock_path(path))):
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line)


def read_manifest(path: Path) -> Iterable[dict[str, Any]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


if __name__ == "__main__":
    # Sanity: bootstrap empty manifest
    ensure_data_dir()
    state = read_global()
    write_global(state)
    print(f"manifest_global: phase={state['phase']} current_task={state['current_task']}")
    print(f"undone: {len(undone_tasks(state))} tasks")
