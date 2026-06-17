from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base


class OntologyGraphRelation(Base):
    __tablename__ = "ontology_graph_relations"

    id = Column(Integer, primary_key=True, index=True)

    source_entity_id = Column(
        Integer,
        ForeignKey("ontology_entities.id"),
        nullable=False
    )

    target_entity_id = Column(
        Integer,
        ForeignKey("ontology_entities.id"),
        nullable=False
    )

    relation_type = Column(String, nullable=False)

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=True
    )