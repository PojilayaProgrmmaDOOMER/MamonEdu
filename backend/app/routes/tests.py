from datetime import datetime
import random

from app.models.material import Material
from app.models.material_concept import MaterialConcept
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.ontology_relation import OntologyRelation
from app.database import SessionLocal
from app.auth.security import get_current_user, require_teacher_or_admin
from app.models.question_concept import QuestionConcept
from app.models.ontology_concept import OntologyConcept
from app.models.user import User
from app.models.topic import Topic
from app.models.test import Test
from app.models.question import Question
from app.models.answer_option import AnswerOption
from app.models.test_attempt import TestAttempt
from app.models.test_attempt_question import TestAttemptQuestion
from app.models.answer_submission import AnswerSubmission
from app.models.user_topic_mastery import UserTopicMastery

from app.schemas.test import TestCreate, TestResponse
from app.schemas.question import QuestionCreate, QuestionResponse
from app.schemas.answer_option import AnswerOptionCreate, AnswerOptionResponse
from app.schemas.test_engine import (
    TestStartResponse,
    TestStartResponseQuestion,
    TestStartResponseOption,
    TestSubmitRequest,
    TestSubmitResponse,
)


router = APIRouter(prefix="/tests", tags=["Tests"])

ADAPTIVE_RELATION_TYPES = [
    "requires",
    "required_for",
    "related_to",
    "used_in",
    "part_of",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TestResponse)
