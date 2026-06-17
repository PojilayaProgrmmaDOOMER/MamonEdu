from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.security import get_current_user, require_teacher_or_admin
from app.database import SessionLocal
from app.models.test_attempt import TestAttempt
from app.models.code_submission import CodeSubmission
from app.models.user_topic_mastery import UserTopicMastery
from app.models.topic import Topic
from app.models.user import User
from app.models.study_group import StudyGroup
from app.models.study_group_student import StudyGroupStudent

from app.schemas.study_group import (
    StudyGroupCreate,
    StudyGroupResponse,
    AddStudentToGroupRequest,
)


router = APIRouter(prefix="/study-groups", tags=["Study Groups"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=StudyGroupResponse)
def create_study_group(
    group: StudyGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    new_group = StudyGroup(
        name=group.name,
        teacher_id=current_user.id,
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return new_group


@router.get("/", response_model=list[StudyGroupResponse])
def get_my_study_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role in ["teacher", "admin"]:
        return db.query(StudyGroup).filter(
            StudyGroup.teacher_id == current_user.id
        ).all()

    student_links = db.query(StudyGroupStudent).filter(
        StudyGroupStudent.student_id == current_user.id
    ).all()

    group_ids = [link.group_id for link in student_links]

    if len(group_ids) == 0:
        return []

    return db.query(StudyGroup).filter(
        StudyGroup.id.in_(group_ids)
    ).all()


@router.post("/{group_id}/students")
def add_student_to_group(
    group_id: int,
    data: AddStudentToGroupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    group = db.query(StudyGroup).filter(
        StudyGroup.id == group_id
    ).first()

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="Study group not found"
        )

    if current_user.role != "admin" and group.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can add students only to your own groups"
        )

    student = db.query(User).filter(
        User.id == data.student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    if student.role != "student":
        raise HTTPException(
            status_code=400,
            detail="User is not a student"
        )

    existing_link = db.query(StudyGroupStudent).filter(
        StudyGroupStudent.group_id == group_id,
        StudyGroupStudent.student_id == data.student_id,
    ).first()

    if existing_link is not None:
        raise HTTPException(
            status_code=400,
            detail="Student already in group"
        )

    link = StudyGroupStudent(
        group_id=group_id,
        student_id=data.student_id,
    )

    db.add(link)
    db.commit()

    return {
        "message": "Student added to group"
    }

@router.get("/{group_id}/analytics")
def get_group_analytics(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    group = db.query(StudyGroup).filter(
        StudyGroup.id == group_id
    ).first()

    if group is None:
        raise HTTPException(
            status_code=404,
            detail="Study group not found"
        )

    if current_user.role != "admin" and group.teacher_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view analytics only for your own groups"
        )

    student_links = db.query(StudyGroupStudent).filter(
        StudyGroupStudent.group_id == group_id
    ).all()

    students_data = []

    for link in student_links:
        student = db.query(User).filter(
            User.id == link.student_id
        ).first()

        if student is None:
            continue

        test_attempts = db.query(TestAttempt).filter(
            TestAttempt.user_id == student.id,
            TestAttempt.completed_at.isnot(None)
        ).all()

        practical_submissions = db.query(CodeSubmission).filter(
            CodeSubmission.user_id == student.id
        ).all()

        mastery_records = db.query(UserTopicMastery).filter(
            UserTopicMastery.user_id == student.id
        ).all()

        test_scores = [
            attempt.score for attempt in test_attempts
            if attempt.score is not None
        ]

        practical_scores = [
            submission.score for submission in practical_submissions
            if submission.score is not None
        ]

        average_test_score = 0
        if len(test_scores) > 0:
            average_test_score = round(
                sum(test_scores) / len(test_scores),
                2
            )

        average_practical_score = 0
        if len(practical_scores) > 0:
            average_practical_score = round(
                sum(practical_scores) / len(practical_scores),
                2
            )

        weak_topics = []

        for record in mastery_records:
            if record.is_mastered is False:
                topic = db.query(Topic).filter(
                    Topic.id == record.topic_id
                ).first()

                weak_topics.append({
                    "topic_id": record.topic_id,
                    "topic_title": topic.title if topic else None,
                    "overall_score": record.overall_score,
                    "beginner_score": record.beginner_score,
                    "intermediate_score": record.intermediate_score,
                    "advanced_score": record.advanced_score,
                    "review_score": record.review_score,
                    "is_mastered": record.is_mastered,
                })

        students_data.append({
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "average_test_score": average_test_score,
            "average_practical_score": average_practical_score,
            "completed_test_attempts_count": len(test_attempts),
            "practical_submissions_count": len(practical_submissions),
            "weak_topics": weak_topics,
        })

    return {
        "group": {
            "id": group.id,
            "name": group.name,
            "teacher_id": group.teacher_id,
        },
        "students_count": len(students_data),
        "students": students_data,
    }