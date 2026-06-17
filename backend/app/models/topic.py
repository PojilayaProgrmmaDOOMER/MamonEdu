from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    difficulty_level = Column(String, nullable=False)