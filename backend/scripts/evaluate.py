#!/usr/bin/env python3
"""Minimal prompt-variant eval runner.

Reads local .txt corpus files, calls shared generate_questions for each
document × prompt ID, and writes JSON artifacts to a timestamped run directory.

Example (from backend/):

    python scripts/evaluate.py --prompts a,b,c --limit 1
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow `python scripts/evaluate.py` from backend/
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.ai.openai import (  # noqa: E402
    DEFAULT_MAX_COMPLETION_TOKENS,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_CHARS,
    GenerationResult,
    generate_questions,
    normalize_question_types,
)
from app.core.ai.prompts import (  # noqa: E402
    PROMPT_IDS,
    PROMPT_NAMES,
    PromptId,
)
from app.models import Difficulty  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_CORPUS = BACKEND_ROOT / "evals" / "corpus"
DEFAULT_OUT = BACKEND_ROOT / "results"
DEFAULT_NUM_QUESTIONS = 5
DEFAULT_DIFFICULTY = Difficulty.medium
# Same default type list generate_questions uses when question_types/counts are omitted.
DEFAULT_QUESTION_TYPES = [qt.value for qt in normalize_question_types(None)]


def _parse_prompts(raw: str) -> list[PromptId]:
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("At least one prompt ID is required")
    invalid = [p for p in parts if p not in PROMPT_IDS]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"Invalid prompt ID(s): {invalid}. Allowed: {list(PROMPT_IDS)}"
        )
    # Preserve order, drop duplicates
    seen: set[str] = set()
    prompts: list[PromptId] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            prompts.append(p)  # type: ignore[arg-type]
    return prompts


def _list_corpus_files(corpus_dir: Path, limit: int) -> list[Path]:
    if not corpus_dir.is_dir():
        raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")
    files = sorted(corpus_dir.glob("*.txt"))
    if not files:
        raise ValueError(f"No .txt corpus files found in {corpus_dir}")
    if limit > 0:
        files = files[:limit]
        if not files:
            raise ValueError(
                f"No .txt corpus files found in {corpus_dir} after --limit {limit}"
            )
    return files


def _serialize_result(
    doc_id: str,
    prompt_id: PromptId,
    result: GenerationResult,
) -> dict[str, Any]:
    return {
        "doc_id": doc_id,
        "prompt_id": prompt_id,
        "ok": result.ok,
        "error": result.error,
        "latency_ms": result.latency_ms,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "total_tokens": result.total_tokens,
        "schema_valid": result.schema_valid,
        "final_contract_valid": result.final_contract_valid,
        "content_checks": result.content_checks,
        "questions": [
            {
                "question": q.question,
                "answer": q.correct_answer,
                "type": q.type.value if hasattr(q.type, "value") else q.type,
                "options": q.options,
            }
            for q in result.questions
        ],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


async def _run(
    *,
    prompts: list[PromptId],
    corpus_dir: Path,
    out_dir: Path,
    limit: int,
) -> Path:
    files = _list_corpus_files(corpus_dir, limit)
    doc_ids = [f.stem for f in files]

    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    config = {
        "run_id": run_id,
        "prompts": prompts,
        "corpus_dir": str(corpus_dir),
        "doc_ids": doc_ids,
        "limit": limit,
        # Controls used by generate_questions (shared openai.py constants / defaults)
        "num_questions": DEFAULT_NUM_QUESTIONS,
        "difficulty": DEFAULT_DIFFICULTY.value,
        "question_types": DEFAULT_QUESTION_TYPES,
        "model": DEFAULT_MODEL,
        "temperature": DEFAULT_TEMPERATURE,
        "max_completion_tokens": DEFAULT_MAX_COMPLETION_TOKENS,
        "max_chars": MAX_CHARS,
    }
    _write_json(run_dir / "config.json", config)
    logger.info(
        "Wrote %s (%d docs, prompts=%s)", run_dir / "config.json", len(files), prompts
    )

    # prompt_id -> list of per-doc results
    by_prompt: dict[PromptId, list[dict[str, Any]]] = {p: [] for p in prompts}

    for path in files:
        doc_id = path.stem
        text = path.read_text(encoding="utf-8")
        for prompt_id in prompts:
            logger.info("Generating doc=%s prompt=%s", doc_id, prompt_id)
            result = await generate_questions(
                text,
                prompt_id=prompt_id,
                num_questions=DEFAULT_NUM_QUESTIONS,
                difficulty=DEFAULT_DIFFICULTY,
            )
            by_prompt[prompt_id].append(_serialize_result(doc_id, prompt_id, result))

    for prompt_id, results in by_prompt.items():
        n_ok = sum(1 for r in results if r["ok"])
        n_failed = len(results) - n_ok
        payload = {
            "prompt_id": prompt_id,
            "prompt_name": PROMPT_NAMES[prompt_id],
            "results": results,
            "summary": {
                "n_docs": len(results),
                "n_ok": n_ok,
                "n_failed": n_failed,
            },
        }
        out_path = run_dir / f"prompt_{prompt_id}.json"
        _write_json(out_path, payload)
        logger.info("Wrote %s (ok=%d failed=%d)", out_path, n_ok, n_failed)

    return run_dir


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Minimal prompt-variant evaluation runner"
    )
    parser.add_argument(
        "--prompts",
        type=_parse_prompts,
        default=_parse_prompts("a,b,c"),
        help="Comma-separated prompt IDs (default: a,b,c)",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
        help=f"Directory of .txt files (default: {DEFAULT_CORPUS})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max number of corpus files to use (0 = all)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Parent directory for run outputs (default: {DEFAULT_OUT})",
    )
    args = parser.parse_args(argv)

    corpus_dir = (
        args.corpus if args.corpus.is_absolute() else BACKEND_ROOT / args.corpus
    )
    out_dir = args.out if args.out.is_absolute() else BACKEND_ROOT / args.out

    try:
        run_dir = asyncio.run(
            _run(
                prompts=args.prompts,
                corpus_dir=corpus_dir.resolve(),
                out_dir=out_dir.resolve(),
                limit=args.limit,
            )
        )
    except (FileNotFoundError, ValueError) as e:
        logger.error("%s", e)
        return 1
    except Exception:
        logger.exception("Evaluation run failed")
        return 1

    logger.info("Done. Results in %s", run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
