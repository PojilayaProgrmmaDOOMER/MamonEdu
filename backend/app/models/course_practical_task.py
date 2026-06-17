from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.database import Base


class CoursePracticalTask(Base):
    __tablename__ = "course_practical_tasks"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    task_type = Column(String, nullable=False, default="code")

    difficulty = Column(String, nullable=False, default="beginner")

    starter_code = Column(Text, nullable=True)

    tests_code = Column(Text, nullable=True)

    max_score = Column(Integer, nullable=False, default=100)