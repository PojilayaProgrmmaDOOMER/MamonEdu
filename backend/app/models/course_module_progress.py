from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func

from app.database import Base


class CourseModuleProgress(Base):
    __tablename__ = "course_module_progress"

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

    status = Column(String, nullable=False, default="locked")
    # locked / available / in_progress / completed / failed

    score = Column(Integer, nullable=True)

    is_completed = Column(Boolean, nullable=False, default=False)

    completed_at = Column(DateTime(timezone=True), nullable=True)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )