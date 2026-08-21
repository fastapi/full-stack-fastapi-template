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

## Manual scores — smoke run `2026-07-31T00-10-58Z` (1 doc: `smoke_recursion`)

Scored from saved artifacts (not a live re-run). Auto gates from that run: A 100% / B 60% / C 80% answer-in-options.

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

### Takeaway (ship / no-ship)

**Ship prompt A.** It alone passed correctness gates and produced exam-usable grounded questions. Hold B/C until the answer∈options validator is merged and a re-smoke shows 100% contract compliance (or clean validation failures with nothing persisted).
