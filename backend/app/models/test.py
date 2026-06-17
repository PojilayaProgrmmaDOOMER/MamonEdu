from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)

    topic_id = Column(
        Integer,
        ForeignKey("topics.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    difficulty_level = Column(String, nullable=False)