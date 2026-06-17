from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class StudyGroupStudent(Base):
    __tablename__ = "study_group_students"

    id = Column(Integer, primary_key=True, index=True)

    group_id = Column(
        Integer,
        ForeignKey("study_groups.id"),
        nullable=False
    )

    student_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )