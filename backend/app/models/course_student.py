from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func

from app.database import Base


class CourseStudent(Base):
    __tablename__ = "course_students"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(String, nullable=False, default="active")

    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )