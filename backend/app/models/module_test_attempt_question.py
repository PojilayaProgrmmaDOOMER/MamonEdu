from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class ModuleTestAttemptQuestion(Base):
    __tablename__ = "module_test_attempt_questions"

    id = Column(Integer, primary_key=True)

    attempt_id = Column(
        Integer,
        ForeignKey("module_test_attempts.id"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("question_bank_items.id"),
        nullable=False
    )