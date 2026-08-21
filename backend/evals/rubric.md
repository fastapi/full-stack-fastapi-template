# Prompt evaluation rubric

Score each **five-question set as a whole** (not each question). Scale **1–5**.

| Score | Appropriate difficulty | Clear wording | Good distractors | Grounded in lecture |
|-------|------------------------|---------------|------------------|---------------------|
| 5 | Clearly matches target difficulty | Exam-ready, unambiguous | Plausible student mistakes | Fully supported by text |
| 3 | Mixed; some too easy/hard | Usable but awkward | Some weak/joke options | Mostly supported; mild stretch |
| 1 | Ignores difficulty | Confusing / unusable | Random or unrelated options | Needs outside knowledge |

**Overall (1–5):** holistic quality of the set for a practice midterm.

## How to use

1. Run `python scripts/evaluate.py` from `backend/`.
2. Open `results/<run_id>/prompt_{a,b,c}.json` and inspect questions.
3. Fill the manual table in `results/<run_id>/report.md`.
4. Write one takeaway sentence (what you’d ship and why).

## What auto metrics mean

- **Reliability:** success rate, schema validity — did generation work?
- **Correctness gates:** answer-in-options, MC/TF counts — contract compliance
- **Efficiency:** latency / tokens — cost tradeoffs, not quality

## Manual scores — full corpus `2026-08-21T01-52-36Z` (13 docs)

**Sampling method:** Spot-checked **4 docs** that succeeded for all three prompts where possible (`smoke_lists`, `smoke_oop`, `smoke_functions`, `smoke_debugging`) — 5 questions each ≈ **20 questions per prompt**, not every generated item. Compared each sample set to the matching `evals/corpus/*.txt` for grounding. Auto gates from the same run (validator already merged): success **A 10/13 (77%) · B 10/13 (77%) · C 11/13 (85%)**; **answer∈options = 100% on every successful doc** (failed docs are `error_kind=validation`, nothing bad persisted). Mean answer-in-options in `report.md` (~77/77/85) averages failures as 0.

| Criterion | A (baseline) | B (difficulty) | C (distractors) |
|-----------|--------------|----------------|-----------------|
| Appropriate difficulty | 3 | 4 | 3 |
| Clear wording | 4 | 4 | 4 |
| Good distractors | 3 | 3 | 4 |
| Grounded in lecture | 5 | 5 | 4 |
| **Overall** | **4** | **3** | **3** |

Notes (from the sample only):
- **A:** Contract-clean on successes; questions track the lecture closely and are exam-usable. Difficulty skews recall/definition; some MC distractors are soft (`function`/`define`, near-tautological T/F).
- **B:** Slightly sharper items (e.g. arguments vs parameters, composition vs inheritance) without the pre-fix ungradable T/F answers. Still not a clear quality win over A at equal reliability.
- **C:** Often stronger MC distractors (more options, more “wrong but tempting”). Occasional awkward items in the sample (e.g. treating `sort` as “not a common list operation” because the lecture only named append/insert/pop) — answerable from the text, but a mild grounding/pedagogy stretch. Highest success rate, not highest overall quality.

### Takeaway (ship / no-ship)

**Ship prompt A.** Full-corpus gates + sampled rubric favor keeping the production baseline: reliable enough, fully contract-compliant when it succeeds, and the most consistently grounded/clear in the spot-check. Hold B/C — B isn’t a clear upgrade; C’s distractor gains don’t outweigh uneven item quality.

## Manual scores — smoke run `2026-07-31T00-10-58Z` (1 doc: `smoke_recursion`)

Scored from saved artifacts (pre-validator). Auto gates from that run: A 100% / B 60% / C 80% answer-in-options.

| Criterion | A (baseline) | B (difficulty) | C (distractors) |
|-----------|--------------|----------------|-----------------|
| Appropriate difficulty | 3 | 4 | 3 |
| Clear wording | 4 | 2 | 4 |
| Good distractors | 3 | 3 | 4 |
| Grounded in lecture | 5 | 4 | 5 |
| **Overall** | **4** | **2** | **3** |

Notes:
- **A:** Contract-clean; questions are grounded and usable. Some MC options are soft/near-tautological.
- **B:** Intended harder items, but two T/F rows used sentence answers (`"A base case"`, long memory phrase) instead of `True`/`False` → ungradable. Overall capped by correctness failure.
- **C:** Stronger distractors on MC; one MC failed exact answer∈options because the answer string had a trailing period the option lacked.

### Takeaway (historical)

**Ship prompt A** (unchanged). Smoke alone already ruled out shipping B/C until the answer∈options validator landed; full-corpus re-eval above confirms keep A.
