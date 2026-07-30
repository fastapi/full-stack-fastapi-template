from typing import Literal

from app.models import Difficulty, QuestionType

PromptId = Literal["a", "b", "c"]
PROMPT_IDS: tuple[PromptId, ...] = ("a", "b", "c")
PROMPT_NAMES: dict[PromptId, str] = {
    "a": "baseline",
    "b": "difficulty",
    "c": "distractors",
}


def _format_allowed_types(
    question_type_counts: dict[QuestionType, int],
) -> str:
    """Same production wording: any mix of the listed types is allowed."""
    types_str = ", ".join(question_type.value for question_type in question_type_counts)
    return f"Allowed question types: {types_str}"


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
    """Production difficulty wording (prompt A)."""
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


def _difficulty_calibration(difficulty: Difficulty) -> str:
    """Prompt B only: stronger difficulty calibration (not distractor quality)."""
    return f"""Difficulty calibration (must be observable in the question stem and required reasoning, not wording alone):
- Target difficulty: {difficulty.value}
- EASY: answer is a single explicit fact from the text; minimal inference; one concept only
- MEDIUM: answer requires connecting 2 ideas from the text; light inference or comparison
- HARD: answer requires synthesizing 2+ non-adjacent parts of the text OR applying a stated rule to a new example still grounded in the text
- Do NOT label a question as harder merely by using denser vocabulary or longer sentences
- Match the cognitive demand to the target difficulty for every question"""


def _distractor_quality_rules() -> str:
    """Prompt C only: stronger distractor quality on top of baseline A."""
    return """Distractor quality rules (apply in addition to the difficulty rules above):
- For multiple_choice: every wrong option must be a realistic mistake a student might make given this material
- Distractors should be conceptually adjacent to the correct answer (common confusions), not random or unrelated
- Avoid joke options, absolute statements with no basis in the text, or options from outside the topic
- The correct answer must still match exactly one option
- True/false questions are unchanged: options must remain exactly ["True", "False"]"""


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
) -> str:
    """Assemble a full prompt from shared sections plus variant-specific parts."""
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
            _format_allowed_types(question_type_counts),
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
    """Return the prompt string for variant a, b, or c.

    A — production baseline wording (any mix of allowed types).
    B — same as A, but with stronger difficulty calibration.
    C — same as A, plus stronger distractor-quality instructions.
    """
    if prompt_id == "a":
        return _build_prompt(
            text=text,
            num_questions=num_questions,
            difficulty=difficulty,
            question_type_counts=question_type_counts,
            difficulty_section=_baseline_difficulty_rules(),
        )
    if prompt_id == "b":
        return _build_prompt(
            text=text,
            num_questions=num_questions,
            difficulty=difficulty,
            question_type_counts=question_type_counts,
            difficulty_section=_difficulty_calibration(difficulty),
        )
    if prompt_id == "c":
        return _build_prompt(
            text=text,
            num_questions=num_questions,
            difficulty=difficulty,
            question_type_counts=question_type_counts,
            difficulty_section=_baseline_difficulty_rules(),
            extra_sections=(_distractor_quality_rules(),),
        )
    raise ValueError(f"Unknown prompt_id: {prompt_id!r}")
