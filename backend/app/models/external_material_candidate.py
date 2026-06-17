from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.database import Base


class ExternalMaterialCandidate(Base):
    __tablename__ = "external_material_candidates"

    id = Column(Integer, primary_key=True, index=True)

    search_profile_id = Column(
        Integer,
        ForeignKey("material_search_profiles.id"),
        nullable=False
    )

    title = Column(String, nullable=False)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    source = Column(String, default="arxiv")

    status = Column(String, default="pending")