from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func

from app.database import Base


class ModuleTestAttempt(Base):
    __tablename__ = "module_test_attempts"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    module_id = Column(
        Integer,
        ForeignKey("course_modules.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    based_on_attempt_id = Column(
        Integer,
        ForeignKey("module_test_attempts.id"),
        nullable=True
    )

    status = Column(
        String,
        default="in_progress"
    )

    score = Column(
        Integer,
        default=0
    )

    is_passed = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )