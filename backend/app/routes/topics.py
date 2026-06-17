from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.topic import Topic
from app.schemas.topic import TopicCreate, TopicUpdate, TopicResponse
from app.auth.security import get_current_user, require_teacher_or_admin
from app.models.user import User

router = APIRouter(prefix="/topics", tags=["Topics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TopicResponse)
def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    new_topic = Topic(
        title=topic.title,
        description=topic.description,
        difficulty_level=topic.difficulty_level
    )

    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)

    return new_topic


@router.get("/", response_model=list[TopicResponse])
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()
    return topics

@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found"
        )

    return topic


@router.put("/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found"
        )

    topic.title = topic_data.title
    topic.description = topic_data.description
    topic.difficulty_level = topic_data.difficulty_level

    db.commit()
    db.refresh(topic)

    return topic


@router.delete("/{topic_id}")
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin)
):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found"
        )

    db.delete(topic)
    db.commit()

    return {
        "message": "Topic deleted successfully"
    }