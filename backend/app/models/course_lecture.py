from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey

from app.database import Base


class CourseLecture(Base):
    __tablename__ = "course_lectures"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)

    module_id = Column(Integer, ForeignKey("course_modules.id"), nullable=False)

    title = Column(String, nullable=False)

    content = Column(Text, nullable=True)

    image_url = Column(String, nullable=True)

    position = Column(Integer, nullable=False, default=1)

    is_published = Column(Boolean, nullable=False, default=False)