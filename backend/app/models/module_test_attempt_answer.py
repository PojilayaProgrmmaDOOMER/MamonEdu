from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.database import Base


class ModuleTestAttemptAnswer(Base):
    __tablename__ = "module_test_attempt_answers"

    id = Column(Integer, primary_key=True, index=True)

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

    selected_answer = Column(String, nullable=True)

    is_correct = Column(Boolean, nullable=False, default=False)