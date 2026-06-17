from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class OntologyConcept(Base):
    __tablename__ = "ontology_concepts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    concept_type = Column(String, nullable=False)
    difficulty_level = Column(String, nullable=False)