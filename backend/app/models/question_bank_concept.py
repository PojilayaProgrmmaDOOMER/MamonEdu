from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class QuestionBankConcept(Base):
    __tablename__ = "question_bank_concepts"

    id = Column(Integer, primary_key=True, index=True)

    question_id = Column(
        Integer,
        ForeignKey("question_bank_items.id"),
        nullable=False
    )

    entity_id = Column(
        Integer,
        ForeignKey("ontology_entities.id"),
        nullable=False
    )