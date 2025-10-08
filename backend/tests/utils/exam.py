import uuid
from typing import Any

from sqlmodel import Session

from app import crud
from app.models import (
    Answer,
    Exam,
    ExamAttempt,
    ExamCreate,
    ExamPublic,
    Question,
    QuestionCreate,
    User,
)
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_exam(
    db: Session, user: User | None = None, with_questions: bool = True
) -> ExamPublic:
    user = user or create_random_user(db)
    owner_id = user.id
    assert owner_id is not None

    title = random_lower_string()
    exam_in = ExamCreate(
        title=title,
        description=f"Randomly generated exam for {title}",
        duration_minutes=30,
        is_published=False,
    )

    db_exam = crud.create_db_exam(session=db, exam_in=exam_in, owner_id=owner_id)

    questions: list[QuestionCreate] = []
    if with_questions:
        for i in range(3):
            questions.append(
                QuestionCreate(
                    question=f"What is the answer to question {i+1} of {title}?",
                    answer=f"Answer {i+1}",
                    type="multiple_choice",
                    exam_id=db_exam.id,
                )
            )

    return crud.create_exam(session=db, db_exam=db_exam, questions=questions)


def create_random_exams(db: Session, user: User | None = None) -> list[ExamPublic]:
    user = user or create_random_user(db)
    return [create_random_exam(db, user) for _ in range(3)]


def create_exam_with_attempt(
    db: Session,
    question_text: str = "What is 2+2?",
    correct_answer: str = "4",
    question_type: str = "short_answer",
) -> Any:
    """
    Helper to create an exam, a question, and an attempt.
    Returns (exam, question, attempt).
    """
    exam = create_random_exam(db)

    question = Question(
        question=question_text,
        answer=correct_answer,
        type=question_type,
        exam_id=exam.id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    exam_attempt = ExamAttempt(exam_id=exam.id, owner_id=exam.owner_id)
    db.add(exam_attempt)
    db.commit()
    db.refresh(exam_attempt)

    return [exam, question, exam_attempt]


def create_exam_with_attempt_and_answer(db: Session, owner_id: uuid.UUID) -> Any:
    """
    Helper to create:
    - an exam owned by `owner_id`
    - a question for that exam
    - an exam attempt for that exam & owner
    - an initial answer for that attempt
    Returns: (exam, question, exam_attempt, answer)
    """
    # Create exam
    exam = Exam(title="Sample Exam", owner_id=owner_id)
    db.add(exam)
    db.commit()
    db.refresh(exam)

    # Create question
    question = Question(
        question="What is 2+2?",
        answer="4",
        type="short_answer",
        exam_id=exam.id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Create exam attempt
    exam_attempt = ExamAttempt(exam_id=exam.id, owner_id=owner_id)
    db.add(exam_attempt)
    db.commit()
    db.refresh(exam_attempt)

    # Add initial answer (wrong for testing)
    answer = Answer(response="3", attempt_id=exam_attempt.id, question_id=question.id)
    db.add(answer)
    db.commit()
    db.refresh(answer)

    return exam, question, exam_attempt, answer
