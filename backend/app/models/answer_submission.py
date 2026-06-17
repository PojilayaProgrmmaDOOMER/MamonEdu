from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer
)

from app.database import Base


class AnswerSubmission(Base):
    __tablename__ = "answer_submissions"

    id = Column(Integer, primary_key=True, index=True)

    attempt_id = Column(
        Integer,
        ForeignKey("test_attempts.id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False
    )

    selected_option_id = Column(
        Integer,
        ForeignKey("answer_options.id"),
        nullable=False
    )

    is_correct = Column(Boolean, nullable=False)