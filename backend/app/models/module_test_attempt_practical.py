from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class ModuleTestAttemptPractical(Base):
    __tablename__ = "module_test_attempt_practicals"

    id = Column(Integer, primary_key=True)

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