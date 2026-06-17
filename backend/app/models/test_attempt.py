from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer
)

from datetime import datetime

from app.database import Base


class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    test_id = Column(
        Integer,
        ForeignKey("tests.id"),
        nullable=False
    )

    score = Column(Float, nullable=True)

    started_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )