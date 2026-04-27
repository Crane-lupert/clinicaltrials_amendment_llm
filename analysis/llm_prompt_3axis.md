# LLM Prompt — 3-Axis Pivotal-Shift Classification

**Use**: 3-vendor ensemble (Opus 4.7 / Sonnet 4.7 / Llama-3.3-70B-Instruct OR Gemma-2-27B) per amendment. Day 6 Fleiss κ measurement (trigger #3). Day 8-12 full sample inference.

---

## System Prompt

```
You are a clinical-trial protocol-amendment analyst. Your task is to classify each amendment along three axes per the F6 schema. You rely on the protocol text + amendment narrative (when present). You answer in strict JSON; no prose outside the JSON object. If the text is insufficient for an axis, you mark that axis "unknown" — never guess.
```

## User Prompt Template

```
[NCT_ID]: {nct_id}
[SPONSOR]: {sponsor_name}  (class: {sponsor_class})
[PHASE]: {phase}
[FIRST_SUBMITTED]: {study_first_submit_date}
[LAST_UPDATE_POST]: {last_update_post_date}

[AMENDMENT_CONTEXT]:
{study_record_json_excerpt}  // protocolSection.descriptionModule + designModule + eligibilityModule diff

[PROTOCOL_TEXT]:  // first 4000 chars of pdfplumber-extracted protocol body, then truncated
{protocol_text_excerpt}

Classify the most recent amendment on three axes per the F6 schema:

Axis 1 — pivotal_shift ∈ { "positive", "neutral", "negative", "unknown" }
  * positive: expands trial reach toward registration (dose↑, arm added, enrollment↑, endpoint upgrade, geography expansion).
  * neutral: design-correction / clarification / housekeeping with no directional regulatory impact.
  * negative: shrinks reach OR signals weakness (endpoint changed post-hoc, sample size↓, population narrowed, arm dropped, hold, unblinding for safety).

Axis 2 — admin_vs_substantive ∈ { "admin", "substantive", "unknown" }
  * admin: typo / IRB list / contact-info / formatting only.
  * substantive: changes endpoint / sample size / dose / eligibility / randomization / duration / SAP.

Axis 3 — driver ∈ { "dsmb", "regulator", "sponsor", "unknown" }
  * dsmb: DSMB / DMC / IDMC triggered.
  * regulator: FDA / EMA / regulatory authority required.
  * sponsor: sponsor-initiated, no DSMB / regulator cue.

Decision rules when ambiguous:
- Lean axis_1 to "neutral" if mechanically design-corrective without directional bias.
- Lean axis_1 to "negative" if change reduces statistical power for the original primary endpoint, even when framed as "interim safety review".
- Vaccine cohort caveat: 2020-2022 COVID/RSV/influenza vaccine trial amendments often "positive substantive sponsor" (scope expansion as EUA path opens). Score per the actual change, but flag is_vaccine_cohort=true if applicable.

Return ONLY this JSON:
{
  "nct_id": "<copy from input>",
  "pivotal_shift": "positive|neutral|negative|unknown",
  "admin_vs_substantive": "admin|substantive|unknown",
  "driver": "dsmb|regulator|sponsor|unknown",
  "is_vaccine_cohort": true|false,
  "rationale_short": "<= 200 chars, 1-2 sentences explaining the most diagnostic signal you used",
  "confidence": 0.0-1.0
}
```

---

## Determinism / temperature

- temperature = 0.0
- max_tokens = 400
- top_p = 1.0

---

## Cost estimate (Phase 1 budget)

| Model | Input tokens (avg) | Output tokens | $ per call (approx) | n=30000 calls |
|---|---:|---:|---:|---:|
| anthropic/claude-opus-4.7 | 4,500 | 200 | $0.045 | $1,350 — over cap |
| anthropic/claude-sonnet-4.7 | 4,500 | 200 | $0.013 | $390 |
| meta-llama/llama-3.3-70b-instruct | 4,500 | 200 | $0.001 | $30 |
| google/gemma-2-27b-it | 4,500 | 200 | $0.0008 | $24 |

**3-vendor ensemble on full Phase 1 sample (~30K events × 3 = 90K calls):**
- Opus 4.7 + Sonnet 4.7 + Llama-3.3-70B = $1,350 + $390 + $30 ≈ **$1,770 — way over $22 cap**
- **Replacement**: Sonnet 4.7 + Llama-3.3-70B + Gemma-2-27B = $390 + $30 + $24 = **$444 — still over $22**
- **Realistic mix at $22 cap**: must subsample. **Strategic sample n ≈ 1,500** with full 3-vendor = 1,500 × 3 = 4,500 calls × $0.0145 avg ≈ **$22**. ✅
- Phase 0 oracle pilot (n=20 × 3 = 60 calls × $0.015 ≈ $1) — negligible.

→ **Day 8-12 full sample dispatch is necessarily strategic-sample, not census.** Strategic sample n ≈ 1,500 stratified by (phase, sponsor_size_quintile, year, vaccine_cohort_y/n) — matches Phase 1 trigger #7 sample-power floor.

---

## References

- F6 schema: `analysis/three_axis_schema.md`
- F6 Phase 0 plan §1, §6 (Day 4-6 oracle pilot)
- F6 reference-validation §4.5.2 (label rater methodology contract)
- F1 prompt template (lift-and-shift): `D:/vscode/fda_adcomm_briefing_llm/src/fda_adcomm_briefing_llm/oracle_pilot.py` (3-vendor + Fleiss κ + 2-axis fallback)
