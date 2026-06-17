from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Text
)

from app.database import Base


class AnswerOption(Base):
    __tablename__ = "answer_options"

    id = Column(Integer, primary_key=True, index=True)

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False
    )

    option_text = Column(Text, nullable=False)

    is_correct = Column(Boolean, default=False)