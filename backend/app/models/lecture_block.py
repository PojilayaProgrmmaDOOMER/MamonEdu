from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.database import Base


class LectureBlock(Base):
    __tablename__ = "lecture_blocks"

    id = Column(Integer, primary_key=True, index=True)

    lecture_id = Column(
        Integer,
        ForeignKey("course_lectures.id"),
        nullable=False
    )

    block_type = Column(String, nullable=False, default="text")
    # text / image

    content = Column(Text, nullable=True)

    image_url = Column(String, nullable=True)

    position = Column(Integer, nullable=False, default=1)