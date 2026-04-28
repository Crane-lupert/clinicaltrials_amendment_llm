"""Streamlit Cloud entry point.

Streamlit Cloud auto-discovers `streamlit_app.py` at the repo root.
This is a thin wrapper that delegates to the actual dashboard implementation
in `src/clinicaltrials_amendment_llm/dashboard.py`.

The dashboard reads pre-computed results from `analysis/*.json` and
`data/manifest_*.jsonl` (all git-tracked) — no live API calls, no secrets,
no shared_utils dependency.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure `src/` is on sys.path so `clinicaltrials_amendment_llm` package resolves
# even though Streamlit Cloud runs from repo root, not from an installed editable.
_REPO_ROOT = Path(__file__).resolve().parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from clinicaltrials_amendment_llm.dashboard import main

main()
