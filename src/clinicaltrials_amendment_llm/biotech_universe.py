"""Biotech R1000 sponsoring firm universe filter.

Day 2 task. Two filters in series:
1. Russell 1000 / Russell 3000 biotech subset (static list, 2024 snapshot).
2. CT.gov sponsor.class == "INDUSTRY" (industry-sponsored only - excludes
   academic / consortium / NIH / OTHER_GOV).

The static R1000 biotech list is a placeholder for Day 2 dry-run. Day 11
sponsor->ticker mapping (manifest_sponsor_map.jsonl) replaces it with a
proper join via filer_ontology + parent rollup.

Universe seed: 2024 XBI ETF holdings + IBB top constituents + selected
mid-cap biotechs (industry-sponsoring biotechs known to file CT.gov
amendments at meaningful frequency). Not exhaustive - Day 11 expands.
"""

from __future__ import annotations

# 2024 biotech R1000 sponsoring firm seed (ticker -> canonical sponsor name).
# Sponsor-name strings are how they appear in CT.gov LeadSponsor.name (or
# parent-rollup target). Lower-cased canonical for matching.
BIOTECH_R1000_SEED: dict[str, list[str]] = {
    # Large-cap biotech / pharma R&D-heavy
    "PFE": ["Pfizer", "Pfizer Inc"],
    "MRK": ["Merck Sharp & Dohme LLC", "Merck Sharp & Dohme Corp.", "Merck"],
    "JNJ": ["Janssen Research & Development, LLC", "Janssen Pharmaceuticals", "Janssen"],
    "BMY": ["Bristol-Myers Squibb", "Bristol Myers Squibb"],
    "LLY": ["Eli Lilly and Company", "Eli Lilly"],
    "GILD": ["Gilead Sciences"],
    "AMGN": ["Amgen"],
    "REGN": ["Regeneron Pharmaceuticals"],
    "VRTX": ["Vertex Pharmaceuticals Incorporated", "Vertex Pharmaceuticals"],
    "BIIB": ["Biogen", "Biogen Idec"],
    "MRNA": ["ModernaTX, Inc.", "Moderna"],
    "BNTX": ["BioNTech SE"],
    "NVAX": ["Novavax"],
    "ABBV": ["AbbVie"],
    "AZN": ["AstraZeneca"],
    "GSK": ["GlaxoSmithKline", "GSK"],
    "SNY": ["Sanofi", "Sanofi-Aventis"],
    "NVS": ["Novartis Pharmaceuticals", "Novartis"],
    "ROG.SW": ["Hoffmann-La Roche", "F. Hoffmann-La Roche", "Genentech, Inc.", "Genentech"],
    # Mid-cap biotech (R&D-active, frequent amendment activity)
    "SRPT": ["Sarepta Therapeutics"],
    "BMRN": ["BioMarin Pharmaceutical"],
    "INCY": ["Incyte Corporation", "Incyte"],
    "ALNY": ["Alnylam Pharmaceuticals"],
    "ILMN": ["Illumina"],
    "CRSP": ["CRISPR Therapeutics"],
    "BLUE": ["bluebird bio"],
    "EXAS": ["Exact Sciences Corporation"],
    "TECH": ["Bio-Techne"],
    "RARE": ["Ultragenyx Pharmaceutical"],
    "IONS": ["Ionis Pharmaceuticals"],
    "BEAM": ["Beam Therapeutics"],
    "EDIT": ["Editas Medicine"],
    "NTLA": ["Intellia Therapeutics"],
    "ARCT": ["Arcturus Therapeutics"],
    "VKTX": ["Viking Therapeutics"],
    "MDGL": ["Madrigal Pharmaceuticals"],
    "NBIX": ["Neurocrine Biosciences"],
    "SGEN": ["Seagen"],
    "ACAD": ["ACADIA Pharmaceuticals"],
    "DNLI": ["Denali Therapeutics"],
    "FATE": ["Fate Therapeutics"],
    "IOVA": ["Iovance Biotherapeutics"],
    "NKTR": ["Nektar Therapeutics"],
    "PTCT": ["PTC Therapeutics"],
    "SAGE": ["Sage Therapeutics"],
    "TBPH": ["Theravance Biopharma"],
    "VIR": ["Vir Biotechnology"],
    "XENE": ["Xenon Pharmaceuticals"],
    "ZNTL": ["Zentalis Pharmaceuticals"],
    "ARWR": ["Arrowhead Pharmaceuticals"],
    "SWTX": ["SpringWorks Therapeutics"],
    "RLAY": ["Relay Therapeutics"],
    "CGEM": ["Cullinan Oncology"],
    "OCUL": ["Ocular Therapeutix"],
    "VERV": ["Verve Therapeutics"],
    "PRTA": ["Prothena Corporation"],
    "AGEN": ["Agenus"],
    "RGNX": ["REGENXBIO"],
    "RVMD": ["Revolution Medicines"],
    "PRTC": ["PureTech Health"],
    "BHVN": ["Biohaven Pharmaceutical"],
    "AKRO": ["Akero Therapeutics"],
    "MYGN": ["Myriad Genetics"],
    "INSM": ["Insmed Incorporated"],
    "JAZZ": ["Jazz Pharmaceuticals"],
    "ALKS": ["Alkermes"],
    "EXEL": ["Exelixis"],
    "LGND": ["Ligand Pharmaceuticals"],
    "UTHR": ["United Therapeutics"],
    "HALO": ["Halozyme Therapeutics"],
    "ARGX": ["argenx"],
    "GMAB": ["Genmab"],
    "LEGN": ["Legend Biotech"],
    "DVAX": ["Dynavax Technologies"],
    "TGTX": ["TG Therapeutics"],
    "VYGR": ["Voyager Therapeutics"],
    "RYTM": ["Rhythm Pharmaceuticals"],
}


def normalize_sponsor_name(name: str) -> str:
    """Canonical match key: lowercase + trim suffixes."""
    if not name:
        return ""
    n = name.lower().strip()
    for suf in [", inc.", ", inc", " inc.", " inc", ", llc", " llc",
                ", ltd.", " ltd.", " ltd", " corp.", " corp", ", corp.",
                ", corporation", " corporation", " co.", " co", " gmbh",
                " ag", " sa", " plc", " s.a.", " s.p.a.", " spa",
                " incorporated", " ltd."]:
        if n.endswith(suf):
            n = n[: -len(suf)]
    return n.strip()


def lookup_ticker(sponsor_name: str) -> str | None:
    """Returns ticker (or None) for a sponsor name from the seed list.

    Day 2 placeholder. Day 11 replaces with filer_ontology fuzzy match +
    parent rollup chain.
    """
    norm = normalize_sponsor_name(sponsor_name)
    for ticker, names in BIOTECH_R1000_SEED.items():
        for n in names:
            if normalize_sponsor_name(n) == norm:
                return ticker
            # also accept startswith match (handles "Pfizer" prefix variants)
            if norm and normalize_sponsor_name(n).startswith(norm):
                return ticker
    return None


def universe_size() -> int:
    return len(BIOTECH_R1000_SEED)


if __name__ == "__main__":
    print(f"BIOTECH_R1000_SEED: {universe_size()} firms")
    print(f"  PFE -> {lookup_ticker('Pfizer Inc')}")
    print(f"  BNTX -> {lookup_ticker('BioNTech SE')}")
    print(f"  unknown -> {lookup_ticker('Random Academic Center')}")
