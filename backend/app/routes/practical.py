from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback
import numpy as np
import random
import numpy as np
import json
from app.models.ontology_relation import OntologyRelation
from app.auth.security import get_current_user, require_teacher_or_admin
from app.database import SessionLocal
from app.models.question import Question
from app.models.question_concept import QuestionConcept
from app.models.answer_option import AnswerOption
from app.models.test_attempt import TestAttempt
from app.models.test_attempt_question import TestAttemptQuestion
from app.models.user import User
from app.models.topic import Topic
from app.models.practical_task import PracticalTask
from app.models.code_submission import CodeSubmission
from app.models.practical_task_concept import PracticalTaskConcept
from app.models.ontology_concept import OntologyConcept
from app.models.material import Material
from app.models.material_concept import MaterialConcept

from app.schemas.practical import (
    PracticalTaskCreate,
    PracticalTaskResponse,
    CodeSubmissionCreate,
    CodeSubmissionResponse,
    PracticalTaskConceptCreate,
    PracticalEvaluationResponse,
)

from app.schemas.test_engine import (
    TestStartResponse,
    TestStartResponseQuestion,
    TestStartResponseOption,
)


router = APIRouter(prefix="/practical", tags=["Practical Tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def calculate_iou(pred_mask, true_mask) -> float:
    pred_mask = np.array(pred_mask).astype(bool)
    true_mask = np.array(true_mask).astype(bool)

    intersection = np.logical_and(pred_mask, true_mask).sum()
    union = np.logical_or(pred_mask, true_mask).sum()

    if union == 0:
        return 0.0

    return float(intersection / union)


@router.post("/tasks", response_model=PracticalTaskResponse)
def create_practical_task(
    task: PracticalTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    topic = db.query(Topic).filter(Topic.id == task.topic_id).first()

    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    new_task = PracticalTask(
        topic_id=task.topic_id,
        title=task.title,
        description=task.description,
        starter_code=task.starter_code,
        expected_function_name=task.expected_function_name,
        evaluation_type=task.evaluation_type,
        test_code=task.test_code,
        max_score=task.max_score,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/tasks", response_model=list[PracticalTaskResponse])
def get_practical_tasks(db: Session = Depends(get_db)):
    return db.query(PracticalTask).all()


@router.get("/tasks/{task_id}", response_model=PracticalTaskResponse)
def get_practical_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(PracticalTask).filter(
        PracticalTask.id == task_id
    ).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Practical task not found")

    return task


@router.post(
    "/tasks/{task_id}/submit-code",
    response_model=PracticalEvaluationResponse,
)
def submit_code(
    task_id: int,
    submission: CodeSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(PracticalTask).filter(
        PracticalTask.id == task_id
    ).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Practical task not found")

    local_scope = {}

    try:
        safe_globals = {
            "__builtins__": {
                "range": range,
                "len": len,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "float": float,
                "int": int,
                "bool": bool,
                "list": list,
            },
            "np": np,
        }

        exec(submission.submitted_code, safe_globals, local_scope)

        if task.expected_function_name not in local_scope:
            raise Exception(f"Function {task.expected_function_name} not found")
        
        if task.evaluation_type == "custom_tests":
            if not task.test_code:
                raise Exception("Test code is not configured for this task")

            test_results = []

            def check(name: str, condition: bool):
                test_results.append({
                    "name": name,
                    "passed": bool(condition)
                })

            local_scope["check"] = check

            exec(task.test_code, safe_globals, local_scope)

            total_tests = len(test_results)
            passed_tests = sum(1 for test in test_results if test["passed"])

            if total_tests == 0:
                raise Exception("No checks were executed in test_code")

            score = round((passed_tests / total_tests) * task.max_score, 2)

            evaluation_result = json.dumps({
                "message": f"Passed {passed_tests}/{total_tests} checks",
                "tests": test_results
            }, ensure_ascii=False)

            status = "checked" if passed_tests == total_tests else "failed"

        elif task.evaluation_type == "segmentation_iou":
            test_image = np.array([
                [0, 0, 0, 0, 0],
                [0, 255, 255, 255, 0],
                [0, 255, 255, 255, 0],
                [0, 255, 255, 255, 0],
                [0, 0, 0, 0, 0],
            ])

            true_mask = np.array([
                [0, 0, 0, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 0, 0],
            ])

            student_function = local_scope[task.expected_function_name]
            pred_mask = student_function(test_image)

            iou = calculate_iou(pred_mask, true_mask)
            score = round(iou * 100, 2)

            evaluation_result = f"IoU: {round(iou, 3)}"
            status = "checked"

        else:
            evaluation_result = "Code executed successfully"
            score = 100
            status = "checked"

    except Exception:
        evaluation_result = traceback.format_exc()
        score = 0
        status = "failed"

    weak_concepts = []
    recommended_materials = []

    if score < 75:
        links = db.query(PracticalTaskConcept).filter(
            PracticalTaskConcept.practical_task_id == task.id
        ).all()

        for link in links:
            concept = db.query(OntologyConcept).filter(
                OntologyConcept.id == link.concept_id
            ).first()

            if concept is not None:
                weak_concepts.append({
                    "id": concept.id,
                    "name": concept.name,
                    "difficulty_level": concept.difficulty_level,
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
                            "source_url": material.source_url,
                        })

    new_submission = CodeSubmission(
        user_id=current_user.id,
        practical_task_id=task.id,
        submitted_code=submission.submitted_code,
        score=score,
        evaluation_result=evaluation_result,
        status=status,
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return PracticalEvaluationResponse(
        id=new_submission.id,
        practical_task_id=new_submission.practical_task_id,
        score=new_submission.score,
        evaluation_result=evaluation_result,
        status=new_submission.status,
        weak_concepts=weak_concepts,
        recommended_materials=recommended_materials,
    )


@router.post("/task-concepts")
def link_task_to_concept(
    data: PracticalTaskConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    link = PracticalTaskConcept(
        practical_task_id=data.practical_task_id,
        concept_id=data.concept_id,
    )

    db.add(link)
    db.commit()

    return {
        "message": "Practical task linked to concept"
    }

@router.post(
    "/submissions/{submission_id}/adaptive-retry",
    response_model=TestStartResponse,
)
def practical_adaptive_retry(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    submission = db.query(CodeSubmission).filter(
        CodeSubmission.id == submission_id,
        CodeSubmission.user_id == current_user.id,
    ).first()

    if submission is None:
        raise HTTPException(
            status_code=404,
            detail="Submission not found"
        )

    task = db.query(PracticalTask).filter(
        PracticalTask.id == submission.practical_task_id
    ).first()

    links = db.query(PracticalTaskConcept).filter(
        PracticalTaskConcept.practical_task_id == task.id
    ).all()

    concept_ids = [link.concept_id for link in links]


    def collect_related_concepts(concept_id: int, max_depth: int = 2):
        collected = set()
        visited = set()

        def traverse(current_concept_id: int, depth: int):
            if depth > max_depth:
                return

            relations = db.query(OntologyRelation).filter(
                OntologyRelation.source_concept_id == current_concept_id
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


    candidate_concept_ids = set(concept_ids)

    for concept_id in concept_ids:
        candidate_concept_ids.update(
            collect_related_concepts(concept_id, max_depth=2)
        )

    candidate_question_ids = set()

    for concept_id in candidate_concept_ids:
        question_links = db.query(QuestionConcept).filter(
            QuestionConcept.concept_id == concept_id
    ).all()

        for q_link in question_links:
            candidate_question_ids.add(q_link.question_id)

    candidate_questions = db.query(Question).filter(
        Question.id.in_(candidate_question_ids),
        Question.is_active == True,
    ).all()

    selected_questions = random.sample(
        candidate_questions,
        min(5, len(candidate_questions))
    )

    new_attempt = TestAttempt(
        user_id=current_user.id,
        test_id=1,
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
        test_id=1,
        questions=response_questions,
    )