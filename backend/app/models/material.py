from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)

    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    title = Column(String, nullable=False)

    content = Column(Text, nullable=False)

    material_type = Column(String, nullable=False)

    source_url = Column(String, nullable=True)

    status = Column(String, nullable=False, default="approved")

    pdf_url = Column(String, nullable=True)

    resource_type = Column(String, nullable=True)
    
    description = Column(Text, nullable=True)