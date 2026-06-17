from sqlalchemy import Column, ForeignKey, Integer, String

from app.database import Base


class OntologyRelation(Base):
    __tablename__ = "ontology_relations"

    id = Column(Integer, primary_key=True, index=True)

    source_concept_id = Column(
        Integer,
        ForeignKey("ontology_concepts.id"),
        nullable=False
    )

    target_concept_id = Column(
        Integer,
        ForeignKey("ontology_concepts.id"),
        nullable=False
    )

    relation_type = Column(String, nullable=False)