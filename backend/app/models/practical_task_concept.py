from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class PracticalTaskConcept(Base):
    __tablename__ = "practical_task_concepts"

    id = Column(Integer, primary_key=True, index=True)

    practical_task_id = Column(
        Integer,
        ForeignKey("practical_tasks.id"),
        nullable=False
    )

    concept_id = Column(
        Integer,
        ForeignKey("ontology_concepts.id"),
        nullable=False
    )