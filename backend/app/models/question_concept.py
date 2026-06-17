from sqlalchemy import Column, ForeignKey, Integer

from app.database import Base


class QuestionConcept(Base):
    __tablename__ = "question_concepts"

    id = Column(Integer, primary_key=True, index=True)

    question_id = Column(
        Integer,
        ForeignKey("questions.id"),
        nullable=False
    )

    concept_id = Column(
        Integer,
        ForeignKey("ontology_concepts.id"),
        nullable=False
    )