from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.database import Base


class OntologyEntity(Base):
    __tablename__ = "ontology_entities"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    entity_type = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=True
    )