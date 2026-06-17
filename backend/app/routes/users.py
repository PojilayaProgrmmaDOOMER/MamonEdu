from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.material import Material
from app.models.material_concept import MaterialConcept
from app.models.module_test_attempt import ModuleTestAttempt
from app.models.module_test_attempt_answer import ModuleTestAttemptAnswer
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.course_module_progress import CourseModuleProgress
from app.models.question_bank_concept import QuestionBankConcept
from app.models.ontology_entity import OntologyEntity
from app.models.ontology_graph_relation import OntologyGraphRelation
from app.auth.security import get_current_user
from app.database import SessionLocal
from app.schemas.user import UserProfileResponse, UserProfileUpdate
from app.models.user import User
from app.models.topic import Topic
from app.models.test_attempt import TestAttempt
from app.models.user_topic_mastery import UserTopicMastery
from app.models.code_submission import CodeSubmission
from fastapi import UploadFile, File
import os
import uuid

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me/profile", response_model=UserProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.post("/me/avatar")
def upload_my_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    upload_dir = "static/uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"user_{current_user.id}_{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    avatar_url = f"/static/uploads/avatars/{filename}"

    current_user.avatar_url = avatar_url

    db.query(User).filter(User.id == current_user.id).update(
        {
            "avatar_url": avatar_url
        }
    )

    db.commit()

    return {
        "user_id": current_user.id,
        "avatar_url": avatar_url
    }



@router.put("/me/profile", response_model=UserProfileResponse)
def update_my_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(
        User.id == current_user.id
    ).first()

    if profile_data.username is not None:
        user.username = profile_data.username

    if profile_data.avatar_url is not None:
        user.avatar_url = profile_data.avatar_url

    if profile_data.bio is not None:
        user.bio = profile_data.bio

    db.commit()
    db.refresh(user)

    return user

@router.get("/me/progress")
def get_my_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    module_attempts = db.query(ModuleTestAttempt).filter(
        ModuleTestAttempt.student_id == current_user.id
    ).order_by(ModuleTestAttempt.id.desc()).all()

    practical_submissions = db.query(CodeSubmission).filter(
        CodeSubmission.user_id == current_user.id
    ).all()

    progress_records = db.query(CourseModuleProgress).filter(
        CourseModuleProgress.student_id == current_user.id
    ).all()

    completed_attempts = [
        attempt for attempt in module_attempts
        if attempt.status in ["passed", "failed"]
    ]

    test_scores = [
        attempt.score for attempt in completed_attempts
        if attempt.score is not None
    ]

    practical_scores = [
        submission.score for submission in practical_submissions
        if submission.score is not None
    ]

    average_test_score = round(sum(test_scores) / len(test_scores), 2) if test_scores else 0
    average_practical_score = round(sum(practical_scores) / len(practical_scores), 2) if practical_scores else 0

    weak_concept_map = {}

    failed_attempts = [
        attempt for attempt in completed_attempts
        if attempt.is_passed is False
    ]

    for attempt in failed_attempts:
        wrong_answers = db.query(ModuleTestAttemptAnswer).filter(
            ModuleTestAttemptAnswer.attempt_id == attempt.id,
            ModuleTestAttemptAnswer.is_correct == False,
        ).all()

        wrong_question_ids = [
            answer.question_id for answer in wrong_answers
        ]

        if not wrong_question_ids:
            continue

        concept_links = db.query(QuestionBankConcept).filter(
            QuestionBankConcept.question_id.in_(wrong_question_ids)
        ).all()

        for link in concept_links:
            entity = db.query(OntologyEntity).filter(
                OntologyEntity.id == link.entity_id
            ).first()

            if entity is None:
                continue

            if entity.id not in weak_concept_map:
                weak_concept_map[entity.id] = {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type,
                    "error_count": 0,
                }

            weak_concept_map[entity.id]["error_count"] += 1

    weak_concepts = sorted(
        weak_concept_map.values(),
        key=lambda item: item["error_count"],
        reverse=True
    )

    recommendation_entity_ids = {
        item["id"]
        for item in weak_concepts
    }

    frontier = set(recommendation_entity_ids)

    for _ in range(2):
        if not frontier:
            break

        relations = db.query(OntologyGraphRelation).filter(
            (
                OntologyGraphRelation.source_entity_id.in_(frontier)
            ) |
            (
                OntologyGraphRelation.target_entity_id.in_(frontier)
            )
        ).all()

        next_frontier = set()

        for relation in relations:
            next_frontier.add(relation.source_entity_id)
            next_frontier.add(relation.target_entity_id)

        next_frontier = next_frontier - recommendation_entity_ids
        recommendation_entity_ids.update(next_frontier)
        frontier = next_frontier

    recommended_materials = []

    if recommendation_entity_ids:
        material_rows = (
            db.query(MaterialConcept, Material)
            .join(
                Material,
                Material.id == MaterialConcept.material_id
            )
            .filter(
                Material.status == "approved",
                MaterialConcept.concept_id.in_(list(recommendation_entity_ids)),
            )
            .all()
        )

        seen_materials = set()

        for link, material in material_rows:
            if material.id not in seen_materials:
                recommended_materials.append({
                    "id": material.id,
                    "title": material.title,
                    "description": material.description or material.content,
                    "material_type": material.material_type,
                    "resource_type": material.resource_type,
                    "source_url": material.source_url,
                    "pdf_url": material.pdf_url,
                    "reason": "Связан со слабым или соседним концептом",
                })
                seen_materials.add(material.id)

    recent_test_attempts = []

    for attempt in completed_attempts[:8]:
        course = db.query(Course).filter(
            Course.id == attempt.course_id
        ).first()

        module = db.query(CourseModule).filter(
            CourseModule.id == attempt.module_id
        ).first()

        recent_test_attempts.append({
            "id": attempt.id,
            "course_id": attempt.course_id,
            "course_title": course.title if course else None,
            "module_id": attempt.module_id,
            "module_title": (
                f"Модуль {module.position}. {module.title}"
                if module else None
            ),
            "module_position": module.position if module else None,
            "score": attempt.score,
            "status": attempt.status,
            "is_passed": attempt.is_passed,
        })

    module_progress = []

    for record in progress_records:
        course = db.query(Course).filter(
            Course.id == record.course_id
        ).first()

        module = db.query(CourseModule).filter(
            CourseModule.id == record.module_id
        ).first()

        module_progress.append({
            "course_id": record.course_id,
            "course_title": course.title if course else None,
            "module_id": record.module_id,
            "module_title": (
                f"Модуль {module.position}. {module.title}"
                if module else None
            ),
            "module_position": module.position if module else None,
            "status": record.status,
            "is_completed": record.is_completed,
            "score": record.score,
            "completed_at": record.completed_at,
        })

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "avatar_url": current_user.avatar_url,
            "bio": current_user.bio,
        },
        "summary": {
            "test_attempts_count": len(module_attempts),
            "completed_test_attempts_count": len(completed_attempts),
            "practical_submissions_count": len(practical_submissions),
            "average_test_score": average_test_score,
            "average_practical_score": average_practical_score,
            "weak_concepts_count": len(weak_concepts),
            "completed_modules_count": len([
                item for item in progress_records if item.is_completed
            ]),
        },
        "weak_topics": weak_concepts,
        "weak_concepts": weak_concepts,
        "recommended_materials": recommended_materials,
        "recent_test_attempts": recent_test_attempts,
        "module_progress": module_progress,
        "recent_practical_submissions": [
            {
                "id": submission.id,
                "practical_task_id": submission.practical_task_id,
                "score": submission.score,
                "status": submission.status,
                "evaluation_result": submission.evaluation_result,
            }
            for submission in practical_submissions[-5:]
        ],
    }

@router.get("/me/recommendations")
def get_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mastery_records = db.query(UserTopicMastery).filter(
        UserTopicMastery.user_id == current_user.id,
        UserTopicMastery.is_mastered == False
    ).all()

    recommended_materials = []

    for record in mastery_records:
        concept_links = db.query(MaterialConcept).all()

        for link in concept_links:
            concept = db.query(OntologyConcept).filter(
                OntologyConcept.id == link.concept_id
            ).first()

            material = db.query(Material).filter(
                Material.id == link.material_id
            ).first()

            if concept is None or material is None:
                continue

            recommended_materials.append({
                "material_id": material.id,
                "title": material.title,
                "material_type": material.material_type,
                "source_url": material.source_url,
                "concept": {
                    "id": concept.id,
                    "name": concept.name,
                    "difficulty_level": concept.difficulty_level,
                },
                "reason": "Recommended because this topic is not mastered yet"
            })

    return {
        "recommendations_count": len(recommended_materials),
        "materials": recommended_materials
    }