from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class MaterialSearchProfile(Base):
    __tablename__ = "material_search_profiles"

    id = Column(Integer, primary_key=True, index=True)

    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    keywords = Column(Text, nullable=False)

    source = Column(String, default="arxiv")

    is_active = Column(Boolean, default=True)
    
    required_keywords = Column(Text, nullable=True)
    excluded_keywords = Column(Text, nullable=True)
    max_results = Column(Integer, default=10)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)