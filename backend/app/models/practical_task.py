from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy import Float
from app.database import Base


class PracticalTask(Base):
    __tablename__ = "practical_tasks"

    id = Column(Integer, primary_key=True, index=True)

    topic_id = Column(
        Integer,
        ForeignKey("topics.id"),
        nullable=False
    )

    title = Column(String, nullable=False)

    description = Column(Text, nullable=False)

    starter_code = Column(Text, nullable=True)

    expected_function_name = Column(
        String,
        default="segment"
    )

    evaluation_type = Column(
        String,
        default="iou"
    )

    test_code = Column(
        Text,
        nullable=True
    )

    max_score = Column(
        Float,
        default=100
    )