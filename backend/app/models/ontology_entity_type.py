from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base


class OntologyEntityType(Base):
    __tablename__ = "ontology_entity_types"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    color = Column(String, nullable=False, default="#94a3b8")

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=True
    )