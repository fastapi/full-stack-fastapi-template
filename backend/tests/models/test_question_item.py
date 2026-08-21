"""Unit tests for QuestionItem answer ∈ options validation."""

import pytest
from pydantic import ValidationError

from app.models import QuestionItem


def test_question_item_valid_multiple_choice() -> None:
    item = QuestionItem(
        question="What is 2+2?",
        answer="4",
        type="multiple_choice",
        options=["2", "3", "4", "5"],
    )
    assert item.type == "multiple_choice"
    assert item.answer == "4"
    assert item.options == ["2", "3", "4", "5"]


def test_question_item_valid_true_false() -> None:
    item = QuestionItem(
        question="Is the sky blue?",
        answer="True",
        type="true_false",
        options=["True", "False"],
    )
    assert item.type == "true_false"
    assert item.answer == "True"
    assert item.options == ["True", "False"]


def test_question_item_true_false_normalizes_answer_case() -> None:
    item = QuestionItem(
        question="Recursion needs a base case.",
        answer="true",
        type="true_false",
        options=["true", "false"],
    )
    assert item.answer == "True"
    assert item.options == ["True", "False"]


def test_question_item_rejects_true_false_answer_not_in_options() -> None:
    with pytest.raises(ValidationError) as exc_info:
        QuestionItem(
            question="Every recursive function needs a base case.",
            answer="A base case",
            type="true_false",
            options=["True", "False"],
        )
    assert "True/false answer must be one of" in str(exc_info.value)


def test_question_item_rejects_multiple_choice_answer_not_in_options() -> None:
    with pytest.raises(ValidationError) as exc_info:
        QuestionItem(
            question="What is 2+2?",
            answer="6",
            type="multiple_choice",
            options=["2", "3", "4", "5"],
        )
    assert "Answer must be one of the options" in str(exc_info.value)


def test_question_item_rejects_missing_answer() -> None:
    with pytest.raises(ValidationError) as exc_info:
        QuestionItem(
            question="What is 2+2?",
            answer=None,
            type="multiple_choice",
            options=["2", "3", "4", "5"],
        )
    assert "answer is required" in str(exc_info.value)
