from sqlalchemy import Column, Integer, Boolean, Text, ForeignKey

from app.database import Base


class ModuleTestAttemptPracticalResult(Base):
    __tablename__ = "module_test_attempt_practical_results"

    id = Column(Integer, primary_key=True, index=True)

    attempt_id = Column(
        Integer,
        ForeignKey("module_test_attempts.id"),
        nullable=False
    )

    task_id = Column(
        Integer,
        ForeignKey("course_practical_tasks.id"),
        nullable=False
    )

    submitted_code = Column(Text, nullable=True)

    score = Column(Integer, nullable=False, default=0)

    is_passed = Column(Boolean, nullable=False, default=False)