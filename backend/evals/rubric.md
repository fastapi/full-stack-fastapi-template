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
