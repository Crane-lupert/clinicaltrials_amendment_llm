"""Smoke tests - run as `pytest tests/test_smoke.py`.

Day 1 sanity only. Day 2+ adds integration tests against live CT.gov v2.
"""

from pathlib import Path

import pytest

from clinicaltrials_amendment_llm import manifest, pdf_parser
from clinicaltrials_amendment_llm.ctgov_client import DaemonViolationError, _assert_allowed_url


def test_manifest_global_bootstrap(tmp_path, monkeypatch):
    """read_global returns a sane default when no manifest exists."""
    monkeypatch.setattr(manifest, "DATA_DIR", tmp_path)
    monkeypatch.setattr(manifest, "MANIFEST_GLOBAL", tmp_path / "manifest_global.json")
    state = manifest.read_global()
    assert state["phase"] == "phase0"
    assert state["current_task"] == manifest.TASK_SEQUENCE[0]
    assert state["done"] == []


def test_manifest_mark_done_advances(tmp_path, monkeypatch):
    monkeypatch.setattr(manifest, "DATA_DIR", tmp_path)
    monkeypatch.setattr(manifest, "MANIFEST_GLOBAL", tmp_path / "manifest_global.json")
    state = manifest.mark_done(manifest.TASK_SEQUENCE[0])
    assert manifest.TASK_SEQUENCE[0] in state["done"]
    assert state["current_task"] == manifest.TASK_SEQUENCE[1]


def test_ctgov_client_blocks_sec_url():
    with pytest.raises(DaemonViolationError):
        _assert_allowed_url("https://www.sec.gov/cgi-bin/browse-edgar?")
    with pytest.raises(DaemonViolationError):
        _assert_allowed_url("https://data.sec.gov/submissions/CIK0000320193.json")


def test_ctgov_client_allows_ctgov_url():
    _assert_allowed_url("https://clinicaltrials.gov/api/v2/studies/NCT00000000")
    _assert_allowed_url("https://www.clinicaltrials.gov/api/v2/studies")


def test_pdf_parser_no_pdf_bin():
    r = pdf_parser.parse_pdf(Path("__definitely_does_not_exist__.pdf"))
    assert r.bin == "no_pdf"
    assert r.text == ""


def test_pdf_parser_yield_summary_threshold():
    """Trigger #6: success+partial >= 80% over n=20."""
    # Synthetic: 16/20 success, 4/20 ocr_required -> 80%
    results = [
        pdf_parser.ParseResult("success", "x", 1, 100, "pdfplumber", "h")
        for _ in range(16)
    ] + [
        pdf_parser.ParseResult("ocr_required", "", 1, 0, "pdfplumber", None)
        for _ in range(4)
    ]
    summary = pdf_parser.yield_bins_summary(results)
    assert summary["n_total"] == 20
    assert summary["success_partial_rate"] == pytest.approx(0.80)
    assert summary["trigger6_pass"] is True

    # 15/20 = 75% -> trigger #6 fires
    results2 = [
        pdf_parser.ParseResult("success", "x", 1, 100, "pdfplumber", "h")
        for _ in range(15)
    ] + [
        pdf_parser.ParseResult("ocr_required", "", 1, 0, "pdfplumber", None)
        for _ in range(5)
    ]
    summary2 = pdf_parser.yield_bins_summary(results2)
    assert summary2["trigger6_pass"] is False