def create_test(
    test: TestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    topic = db.query(Topic).filter(Topic.id == test.topic_id).first()

    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    new_test = Test(
        topic_id=test.topic_id,
        title=test.title,
        description=test.description,
        difficulty_level=test.difficulty_level,
    )

    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    return new_test


@router.get("/", response_model=list[TestResponse])
def get_tests(db: Session = Depends(get_db)):
    return db.query(Test).all()


@router.post("/questions", response_model=QuestionResponse)
def create_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    test = db.query(Test).filter(Test.id == question.test_id).first()

    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")

    new_question = Question(
        test_id=question.test_id,
        question_text=question.question_text,
        question_type=question.question_type,
        difficulty_level=question.difficulty_level,
        weight=question.weight,
        explanation=question.explanation,
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


@router.get("/{test_id}/questions", response_model=list[QuestionResponse])
def get_test_questions(test_id: int, db: Session = Depends(get_db)):
    test = db.query(Test).filter(Test.id == test_id).first()

    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")

    return db.query(Question).filter(
        Question.test_id == test_id,
        Question.is_active == True,
    ).all()


@router.post("/answer-options", response_model=AnswerOptionResponse)
def create_answer_option(
    option: AnswerOptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    question = db.query(Question).filter(
        Question.id == option.question_id
    ).first()

    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    new_option = AnswerOption(
        question_id=option.question_id,
        option_text=option.option_text,
        is_correct=option.is_correct,
    )

    db.add(new_option)
    db.commit()
    db.refresh(new_option)

    return new_option


@router.get(
    "/questions/{question_id}/answer-options",
    response_model=list[AnswerOptionResponse],
)
def get_question_answer_options(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()

    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    return db.query(AnswerOption).filter(
        AnswerOption.question_id == question_id
    ).all()


@router.post("/{test_id}/start", response_model=TestStartResponse)
def start_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test = db.query(Test).filter(Test.id == test_id).first()

    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")

    questions = db.query(Question).filter(
        Question.test_id == test_id,
        Question.is_active == True,
    ).all()

    if len(questions) == 0:
        raise HTTPException(status_code=400, detail="Test has no active questions")

    beginner_questions = [q for q in questions if q.difficulty_level == "beginner"]
    intermediate_questions = [q for q in questions if q.difficulty_level == "intermediate"]
    advanced_questions = [q for q in questions if q.difficulty_level == "advanced"]
    review_questions = [q for q in questions if q.difficulty_level == "review"]

    selected_questions = []

    selected_questions.extend(random.sample(beginner_questions, min(8, len(beginner_questions))))
    selected_questions.extend(random.sample(intermediate_questions, min(6, len(intermediate_questions))))
    selected_questions.extend(random.sample(advanced_questions, min(4, len(advanced_questions))))
    selected_questions.extend(random.sample(review_questions, min(2, len(review_questions))))

    if len(selected_questions) == 0:
        selected_questions = random.sample(questions, min(20, len(questions)))

    random.shuffle(selected_questions)

    attempt = TestAttempt(user_id=current_user.id, test_id=test_id)

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    for question in selected_questions:
        db.add(
            TestAttemptQuestion(
                attempt_id=attempt.id,
                question_id=question.id,
            )
        )

    db.commit()

    response_questions = []

    for question in selected_questions:
        options = db.query(AnswerOption).filter(
            AnswerOption.question_id == question.id
        ).all()

        response_options = [
            TestStartResponseOption(
                id=option.id,
                option_text=option.option_text,
            )
            for option in options
        ]

        response_questions.append(
            TestStartResponseQuestion(
                id=question.id,
                question_text=question.question_text,
                question_type=question.question_type,
                difficulty_level=question.difficulty_level,
                weight=question.weight,
                options=response_options,
            )
        )

    return TestStartResponse(
        attempt_id=attempt.id,
        test_id=test_id,
        questions=response_questions,
    )


@router.post(
    "/attempts/{attempt_id}/submit",
    response_model=TestSubmitResponse,
)
def submit_test(
    attempt_id: int,
    request: TestSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id,
    ).first()

    if attempt is None:
        raise HTTPException(status_code=404, detail="Test attempt not found")

    attempt_questions = db.query(TestAttemptQuestion).filter(
        TestAttemptQuestion.attempt_id == attempt_id
    ).all()

    allowed_question_ids = {item.question_id for item in attempt_questions}

    total_weight = 0
    earned_weight = 0
    correct_answers = 0
    weak_concepts = []
    recommended_concepts = []
    recommended_materials = []
    

    level_stats = {
        "beginner": {"total": 0, "earned": 0},
        "intermediate": {"total": 0, "earned": 0},
        "advanced": {"total": 0, "earned": 0},
        "review": {"total": 0, "earned": 0},
    }

    for answer in request.answers:
        if answer.question_id not in allowed_question_ids:
            raise HTTPException(
                status_code=400,
                detail="Question was not included in this attempt",
            )

        question = db.query(Question).filter(Question.id == answer.question_id).first()

        if question is None:
            raise HTTPException(status_code=404, detail="Question not found")

        correct_options = db.query(AnswerOption).filter(
            AnswerOption.question_id == answer.question_id,
            AnswerOption.is_correct == True,
        ).all()

        correct_option_ids = {option.id for option in correct_options}
        selected_option_ids = set(answer.selected_option_ids)

        question_is_correct = selected_option_ids == correct_option_ids

        total_weight += question.weight
        level_stats[question.difficulty_level]["total"] += question.weight

        if question_is_correct:
            earned_weight += question.weight
            correct_answers += 1
            level_stats[question.difficulty_level]["earned"] += question.weight
        else:
            question_concepts = db.query(QuestionConcept).filter(
                QuestionConcept.question_id == question.id
            ).all()

            for question_concept in question_concepts:
                concept = db.query(OntologyConcept).filter(
                    OntologyConcept.id == question_concept.concept_id
                ).first()

                if concept is not None:
                    weak_concepts.append({
                        "id": concept.id,
                        "name": concept.name,
                        "difficulty_level": concept.difficulty_level
                    })

                    relations = db.query(OntologyRelation).filter(
                        OntologyRelation.source_concept_id == concept.id
                    ).all()

                    for relation in relations:
                        related_concept = db.query(OntologyConcept).filter(
                            OntologyConcept.id == relation.target_concept_id
                        ).first()

                        if related_concept is not None:
                            recommended_concepts.append({
                                "id": related_concept.id,
                                "name": related_concept.name,
                                "difficulty_level": related_concept.difficulty_level,
                                "relation_type": relation.relation_type
                             })

                    material_links = db.query(MaterialConcept).filter(
                        MaterialConcept.concept_id == concept.id
                    ).all()

                    for material_link in material_links:
                        material = db.query(Material).filter(
                            Material.id == material_link.material_id
                        ).first()

                        if material is not None:
                            recommended_materials.append({
                                "id": material.id,
                                "title": material.title,
                                "material_type": material.material_type,
                                "source_url": material.source_url
                            })

        for selected_option_id in answer.selected_option_ids:
            option = db.query(AnswerOption).filter(
                AnswerOption.id == selected_option_id,
                AnswerOption.question_id == answer.question_id,
            ).first()

            if option is None:
                raise HTTPException(status_code=400, detail="Invalid answer option")

            db.add(
                AnswerSubmission(
                    attempt_id=attempt_id,
                    question_id=answer.question_id,
                    selected_option_id=selected_option_id,
                    is_correct=option.is_correct,
                )
            )

    if total_weight == 0:
        score = 0
    else:
        score = round((earned_weight / total_weight) * 100, 2)

    def calculate_level_score(level_name: str) -> float:
        total = level_stats[level_name]["total"]
        earned = level_stats[level_name]["earned"]

        if total == 0:
            return 0

        return round((earned / total) * 100, 2)

    beginner_score = calculate_level_score("beginner")
    intermediate_score = calculate_level_score("intermediate")
    advanced_score = calculate_level_score("advanced")
    review_score = calculate_level_score("review")

    is_mastered = (
        score >= 75
        and beginner_score >= 80
        and intermediate_score >= 70
        and advanced_score >= 50
    )

    attempt.score = score
    attempt.completed_at = datetime.utcnow()

    test = db.query(Test).filter(Test.id == attempt.test_id).first()

    mastery = db.query(UserTopicMastery).filter(
        UserTopicMastery.user_id == current_user.id,
        UserTopicMastery.topic_id == test.topic_id,
    ).first()

    if mastery is None:
        mastery = UserTopicMastery(
            user_id=current_user.id,
            topic_id=test.topic_id,
        )
        db.add(mastery)

    mastery.overall_score = score
    mastery.beginner_score = beginner_score
    mastery.intermediate_score = intermediate_score
    mastery.advanced_score = advanced_score
    mastery.review_score = review_score
    mastery.is_mastered = is_mastered

    db.commit()

    return TestSubmitResponse(
        attempt_id=attempt.id,
        score=score,
        is_passed=is_mastered,
        correct_answers=correct_answers,
        total_questions=len(allowed_question_ids),
        total_weight=total_weight,
        earned_weight=earned_weight,
        beginner_score=beginner_score,
        intermediate_score=intermediate_score,
        advanced_score=advanced_score,
        review_score=review_score,
        weak_concepts=weak_concepts,
        recommended_concepts=recommended_concepts,
        recommended_materials=recommended_materials,
    )

@router.get("/attempts/{attempt_id}/recommendations")
def get_attempt_recommendations(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id,
    ).first()

    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Test attempt not found"
        )

    wrong_submissions = db.query(AnswerSubmission).filter(
        AnswerSubmission.attempt_id == attempt_id,
        AnswerSubmission.is_correct == False,
    ).all()

    wrong_question_ids = {
        submission.question_id for submission in wrong_submissions
    }

    weak_concept_ids = set()

    for question_id in wrong_question_ids:
        links = db.query(QuestionConcept).filter(
            QuestionConcept.question_id == question_id
        ).all()

        for link in links:
            weak_concept_ids.add(link.concept_id)

    def collect_related_concepts(concept_id: int, max_depth: int = 2):
        collected = set()
        visited = set()

        def traverse(current_concept_id: int, depth: int):
            if depth > max_depth:
                return

            relations = db.query(OntologyRelation).filter(
                OntologyRelation.source_concept_id == current_concept_id,
                OntologyRelation.relation_type.in_(ADAPTIVE_RELATION_TYPES),
            ).all()

            for relation in relations:
                target_id = relation.target_concept_id

                if target_id in visited:
                    continue

                visited.add(target_id)
                collected.add(target_id)

                traverse(target_id, depth + 1)

        traverse(concept_id, 1)

        return collected

    related_concept_ids = set()

    for concept_id in weak_concept_ids:
        related_concept_ids.update(
            collect_related_concepts(concept_id, max_depth=2)
        )
    related_concept_ids = related_concept_ids - weak_concept_ids
    all_recommendation_concept_ids = weak_concept_ids | related_concept_ids

    weak_concepts = db.query(OntologyConcept).filter(
        OntologyConcept.id.in_(weak_concept_ids)
    ).all()

    related_concepts = db.query(OntologyConcept).filter(
        OntologyConcept.id.in_(related_concept_ids)
    ).all()

    material_links = db.query(MaterialConcept).filter(
        MaterialConcept.concept_id.in_(all_recommendation_concept_ids)
    ).all()

    material_ids = {link.material_id for link in material_links}

    materials = []

    if len(material_ids) > 0:
        materials = db.query(Material).filter(
            Material.id.in_(material_ids)
        ).all()

    return {
        "attempt_id": attempt.id,
        "test_id": attempt.test_id,
        "score": attempt.score,
        "is_passed": attempt.score is not None and attempt.score >= 75,
        "wrong_questions_count": len(wrong_question_ids),

        "weak_concepts": [
            {
                "id": concept.id,
                "name": concept.name,
                "description": concept.description,
                "concept_type": concept.concept_type,
                "difficulty_level": concept.difficulty_level,
            }
            for concept in weak_concepts
        ],

        "related_concepts": [
            {
                "id": concept.id,
                "name": concept.name,
                "description": concept.description,
                "concept_type": concept.concept_type,
                "difficulty_level": concept.difficulty_level,
            }
            for concept in related_concepts
        ],

        "recommended_materials": [
            {
                "id": material.id,
                "topic_id": material.topic_id,
                "title": material.title,
                "material_type": material.material_type,
                "source_url": material.source_url,
                "status": material.status,
            }
            for material in materials
        ],

        "can_start_adaptive_retry": len(all_recommendation_concept_ids) > 0,
    }



@router.post(
    "/attempts/{attempt_id}/adaptive-retry",
    response_model=TestStartResponse,
)
def adaptive_retry(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    old_attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id,
    ).first()

    if old_attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Test attempt not found"
        )
    test = db.query(Test).filter(
        Test.id == old_attempt.test_id
    ).first()

    mastery = db.query(UserTopicMastery).filter(
        UserTopicMastery.user_id == current_user.id,
        UserTopicMastery.topic_id == test.topic_id,
    ).first()

    if mastery and mastery.is_mastered:
        raise HTTPException(
            status_code=400,
            detail="Topic already mastered. Adaptive retry is not required."
        )
    old_attempt_questions = db.query(TestAttemptQuestion).filter(
        TestAttemptQuestion.attempt_id == attempt_id
    ).all()

    old_question_ids = {
        item.question_id for item in old_attempt_questions
    }

    wrong_submissions = db.query(AnswerSubmission).filter(
        AnswerSubmission.attempt_id == attempt_id,
        AnswerSubmission.is_correct == False,
    ).all()

    wrong_question_ids = {
        submission.question_id for submission in wrong_submissions
    }

    weak_concept_ids = set()

    for question_id in wrong_question_ids:
        links = db.query(QuestionConcept).filter(
            QuestionConcept.question_id == question_id
        ).all()

        for link in links:
            weak_concept_ids.add(link.concept_id)

    if len(weak_concept_ids) == 0:
        raise HTTPException(
            status_code=400,
            detail="No weak concepts found for this attempt"
        )

    def collect_related_concepts(concept_id: int, max_depth: int = 2):
        collected = set()
        visited = set()

        def traverse(current_concept_id: int, depth: int):
            if depth > max_depth:
                return

            relations = db.query(OntologyRelation).filter(
                OntologyRelation.source_concept_id == current_concept_id,
                OntologyRelation.relation_type.in_(ADAPTIVE_RELATION_TYPES),
            ).all()

            for relation in relations:
                target_id = relation.target_concept_id

                if target_id in visited:
                    continue

                visited.add(target_id)
                collected.add(target_id)

                traverse(target_id, depth + 1)

        traverse(concept_id, 1)

        return collected


    candidate_concept_ids = set(weak_concept_ids)

    for concept_id in weak_concept_ids:
        candidate_concept_ids.update(
            collect_related_concepts(concept_id, max_depth=2)
        )

    candidate_question_ids = set()

    for concept_id in candidate_concept_ids:
        links = db.query(QuestionConcept).filter(
            QuestionConcept.concept_id == concept_id
        ).all()

        for link in links:
            if link.question_id not in old_question_ids:
                candidate_question_ids.add(link.question_id)

    candidate_questions = db.query(Question).filter(
        Question.id.in_(candidate_question_ids),
        Question.is_active == True,
    ).all()

    if len(candidate_questions) == 0:
        raise HTTPException(
            status_code=400,
            detail="No new adaptive questions found"
        )

    selected_questions = random.sample(
        candidate_questions,
        min(20, len(candidate_questions))
    )

    new_attempt = TestAttempt(
        user_id=current_user.id,
        test_id=old_attempt.test_id,
    )

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    for question in selected_questions:
        db.add(
            TestAttemptQuestion(
                attempt_id=new_attempt.id,
                question_id=question.id,
            )
        )

    db.commit()

    response_questions = []

    for question in selected_questions:
        options = db.query(AnswerOption).filter(
            AnswerOption.question_id == question.id
        ).all()

        response_options = [
            TestStartResponseOption(
                id=option.id,
                option_text=option.option_text,
            )
            for option in options
        ]

        response_questions.append(
            TestStartResponseQuestion(
                id=question.id,
                question_text=question.question_text,
                question_type=question.question_type,
                difficulty_level=question.difficulty_level,
                weight=question.weight,
                options=response_options,
            )
        )

    return TestStartResponse(
        attempt_id=new_attempt.id,
        test_id=old_attempt.test_id,
        questions=response_questions,
    )