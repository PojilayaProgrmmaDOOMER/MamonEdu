from sqlalchemy import Column, ForeignKey, Integer

from app.database import Base


class MaterialConcept(Base):
    __tablename__ = "material_concepts"

    id = Column(Integer, primary_key=True, index=True)

    material_id = Column(
        Integer,
        ForeignKey("materials.id"),
        nullable=False
    )

    concept_id = Column(Integer, ForeignKey("ontology_entities.id"), nullable=False)