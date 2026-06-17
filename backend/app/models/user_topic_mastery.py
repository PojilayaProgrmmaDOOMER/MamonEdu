from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Boolean

from app.database import Base


class UserTopicMastery(Base):
    __tablename__ = "user_topic_mastery"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    topic_id = Column(
        Integer,
        ForeignKey("topics.id"),
        nullable=False
    )

    overall_score = Column(Float, nullable=False, default=0)

    beginner_score = Column(Float, nullable=False, default=0)

    intermediate_score = Column(Float, nullable=False, default=0)

    advanced_score = Column(Float, nullable=False, default=0)

    review_score = Column(Float, nullable=False, default=0)

    is_mastered = Column(Boolean, nullable=False, default=False)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )