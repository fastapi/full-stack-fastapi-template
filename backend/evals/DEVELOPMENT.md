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
- Corpus expanded to **12** short lecture-like `.txt` docs under `evals/corpus/`.
- Live re-smoke **skipped** locally: `OPENAI_API_KEY` in `.env` is the placeholder `changethis` (not a real key). Re-run when a real key is available:
  ```bash
  cd backend
  python scripts/evaluate.py --prompts a,b,c --limit 1   # smoke
  python scripts/evaluate.py --prompts a,b,c             # full corpus
  ```
- Manual rubric filled from the `2026-07-31T00-10-58Z` artifacts (see `evals/rubric.md`).

## Open follow-ups
- [x] Enforce `answer ∈ options` in structured-output validation
- [ ] Re-run smoke after fix with a real OpenAI key; confirm answer-in-options = 100% on successful A/B/C runs (failures should be validation, not persisted bad answers)
- [x] Fill manual rubric; write ship/no-ship takeaway
- [x] Land harness (PR #60); validator as fast follow (PR #61)

## Ship / no-ship takeaway

**Ship prompt A (baseline) in production.** It was the only variant with 100% answer-in-options and `final_contract_valid` on the smoke set, with clear grounded wording. Do **not** ship B or C until a post-validator re-smoke shows contract compliance; B produced ungradable T/F answers, and C failed exact answer∈options on a trailing-period mismatch.

## How to reproduce the finding
```bash
cd backend
# inspect existing artifact, or:
python scripts/evaluate.py --prompts b --limit 1
# open results/<run_id>/prompt_b.json — look for true_false rows where answer is not True/False
```
