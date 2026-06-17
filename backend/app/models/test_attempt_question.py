from sqlalchemy import Column, ForeignKey, Integer

from app.database import Base


class TestAttemptQuestion(Base):
    __tablename__ = "test_attempt_questions"

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