from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base


class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    teacher_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )