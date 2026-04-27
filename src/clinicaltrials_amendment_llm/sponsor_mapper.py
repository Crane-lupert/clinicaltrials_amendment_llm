"""Day 11 sponsor -> ticker expansion (filer_ontology + parent rollup).

Phase 1 trigger #7: final analyzable n >= 1,500. Day 5 had 17% mapping rate
(607 / 3,500) using the 77-firm BIOTECH_R1000_SEED. Need more coverage.

Sources (in priority order):
1. biotech_universe.BIOTECH_R1000_SEED (77 firms, hand-curated, includes parent rollup
   for subsidiaries like Janssen -> JNJ).
2. SEC company_tickers.json (10,341 SEC-listed firms, CIK + ticker + title).
   Filtered to biotech-relevant by keyword match (biotech / pharma / therapeutic /
   biopharm / oncology / genetics / sciences / life-sci).
3. Parent rollup heuristics (Genentech -> ROG.SW; Janssen -> JNJ; Pfizer subsidiaries -> PFE).

PURE daemon-free (Gate F): static file reads only, no SEC EDGAR API call.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from clinicaltrials_amendment_llm.biotech_universe import (
    BIOTECH_R1000_SEED,
    normalize_sponsor_name,
)

COMPANY_TICKERS_PATH = Path("D:/vscode/portfolio-coordination/sec-data/company_tickers.json")

# Keywords that suggest a SEC-listed entry is a biotech / pharma / life-science firm.
# Used to filter the 10K-row company_tickers.json down to biotech-relevant subset.
BIOTECH_KEYWORDS = (
    "biotech", "pharma", "therapeutic", "biopharm", "oncology", "genetic",
    "sciences", "life sci", "lifesci", "medicines", "gene therapy",
    "cell therap", "vaccine", "immuno", "diagnostic", "molecular",
    "genom", "biolog", "neuro",
)

# Parent rollup: when CT.gov sponsor is a subsidiary, map to public-traded parent.
# Conservative list - only well-known structural relationships (industry-standard).
PARENT_ROLLUP: dict[str, str] = {
    # Janssen variants -> Johnson & Johnson
    "janssen pharmaceuticals": "JNJ",
    "janssen research & development": "JNJ",
    "janssen biotech": "JNJ",
    "janssen sciences ireland": "JNJ",
    "janssen-cilag international": "JNJ",
    # Genentech -> Roche
    "genentech": "ROG.SW",
    # Pfizer variants
    "pfizer global research and development": "PFE",
    "pfizer global research & development": "PFE",
    # Merck KGaA Darmstadt vs MRK is risky to rollup blindly; skip.
    # Sanofi-Aventis variants
    "sanofi-aventis recherche": "SNY",
    "sanofi-aventis u.s.": "SNY",
    "sanofi-aventis": "SNY",
    "sanofi-pasteur": "SNY",
    # GSK variants
    "glaxosmithkline": "GSK",
    "smithkline beecham": "GSK",
    # Novartis variants
    "novartis pharma ag": "NVS",
    "novartis pharma services": "NVS",
    "novartis pharmaceuticals corporation": "NVS",
    # AstraZeneca variants
    "astrazeneca ab": "AZN",
    "astrazeneca pharmaceuticals lp": "AZN",
    # Bristol-Myers Squibb variants
    "bristol-myers squibb international": "BMY",
}


@lru_cache(maxsize=1)
def _load_sec_biotech_index() -> dict[str, str]:
    """Load company_tickers.json, filter biotech-relevant, return {norm_name: ticker}."""
    if not COMPANY_TICKERS_PATH.exists():
        return {}
    data = json.loads(COMPANY_TICKERS_PATH.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for v in data.values():
        if not isinstance(v, dict):
            continue
        ticker = v.get("ticker")
        title = v.get("title", "")
        if not ticker or not title:
            continue
        title_l = title.lower()
        # Keep only biotech-relevant
        if not any(kw in title_l for kw in BIOTECH_KEYWORDS):
            continue
        norm = normalize_sponsor_name(title)
        if norm:
            out[norm] = ticker
    return out


@lru_cache(maxsize=1)
def _seed_index() -> dict[str, str]:
    """Flatten BIOTECH_R1000_SEED into {norm_name: ticker}."""
    out: dict[str, str] = {}
    for ticker, names in BIOTECH_R1000_SEED.items():
        for name in names:
            norm = normalize_sponsor_name(name)
            if norm:
                out[norm] = ticker
    return out


def lookup_ticker_expanded(sponsor_name: str) -> tuple[str | None, str]:
    """Returns (ticker, source).

    source ∈ {seed, parent_rollup, sec_biotech_index, none}.
    Order: seed exact → seed startswith → parent rollup → sec biotech (exact) →
    sec biotech (startswith).
    """
    if not sponsor_name:
        return None, "none"

    norm = normalize_sponsor_name(sponsor_name)
    if not norm:
        return None, "none"

    # 1. Seed exact
    seed = _seed_index()
    if norm in seed:
        return seed[norm], "seed"

    # 2. Parent rollup
    for k, v in PARENT_ROLLUP.items():
        if norm.startswith(k) or k in norm:
            return v, "parent_rollup"

    # 3. Seed startswith / contains
    for sn, tk in seed.items():
        if norm.startswith(sn) or sn.startswith(norm):
            # Avoid overly aggressive: require >= 4 chars overlap on shorter side
            if min(len(norm), len(sn)) >= 4:
                return tk, "seed_partial"

    # 4. SEC biotech index exact
    sec_idx = _load_sec_biotech_index()
    if norm in sec_idx:
        return sec_idx[norm], "sec_biotech_exact"

    # 5. SEC biotech index startswith
    for sn, tk in sec_idx.items():
        if norm.startswith(sn) or sn.startswith(norm):
            if min(len(norm), len(sn)) >= 5:
                return tk, "sec_biotech_partial"

    return None, "none"


def update_manifest_with_expanded_tickers() -> dict:
    """Re-map all manifest_amendment_fetch records with the expanded mapper.

    Reads each record, computes new ticker via lookup_ticker_expanded, returns
    summary stats. Does NOT mutate the manifest in place; instead writes a
    sidecar manifest_sponsor_map.jsonl with (nct_id, sponsor_name, old_ticker,
    new_ticker, source).
    """
    from clinicaltrials_amendment_llm.manifest import (
        MANIFEST_AMENDMENT_FETCH,
        MANIFEST_SPONSOR_MAP,
        append_manifest,
        read_manifest,
    )

    stats = {
        "total": 0,
        "old_mapped": 0,
        "new_mapped": 0,
        "by_source": {"seed": 0, "seed_partial": 0, "parent_rollup": 0,
                      "sec_biotech_exact": 0, "sec_biotech_partial": 0, "none": 0},
        "added_via_expansion": 0,
    }
    seen_pairs: set[tuple[str, str]] = set()
    for r in read_manifest(MANIFEST_SPONSOR_MAP):
        nct = r.get("nct_id")
        if nct:
            seen_pairs.add((nct, r.get("source", "")))

    for r in read_manifest(MANIFEST_AMENDMENT_FETCH):
        sponsor = r.get("sponsor_name")
        nct = r.get("nct_id")
        if not nct or not sponsor:
            continue
        stats["total"] += 1
        old = r.get("ticker")
        if old:
            stats["old_mapped"] += 1

        new, source = lookup_ticker_expanded(sponsor)
        if new:
            stats["new_mapped"] += 1
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            if not old:
                stats["added_via_expansion"] += 1

            if (nct, source) not in seen_pairs:
                append_manifest(MANIFEST_SPONSOR_MAP, {
                    "nct_id": nct,
                    "sponsor_name": sponsor,
                    "old_ticker": old,
                    "new_ticker": new,
                    "source": source,
                })
        else:
            stats["by_source"]["none"] = stats["by_source"].get("none", 0) + 1

    stats["new_mapping_rate"] = round(stats["new_mapped"] / max(stats["total"], 1), 4)
    stats["new_above_floor_1500"] = stats["new_mapped"] >= 1500
    return stats


if __name__ == "__main__":
    print(f"Seed index size: {len(_seed_index())}")
    print(f"SEC biotech index size: {len(_load_sec_biotech_index())}")
    print(f"Parent rollup size: {len(PARENT_ROLLUP)}")
    print()
    stats = update_manifest_with_expanded_tickers()
    print(json.dumps(stats, indent=2))
