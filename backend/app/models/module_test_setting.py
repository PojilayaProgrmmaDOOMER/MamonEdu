from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class ModuleTestSetting(Base):
    __tablename__ = "module_test_settings"

    id = Column(Integer, primary_key=True, index=True)

    module_id = Column(
        Integer,
        ForeignKey("course_modules.id"),
        nullable=False,
        unique=True
    )

    pass_score = Column(Integer, nullable=False, default=70)

    question_count = Column(Integer, nullable=False, default=10)

    practical_count = Column(Integer, nullable=False, default=0)

    beginner_count = Column(Integer, nullable=False, default=4)

    intermediate_count = Column(Integer, nullable=False, default=4)

    advanced_count = Column(Integer, nullable=False, default=2)