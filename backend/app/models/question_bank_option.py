from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.database import Base


class QuestionBankOption(Base):
    __tablename__ = "question_bank_options"

    id = Column(Integer, primary_key=True, index=True)

    question_id = Column(
        Integer,
        ForeignKey("question_bank_items.id"),
        nullable=False
    )

    option_text = Column(String, nullable=False)

    is_correct = Column(Boolean, nullable=False, default=False)

    position = Column(Integer, nullable=False, default=1)