from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class LectureConcept(Base):
    __tablename__ = "lecture_concepts"

    id = Column(Integer, primary_key=True, index=True)

    lecture_id = Column(
        Integer,
        ForeignKey("course_lectures.id"),
        nullable=False
    )

    entity_id = Column(
        Integer,
        ForeignKey("ontology_entities.id"),
        nullable=False
    )