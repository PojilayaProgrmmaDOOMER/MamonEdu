from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class CoursePracticalConcept(Base):
    __tablename__ = "course_practical_concepts"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(
        Integer,
        ForeignKey("course_practical_tasks.id"),
        nullable=False
    )

    entity_id = Column(
        Integer,
        ForeignKey("ontology_entities.id"),
        nullable=False
    )