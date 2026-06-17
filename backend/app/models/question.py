from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text
)

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    test_id = Column(
        Integer,
        ForeignKey("tests.id"),
        nullable=False
    )

    question_text = Column(Text, nullable=False)

    question_type = Column(String, nullable=False)

    difficulty_level = Column(String, nullable=False)

    weight = Column(Integer, nullable=False)

    explanation = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)