from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class ModuleTestConcept(Base):
    __tablename__ = "module_test_concepts"

    id = Column(Integer, primary_key=True, index=True)

    module_id = Column(
        Integer,
        ForeignKey("course_modules.id"),
        nullable=False
    )

    entity_id = Column(
        Integer,
        ForeignKey("ontology_entities.id"),
        nullable=False
    )