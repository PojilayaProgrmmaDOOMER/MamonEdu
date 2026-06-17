from sqlalchemy import Column, Integer, Text, ForeignKey, Float, String

from app.database import Base


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    practical_task_id = Column(
        Integer,
        ForeignKey("practical_tasks.id"),
        nullable=False
    )

    submitted_code = Column(Text, nullable=False)

    score = Column(Float, default=0)

    evaluation_result = Column(Text, nullable=True)

    status = Column(
        String,
        default="pending"
    )