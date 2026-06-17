from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.database import Base


class QuestionBankItem(Base):
    __tablename__ = "question_bank_items"

    id = Column(Integer, primary_key=True, index=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    question_text = Column(Text, nullable=False)

    question_type = Column(String, nullable=False, default="single_choice")

    difficulty = Column(String, nullable=False, default="beginner")

    explanation = Column(Text, nullable=True)

    correct_answer = Column(String, nullable=True)