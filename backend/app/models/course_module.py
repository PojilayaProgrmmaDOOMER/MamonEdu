from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey

from app.database import Base


class CourseModule(Base):
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    position = Column(Integer, nullable=False, default=1)

    is_published = Column(Boolean, nullable=False, default=False)