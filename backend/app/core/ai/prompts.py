from typing import Literal

from app.models import Difficulty, QuestionType

PromptId = Literal["a", "b", "c"]
PROMPT_IDS: tuple[PromptId, ...] = ("a", "b", "c")
PROMPT_NAMES: dict[PromptId, str] = {
    "a": "baseline",
    "b": "grounded",
    "c": "difficulty",
}


def _format_allowed_types(
    question_type_counts: dict[QuestionType, int],
) -> str:
    types_str = ", ".join(question_type.value for question_type in question_type_counts)
    return f"Allowed question types: {types_str}"


def _format_question_mix(
    question_type_counts: dict[QuestionType, int],
    num_questions: int,
) -> str:
    lines = ["Required question mix (must follow exactly):"]
    for question_type, count in question_type_counts.items():
        lines.append(f"- {question_type.value}: {count}")
    lines.append(f"Total questions: {num_questions}")
    return "\n".join(lines)


def _question_structure_rules() -> str:
    return """Rules (must follow exactly):
- Each question MUST include:
  - question (string)
  - answer (string or null)
  - type: "multiple_choice" or "true_false"
  - options (array of strings)

- For true_false questions:
  - type MUST be "true_false"
  - options MUST be exactly ["True", "False"]
  - Do NOT use true_false type with multiple choice options

- For multiple_choice questions:
  - type MUST be "multiple_choice"
  - options MUST contain at least 3 plausible choices (not just True/False)
  - answer MUST match exactly one option
  - Do NOT use multiple_choice type with only True/False options"""


def _baseline_difficulty_rules() -> str:
    return """Difficulty rules:
- EASY:
  - Focus on direct facts explicitly stated in the text
  - Minimal inference
  - Single concept per question
  - Obvious distractors

- MEDIUM:
  - Require understanding relationships between concepts
  - Light inference or comparison
  - Distractors should be plausible but incorrect

- HARD:
  - Require multi-step reasoning or synthesis across multiple parts of the text
  - Subtle distinctions between options
  - Distractors should be conceptually close to the correct answer"""


def _grounding_rules() -> str:
    return """Grounding rules (strict — override other instincts):
- Every question MUST be answerable using ONLY sentences that appear in the document text
- Before writing each question, identify the supporting span(s) in the text; if you cannot, discard that question and write a different one
- Prefer wording that closely mirrors the document's terms; do not paraphrase into new technical claims
- Distractors MUST also be drawn from concepts present in the text (misapplied), never invented jargon
- If the text is thin, ask simpler, explicitly supported facts rather than inventing content — still return exactly the required mix"""


def _difficulty_contract(difficulty: Difficulty) -> str:
    return f"""Difficulty contract (must be observable in the question, not just the label):
- Target difficulty: {difficulty.value}
- EASY: answer is a single explicit fact; distractors are clearly wrong to someone who skimmed the text
- MEDIUM: answer requires connecting 2 ideas from the text; at least 2 distractors are plausible to a partial reader
- HARD: answer requires synthesizing 2+ non-adjacent parts of the text OR applying a stated rule to a new example still grounded in the text; all distractors must be conceptually adjacent (common confusions)

Distractor rules:
- For multiple_choice: every wrong option must be a realistic mistake a student might make given this material
- Avoid joke options, absolutes with no basis, or options unrelated to the topic
- The correct answer must still match exactly one option"""


def _additional_constraints() -> str:
    return """Additional constraints:
- Do NOT introduce facts not present in the document
- Do NOT rely on outside knowledge
- Difficulty MUST affect question complexity, not wording alone"""


def _critical_footer() -> str:
    return """CRITICAL: The question type MUST match the options:
- If type is "true_false", options MUST be exactly ["True", "False"]
- If type is "multiple_choice", options MUST have at least 3 different choices (NOT True/False)
- Do NOT mix types: a true_false question cannot have multiple choice options, and vice versa"""


def _build_prompt(
    *,
    text: str,
    num_questions: int,
    difficulty: Difficulty,
    question_type_counts: dict[QuestionType, int],
    difficulty_section: str,
    extra_sections: tuple[str, ...] = (),
    strict_type_mix: bool = False,
) -> str:
    assert sum(question_type_counts.values()) == num_questions

    type_section = (
        _format_question_mix(question_type_counts, num_questions)
        if strict_type_mix
        else _format_allowed_types(question_type_counts)
    )

    sections = [
        f"Generate {num_questions} questions from the following document text.",
        "",
        _question_structure_rules(),
        "",
        difficulty_section,
    ]
    for extra in extra_sections:
        sections.extend(["", extra])
    sections.extend(
        [
            "",
            _additional_constraints(),
            "",
            "Return structured data only.",
            "",
            "Document text:",
            text,
            "",
            f"Difficulty: {difficulty.value}",
            type_section,
            "",
            _critical_footer(),
        ]
    )
    return "\n".join(sections) + "\n"


def get_prompt(
    prompt_id: PromptId,
    text: str,
    *,
    num_questions: int,
    difficulty: Difficulty,
    question_type_counts: dict[QuestionType, int],
) -> str:
    if prompt_id == "a":
        # Production baseline: allow any mix of the listed types (no fixed counts).
        return _build_prompt(
            text=text,
            num_questions=num_questions,
            difficulty=difficulty,
            question_type_counts=question_type_counts,
            difficulty_section=_baseline_difficulty_rules(),
            strict_type_mix=False,
        )
    if prompt_id == "b":
        return _build_prompt(
            text=text,
            num_questions=num_questions,
            difficulty=difficulty,
            question_type_counts=question_type_counts,
            difficulty_section=_baseline_difficulty_rules(),
            extra_sections=(_grounding_rules(),),
            strict_type_mix=True,
        )
    if prompt_id == "c":
        return _build_prompt(
            text=text,
            num_questions=num_questions,
            difficulty=difficulty,
            question_type_counts=question_type_counts,
            difficulty_section=_difficulty_contract(difficulty),
            strict_type_mix=True,
        )
    raise ValueError(f"Unknown prompt_id: {prompt_id!r}")
