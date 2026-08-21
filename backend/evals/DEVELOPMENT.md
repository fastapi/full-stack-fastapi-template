# Eval harness — development log

Working notes for MidtermMock prompt evaluation. Not a substitute for the README methodology section.

## Timeline

### 2026-07-30 — Harness scaffold
- Shared prompt registry: A (baseline), B (difficulty), C (distractors)
- Shared `generate_questions` used by API + eval
- `scripts/evaluate.py` → timestamped `config.json`, `prompt_*.json`, `report.md`
- Metric split: reliability / correctness gates / efficiency tradeoffs / manual rubric
- Smoke corpus + `evals/rubric.md`

### 2026-07-30 — Smoke run (`2026-07-31T00-10-58Z`)
- 1 doc (`smoke_recursion`) × prompts A/B/C against live `gpt-4o-mini`
- A: answer-in-options 100%
- B: answer-in-options **60%**, `final_contract_valid=false`
- C: answer-in-options 80%

### 2026-08-10 — Manual review of prompt B artifact
**Caught a pre-existing production bug** while reviewing `results/2026-07-31T00-10-58Z/prompt_b.json`.

#### Bug: T/F (and MC) answers not required to be in `options`
- **Symptom:** Model returned `type: true_false`, `options: ["True","False"]`, but `answer` was a phrase (e.g. `"A base case"`) or a full sentence—not `True`/`False`.
- **Impact:** Questions can be stored/served; scoring compares student choice to an impossible `correct_answer` → broken T/F grading.
- **Root cause:** `QuestionItem` only validates type ↔ options shape. It does **not** enforce `answer ∈ options`. Prompt rules were soft; code never hard-failed.
- **Not a regression from the eval PR** — pre-existing gap; the harness’s `answer_in_options_rate` gate surfaced it.
- **Status:** Fixed in `fix/question-answer-in-options` (PR #61) — `QuestionItem` + convert path reject answer ∉ options; generation returns `error_kind=validation`.

### 2026-08-20 — Validator fix + evidence pack
- Unit tests cover valid MC/T/F, invalid T/F sentence-as-answer, invalid MC, missing answer, and generation → `error_kind=validation`.
- Corpus expanded to **13** short lecture-like `.txt` docs under `evals/corpus/`.
- Manual rubric for the pre-fix smoke filled in `evals/rubric.md` (historical section).

### 2026-08-21 — Full-corpus re-eval (`2026-08-21T01-52-36Z`)
Post-validator live run: 13 docs × A/B/C, `gpt-4o-mini`, difficulty `medium`, 5 questions/doc, `max_completion_tokens=500`.

| Prompt | Success | Answer∈options on successes | Notes |
|--------|---------|------------------------------|-------|
| A baseline | 10/13 (**77%**) | **100%** | 3 validation failures |
| B difficulty | 10/13 (**77%**) | **100%** | 3 validation failures |
| C distractors | 11/13 (**85%**) | **100%** | 2 validation failures |

Mean answer-in-options in `report.md` (~77/77/85) counts failed docs as 0; every `ok` doc had `answer_in_options_rate=1.0`. Failures are `error_kind=validation` (bad answers not persisted). Manual spot-check (4 docs / ~20 questions per prompt): see `evals/rubric.md` — **ship A**.

## Open follow-ups
- [x] Enforce `answer ∈ options` in structured-output validation
- [x] Re-run after fix with a real OpenAI key; confirm answer-in-options = 100% on successful A/B/C runs (failures are validation, not persisted bad answers)
- [x] Fill manual rubric; write ship/no-ship takeaway
- [x] Land harness (PR #60); validator as fast follow (PR #61)
- [ ] Optional: raise reliability (fewer validation rejects) without changing the shipped A prompt semantics

## Ship / no-ship takeaway

**Ship prompt A (baseline) in production.** Full-corpus gates show contract compliance on all successes; sampled rubric quality is highest/most consistent for A. Do **not** switch to B or C — B isn’t a clear quality upgrade at the same success rate; C’s slightly higher success and stronger distractors don’t outweigh uneven item quality in the spot-check.

## How to reproduce the finding
```bash
cd backend
python scripts/evaluate.py --prompts a,b,c
# open results/<run_id>/report.md and prompt_{a,b,c}.json
# pre-fix bug (historical): look in older smoke artifacts for true_false rows where answer is not True/False
```
