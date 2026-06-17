from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
import pydot
import random
from app.models.lecture_block import LectureBlock
from app.models.question_bank_item import QuestionBankItem
from app.models.question_bank_concept import QuestionBankConcept
from app.database import SessionLocal
from app.auth.security import get_current_user, require_teacher_or_admin
from app.models.course_lecture import CourseLecture
from app.models.user import User
from app.models.material import Material
from app.models.material_concept import MaterialConcept
from app.models.material_search_profile import MaterialSearchProfile
from app.models.external_material_candidate import ExternalMaterialCandidate
from app.models.question import Question
from app.models.question_concept import QuestionConcept
from app.models.ontology_concept import OntologyConcept
from app.models.ontology_relation import OntologyRelation
from app.models.ontology_entity import OntologyEntity
from app.models.ontology_graph_relation import OntologyGraphRelation
from app.models.ontology_entity_type import OntologyEntityType
from app.models.course import Course
from app.models.course_student import CourseStudent
from app.models.course_module import CourseModule
from app.models.lecture_concept import LectureConcept
from app.models.module_test_setting import ModuleTestSetting
from app.models.course_practical_task import CoursePracticalTask
from app.models.course_practical_concept import CoursePracticalConcept
from app.models.course_module_progress import CourseModuleProgress
from app.models.module_test_concept import ModuleTestConcept
from app.models.module_test_attempt import ModuleTestAttempt
from app.models.module_test_attempt_question import ModuleTestAttemptQuestion
from app.models.module_test_attempt_practical import ModuleTestAttemptPractical
from app.models.module_test_attempt_answer import ModuleTestAttemptAnswer
from app.models.module_test_attempt_practical_result import ModuleTestAttemptPracticalResult
from app.models.question_bank_option import QuestionBankOption
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.course_module_progress import CourseModuleProgress
from app.models.module_test_attempt import ModuleTestAttempt
from app.models.module_test_attempt_answer import ModuleTestAttemptAnswer
from app.models.question_bank_concept import QuestionBankConcept
from app.models.ontology_entity import OntologyEntity
from PIL import Image, ImageDraw, ImageFont
from fastapi.responses import FileResponse
from datetime import datetime
import os
import uuid
from PIL import Image, ImageDraw, ImageFont
from fastapi.responses import FileResponse
from datetime import datetime
import uuid
import os
from app.models.user import User
from fastapi import UploadFile, File
import os
import uuid
from datetime import datetime
from app.schemas.ontology import (
    OntologyConceptCreate,
    OntologyConceptResponse,
    OntologyRelationCreate,
    OntologyRelationResponse,
    QuestionConceptCreate,
    QuestionConceptResponse,
    MaterialConceptCreate,
    MaterialConceptResponse,
    OntologyEntityCreate,
    OntologyEntityResponse,
    OntologyEntityUpdate,
    OntologyGraphRelationCreate,
    OntologyGraphRelationResponse,
    OntologyEntityTypeCreate,
    OntologyEntityTypeUpdate,
    OntologyEntityTypeResponse,
    CourseCreate,
    CourseResponse,
    CourseUpdate,
    CourseStudentAdd,
    CourseStudentResponse,
    CourseStudentAddByUsername,
    CourseModuleCreate,
    CourseModuleUpdate,
    CourseModuleResponse,
    CourseLectureCreate,
    CourseLectureUpdate,
    CourseLectureResponse,
    LectureConceptCreate,
    LectureConceptResponse,
    ModuleTestSettingCreate,
    ModuleTestSettingUpdate,
    ModuleTestSettingResponse,
    QuestionBankItemCreate,
    QuestionBankItemUpdate,
    QuestionBankItemResponse,
    QuestionBankConceptCreate,
    QuestionBankConceptResponse,
    CoursePracticalTaskCreate,
    CoursePracticalTaskUpdate,
    CoursePracticalTaskResponse,
    CoursePracticalConceptCreate,
    CoursePracticalConceptResponse,
    CourseModuleProgressCreate,
    CourseModuleProgressUpdate,
    CourseModuleProgressResponse,
    ModuleTestConceptCreate,
    ModuleTestConceptResponse,
    ModuleTestAttemptSubmit,
    ModuleTestAttemptSubmitResponse,
    QuestionBankOptionCreate,
    QuestionBankOptionUpdate,
    QuestionBankOptionResponse,
    LectureBlockCreate,
    LectureBlockUpdate,
    LectureBlockResponse,
    CourseMaterialCreate,
)


router = APIRouter(prefix="/ontology", tags=["Ontology"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def course_to_response(course: Course, db: Session):
    root_entity = db.query(OntologyEntity).filter(
        OntologyEntity.id == course.root_entity_id
    ).first()

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "root_entity_id": course.root_entity_id,
        "created_by": course.created_by,
        "status": course.status,
        "root_entity_name": root_entity.name if root_entity else None,
        "root_entity_type": root_entity.entity_type if root_entity else None,
        "cover_url": course.cover_url,
    }

@router.get("/courses/{course_id}/certificate")
def generate_course_certificate(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    modules = db.query(CourseModule).filter(
        CourseModule.course_id == course_id
    ).all()

    if not modules:
        raise HTTPException(status_code=400, detail="Course has no modules")

    completed_count = db.query(CourseModuleProgress).filter(
        CourseModuleProgress.course_id == course_id,
        CourseModuleProgress.student_id == current_user.id,
        CourseModuleProgress.is_completed == True,
    ).count()

    if completed_count < len(modules):
        raise HTTPException(
            status_code=403,
            detail="Course is not completed yet"
        )

    teacher = db.query(User).filter(User.id == course.created_by).first()

    os.makedirs("static/certificates", exist_ok=True)

    width, height = 1920, 1080
    
    # Шрифты
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 72)
        name_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 54)
        text_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 34)
        small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Курсивные шрифты
    try:
        italic_name_font = ImageFont.truetype("C:/Windows/Fonts/ariali.ttf", 54)
        italic_text_font = ImageFont.truetype("C:/Windows/Fonts/ariali.ttf", 34)
    except:
        italic_name_font = name_font
        italic_text_font = text_font

    # Фон с мягким градиентом
    image = Image.new("RGB", (width, height), "#f4f6fb")

    for y in range(height):
        ratio = y / height
        r = int(244 + (255 - 244) * ratio)
        g = int(246 + (251 - 246) * ratio)
        b = int(251 + (255 - 251) * ratio)

        for x in range(width):
            image.putpixel((x, y), (r, g, b))

    draw = ImageDraw.Draw(image)

    # Белая карточка без рамки
    draw.rounded_rectangle(
        (90, 70, width - 90, height - 70),
        radius=44,
        fill="#ffffff",
    )

    # Акценты
    draw.ellipse((-230, -230, 540, 540), fill="#f2c340")
    draw.ellipse((1470, 720, 2100, 1350), fill="#9f1239")
    draw.ellipse((1160, 110, 1500, 450), fill="#fff7d6")

    # Крупный логотип слева сверху
    try:
        logo = Image.open("static/logo/mammoth.png").convert("RGBA")
        logo.thumbnail((520, 520))
        image.paste(logo, (110, 70), logo)
    except Exception as e:
        print("Logo not loaded:", e)

    # Центрированные заголовки
    brand_text = "MamontEdu"
    cert_text = "СЕРТИФИКАТ"
    subtitle_text = "подтверждает успешное завершение курса"

    brand_bbox = draw.textbbox((0, 0), brand_text, font=name_font)
    cert_bbox = draw.textbbox((0, 0), cert_text, font=title_font)
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=text_font)

    draw.text(
        ((width - (brand_bbox[2] - brand_bbox[0])) / 2, 110),
        brand_text,
        fill="#111827",
        font=name_font,
    )

    draw.text(
        ((width - (cert_bbox[2] - cert_bbox[0])) / 2, 205),
        cert_text,
        fill="#111827",
        font=title_font,
    )

    draw.text(
        ((width - (subtitle_bbox[2] - subtitle_bbox[0])) / 2, 300),
        subtitle_text,
        fill="#64748b",
        font=text_font,
    )

    # Название курса сразу под подписью, по центру
    course_bbox = draw.textbbox((0, 0), course.title, font=name_font)

    draw.text(
        ((width - (course_bbox[2] - course_bbox[0])) / 2, 370),
        course.title,
        fill="#9f1239",
        font=name_font,
    )

    teacher_name = teacher.username if teacher else "Преподаватель курса"
    completion_date = datetime.now().strftime("%d.%m.%Y")

    # Контент слева, но ниже жёлтого круга
    draw.text(
        (240, 580),
        "Студент:",
        fill="#64748b",
        font=text_font,
    )

    draw.text(
        (240, 635),
        current_user.username,
        fill="#111827",
        font=italic_name_font,
    )

    draw.text(
        (240, 750),
        "Преподаватель курса:",
        fill="#64748b",
        font=text_font,
    )

    draw.text(
        (240, 805),
        teacher_name,
        fill="#111827",
        font=italic_text_font,
    )

    draw.text(
        (240, 905),
        f"Дата получения: {completion_date}",
        fill="#334155",
        font=text_font,
    )

    certificate_number = f"CERT-{course_id}-{current_user.id}-{uuid.uuid4().hex[:8].upper()}"

    draw.text(
        (240, 970),
        certificate_number,
        fill="#64748b",
        font=small_font,
    )

    # Подпись справа
    draw.line((1230, 820, 1650, 820), fill="#111827", width=3)
    draw.text(
        (1300, 840),
        "подпись преподавателя",
        fill="#64748b",
        font=small_font,
    )

    filename = f"certificate_{course_id}_{current_user.id}.png"
    path = os.path.join("static/certificates", filename)

    image.save(path)

    return FileResponse(
        path,
        media_type="image/png",
        filename=filename,
    )


@router.get("/courses/{course_id}/materials")
def get_course_materials(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    materials = db.query(Material).filter(
        Material.course_id == course_id
    ).order_by(Material.id.desc()).all()

    result = []

    for material in materials:
        links = db.query(MaterialConcept, OntologyEntity).join(
            OntologyEntity,
            OntologyEntity.id == MaterialConcept.concept_id
        ).filter(
            MaterialConcept.material_id == material.id
        ).all()

        result.append({
            "id": material.id,
            "title": material.title,
            "content": material.content,
            "material_type": material.material_type,
            "source_url": material.source_url,
            "pdf_url": material.pdf_url,
            "status": material.status,
            "concepts": [
                {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type,
                }
                for link, entity in links
            ],
        })

    return result


@router.delete("/materials/{material_id}")
def delete_course_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")

    db.query(MaterialConcept).filter(
        MaterialConcept.material_id == material.id
    ).delete(synchronize_session=False)

    db.delete(material)
    db.commit()

    return {"message": "Material deleted"}


@router.post("/courses/{course_id}/cover")
def upload_course_cover(
    course_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    upload_dir = "static/uploads/courses"
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"course_{course_id}_{uuid.uuid4()}{ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    cover_url = f"/static/uploads/courses/{filename}"

    course.cover_url = cover_url

    db.commit()
    db.refresh(course)

    return {
        "course_id": course.id,
        "cover_url": cover_url
    }



@router.get(
    "/lectures/{lecture_id}/blocks",
    response_model=list[LectureBlockResponse],
)
def get_lecture_blocks(
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture not found"
        )

    return db.query(LectureBlock).filter(
        LectureBlock.lecture_id == lecture_id
    ).order_by(LectureBlock.position).all()


@router.post(
    "/lectures/{lecture_id}/blocks",
    response_model=LectureBlockResponse,
)
def create_lecture_block(
    lecture_id: int,
    data: LectureBlockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture not found"
        )

    course = db.query(Course).filter(
        Course.id == lecture.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    block = LectureBlock(
        lecture_id=lecture_id,
        block_type=data.block_type,
        content=data.content,
        image_url=data.image_url,
        position=data.position,
    )

    db.add(block)
    db.commit()
    db.refresh(block)

    return block


@router.put(
    "/lectures/{lecture_id}/blocks/{block_id}",
    response_model=LectureBlockResponse,
)
def update_lecture_block(
    lecture_id: int,
    block_id: int,
    data: LectureBlockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture not found"
        )

    course = db.query(Course).filter(
        Course.id == lecture.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    block = db.query(LectureBlock).filter(
        LectureBlock.id == block_id,
        LectureBlock.lecture_id == lecture_id,
    ).first()

    if block is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture block not found"
        )

    block.block_type = data.block_type
    block.content = data.content
    block.image_url = data.image_url
    block.position = data.position

    db.commit()
    db.refresh(block)

    return block


@router.delete("/lectures/{lecture_id}/blocks/{block_id}")
def delete_lecture_block(
    lecture_id: int,
    block_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture not found"
        )

    course = db.query(Course).filter(
        Course.id == lecture.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    block = db.query(LectureBlock).filter(
        LectureBlock.id == block_id,
        LectureBlock.lecture_id == lecture_id,
    ).first()

    if block is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture block not found"
        )

    db.delete(block)
    db.commit()

    return {
        "message": "Lecture block deleted"
    }

@router.post("/lectures/{lecture_id}/blocks/{block_id}/image")
def upload_lecture_block_image(
    lecture_id: int,
    block_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture not found"
        )

    course = db.query(Course).filter(
        Course.id == lecture.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    block = db.query(LectureBlock).filter(
        LectureBlock.id == block_id,
        LectureBlock.lecture_id == lecture_id,
    ).first()

    if block is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture block not found"
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files allowed"
        )

    upload_dir = "static/uploads/lectures"
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(upload_dir, filename)

    with open(path, "wb") as buffer:
        buffer.write(file.file.read())

    image_url = f"/static/uploads/lectures/{filename}"

    block.block_type = "image"
    block.image_url = image_url

    db.commit()
    db.refresh(block)

    return {
        "block_id": block.id,
        "image_url": image_url
    }


@router.post("/lectures/{lecture_id}/image")
def upload_lecture_image(
    lecture_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Course lecture not found"
        )

    course = db.query(Course).filter(
        Course.id == lecture.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed"
        )

    upload_dir = "static/uploads/lectures"
    os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    image_url = f"/static/uploads/lectures/{filename}"

    lecture.image_url = image_url

    db.commit()
    db.refresh(lecture)

    return {
        "lecture_id": lecture.id,
        "image_url": image_url
    }



@router.get(
    "/question-bank/{question_id}/options",
    response_model=list[QuestionBankOptionResponse],
)
def get_question_bank_options(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    question = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    return db.query(QuestionBankOption).filter(
        QuestionBankOption.question_id == question_id
    ).order_by(QuestionBankOption.position).all()


@router.post(
    "/question-bank/{question_id}/options",
    response_model=QuestionBankOptionResponse,
)
def create_question_bank_option(
    question_id: int,
    data: QuestionBankOptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    question = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    course = db.query(Course).filter(
        Course.id == question.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    option = QuestionBankOption(
        question_id=question_id,
        option_text=data.option_text,
        is_correct=data.is_correct,
        position=data.position,
    )

    db.add(option)
    db.commit()
    db.refresh(option)

    return option


@router.put(
    "/question-bank/{question_id}/options/{option_id}",
    response_model=QuestionBankOptionResponse,
)
def update_question_bank_option(
    question_id: int,
    option_id: int,
    data: QuestionBankOptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    question = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    course = db.query(Course).filter(
        Course.id == question.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    option = db.query(QuestionBankOption).filter(
        QuestionBankOption.id == option_id,
        QuestionBankOption.question_id == question_id,
    ).first()

    if option is None:
        raise HTTPException(
            status_code=404,
            detail="Question option not found"
        )

    option.option_text = data.option_text
    option.is_correct = data.is_correct
    option.position = data.position

    db.commit()
    db.refresh(option)

    return option


@router.delete("/question-bank/{question_id}/options/{option_id}")
def delete_question_bank_option(
    question_id: int,
    option_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    question = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    course = db.query(Course).filter(
        Course.id == question.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    option = db.query(QuestionBankOption).filter(
        QuestionBankOption.id == option_id,
        QuestionBankOption.question_id == question_id,
    ).first()

    if option is None:
        raise HTTPException(
            status_code=404,
            detail="Question option not found"
        )

    db.delete(option)
    db.commit()

    return {
        "message": "Question option deleted"
    }




@router.post("/module-test-attempts/{attempt_id}/adaptive-retry")
def create_adaptive_retry_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    old_attempt = db.query(ModuleTestAttempt).filter(
        ModuleTestAttempt.id == attempt_id
    ).first()

    if old_attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Module test attempt not found"
        )

    if current_user.role == "student" and old_attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can retry only your own attempts"
        )

    if old_attempt.is_passed:
        raise HTTPException(
            status_code=400,
            detail="Passed attempt does not need adaptive retry"
        )

    settings = db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == old_attempt.module_id
    ).first()

    if settings is None:
        raise HTTPException(
            status_code=404,
            detail="Module test settings not found"
        )

    wrong_answers = db.query(ModuleTestAttemptAnswer).filter(
        ModuleTestAttemptAnswer.attempt_id == old_attempt.id,
        ModuleTestAttemptAnswer.is_correct == False,
    ).all()

    wrong_question_ids = [
        answer.question_id
        for answer in wrong_answers
    ]

    weak_entity_ids = []

    if wrong_question_ids:
        concept_links = db.query(QuestionBankConcept).filter(
            QuestionBankConcept.question_id.in_(wrong_question_ids)
        ).all()

        weak_entity_ids = list({
            link.entity_id
            for link in concept_links
        })

    if not weak_entity_ids:
        raise HTTPException(
            status_code=400,
            detail="No weak concepts found for adaptive retry"
        )

    # Обход графа на 2 шага от слабых концептов
    related_entity_ids = set(weak_entity_ids)

    frontier = set(weak_entity_ids)

    for _ in range(2):
        relations = db.query(OntologyGraphRelation).filter(
            OntologyGraphRelation.course_id == old_attempt.course_id,
            (
                (OntologyGraphRelation.source_entity_id.in_(frontier)) |
                (OntologyGraphRelation.target_entity_id.in_(frontier))
            )
        ).all()

        next_frontier = set()

        for relation in relations:
            next_frontier.add(relation.source_entity_id)
            next_frontier.add(relation.target_entity_id)

        next_frontier = next_frontier - related_entity_ids

        related_entity_ids.update(next_frontier)
        frontier = next_frontier

        if not frontier:
            break

    # 1. Сначала берём именно вопросы, в которых студент ошибся
    wrong_questions = db.query(QuestionBankItem).filter(
        QuestionBankItem.course_id == old_attempt.course_id,
        QuestionBankItem.id.in_(wrong_question_ids),
    ).all()

    selected_questions_map = {
        question.id: question
        for question in wrong_questions
    }

    # 2. Добираем вопросы по слабым и связанным концептам
    related_question_ids = [
        link.question_id
        for link in db.query(QuestionBankConcept).filter(
            QuestionBankConcept.entity_id.in_(list(related_entity_ids))
        ).all()
    ]

    additional_questions = db.query(QuestionBankItem).filter(
        QuestionBankItem.course_id == old_attempt.course_id,
        QuestionBankItem.id.in_(related_question_ids),
        ~QuestionBankItem.id.in_(selected_questions_map.keys()),
    ).all()

    random.shuffle(additional_questions)

    target_count = settings.question_count or 20

    for question in additional_questions:
        if len(selected_questions_map) >= target_count:
            break

        selected_questions_map[question.id] = question

    selected_questions = list(selected_questions_map.values())

    if not selected_questions:
        raise HTTPException(
            status_code=404,
            detail="No questions found for adaptive retry"
        )

    # Практические задания по related_entity_ids
    practical_query = db.query(CoursePracticalTask).filter(
        CoursePracticalTask.course_id == old_attempt.course_id
    )

    task_ids = [
        link.task_id
        for link in db.query(CoursePracticalConcept).filter(
            CoursePracticalConcept.entity_id.in_(list(related_entity_ids))
        ).all()
    ]

    selected_practical_tasks = []

    if task_ids:
        practical_tasks = practical_query.filter(
            CoursePracticalTask.id.in_(task_ids)
        ).all()

        selected_practical_tasks = random.sample(
            practical_tasks,
            min(settings.practical_count, len(practical_tasks))
        )

    retry_attempt = ModuleTestAttempt(
        course_id=old_attempt.course_id,
        module_id=old_attempt.module_id,
        student_id=old_attempt.student_id,
        based_on_attempt_id=old_attempt.id,
        status="in_progress",
        score=0,
        is_passed=False,
    )

    db.add(retry_attempt)
    db.commit()
    db.refresh(retry_attempt)

    for question in selected_questions:
        db.add(
            ModuleTestAttemptQuestion(
                attempt_id=retry_attempt.id,
                question_id=question.id,
            )
        )

    for task in selected_practical_tasks:
        db.add(
            ModuleTestAttemptPractical(
                attempt_id=retry_attempt.id,
                task_id=task.id,
            )
        )

    db.commit()

    weak_concepts = []

    if weak_entity_ids:
        weak_entities = db.query(OntologyEntity).filter(
            OntologyEntity.id.in_(weak_entity_ids)
        ).all()

        weak_concepts = [
            {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type,
            }
            for entity in weak_entities
        ]

    related_concepts = []

    related_entities = db.query(OntologyEntity).filter(
        OntologyEntity.id.in_(list(related_entity_ids))
    ).all()

    related_concepts = [
        {
            "id": entity.id,
            "name": entity.name,
            "type": entity.entity_type,
        }
        for entity in related_entities
    ]

    return {
        "attempt_id": retry_attempt.id,
        "course_id": retry_attempt.course_id,
        "module_id": retry_attempt.module_id,
        "status": retry_attempt.status,
        "based_on_attempt_id": old_attempt.id,
        "weak_concepts": weak_concepts,
        "related_concepts": related_concepts,
        "questions": [
            {
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "difficulty": question.difficulty,
                "explanation": question.explanation,
            }
            for question in selected_questions
        ],
        "practical_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "difficulty": task.difficulty,
                "starter_code": task.starter_code,
                "max_score": task.max_score,
            }
            for task in selected_practical_tasks
        ],
    }


@router.get(
    "/courses/{course_id}/modules/{module_id}/test-concepts",
    response_model=list[ModuleTestConceptResponse],
)
def get_module_test_concepts(
    course_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    rows = (
        db.query(ModuleTestConcept, OntologyEntity)
        .join(OntologyEntity, OntologyEntity.id == ModuleTestConcept.entity_id)
        .filter(ModuleTestConcept.module_id == module_id)
        .order_by(OntologyEntity.name)
        .all()
    )

    return [
        {
            "id": link.id,
            "module_id": link.module_id,
            "entity_id": link.entity_id,
            "entity_name": entity.name,
            "entity_type": entity.entity_type,
        }
        for link, entity in rows
    ]


@router.post(
    "/courses/{course_id}/modules/{module_id}/test-concepts",
    response_model=ModuleTestConceptResponse,
)
def add_module_test_concept(
    course_id: int,
    module_id: int,
    data: ModuleTestConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    entity = db.query(OntologyEntity).filter(
        OntologyEntity.id == data.entity_id,
        OntologyEntity.course_id == course_id,
    ).first()

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail="Ontology entity not found in this course"
        )

    existing = db.query(ModuleTestConcept).filter(
        ModuleTestConcept.module_id == module_id,
        ModuleTestConcept.entity_id == data.entity_id,
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Concept already linked to this module test"
        )

    link = ModuleTestConcept(
        module_id=module_id,
        entity_id=data.entity_id,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return {
        "id": link.id,
        "module_id": link.module_id,
        "entity_id": link.entity_id,
        "entity_name": entity.name,
        "entity_type": entity.entity_type,
    }


@router.delete(
    "/courses/{course_id}/modules/{module_id}/test-concepts/{entity_id}"
)
def remove_module_test_concept(
    course_id: int,
    module_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    link = db.query(ModuleTestConcept).filter(
        ModuleTestConcept.module_id == module_id,
        ModuleTestConcept.entity_id == entity_id,
    ).first()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Module test concept link not found"
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Concept removed from module test"
    }


@router.post("/courses/{course_id}/modules/{module_id}/generate-test")
def generate_module_test(
    course_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    settings = db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == module_id
    ).first()

    if settings is None:
        raise HTTPException(
            status_code=404,
            detail="Module test settings not found"
        )

    # Получаем концепты, привязанные к тесту модуля
    test_concept_links = db.query(ModuleTestConcept).filter(
        ModuleTestConcept.module_id == module_id
    ).all()

    test_entity_ids = [
        link.entity_id
        for link in test_concept_links
    ]

    # Формируем запрос вопросов с учетом концептов теста
    questions_query = db.query(QuestionBankItem).filter(
        QuestionBankItem.course_id == course_id
    )

    if test_entity_ids:
        question_ids = [
            link.question_id
            for link in db.query(QuestionBankConcept).filter(
                QuestionBankConcept.entity_id.in_(test_entity_ids)
            ).all()
        ]

        questions_query = questions_query.filter(
            QuestionBankItem.id.in_(question_ids)
        )

    all_questions = questions_query.all()

    # Фильтруем практические задания по концептам теста
    practical_query = db.query(CoursePracticalTask).filter(
        CoursePracticalTask.course_id == course_id
    )

    if test_entity_ids:
        task_ids = [
            link.task_id
            for link in db.query(CoursePracticalConcept).filter(
                CoursePracticalConcept.entity_id.in_(test_entity_ids)
            ).all()
        ]

        practical_query = practical_query.filter(
            CoursePracticalTask.id.in_(task_ids)
        )

    all_practical_tasks = practical_query.all()

    # Распределяем по сложности
    beginner_questions = [
        question for question in all_questions
        if question.difficulty == "beginner"
    ]

    intermediate_questions = [
        question for question in all_questions
        if question.difficulty == "intermediate"
    ]

    advanced_questions = [
        question for question in all_questions
        if question.difficulty == "advanced"
    ]

    selected_questions = []

    selected_questions.extend(
        random.sample(
            beginner_questions,
            min(settings.beginner_count, len(beginner_questions))
        )
    )

    selected_questions.extend(
        random.sample(
            intermediate_questions,
            min(settings.intermediate_count, len(intermediate_questions))
        )
    )

    selected_questions.extend(
        random.sample(
            advanced_questions,
            min(settings.advanced_count, len(advanced_questions))
        )
    )

    if len(selected_questions) < settings.question_count:
        used_ids = {question.id for question in selected_questions}

        remaining_questions = [
            question for question in all_questions
            if question.id not in used_ids
        ]

        need_more = settings.question_count - len(selected_questions)

        selected_questions.extend(
            random.sample(
                remaining_questions,
                min(need_more, len(remaining_questions))
            )
        )

    selected_practical_tasks = random.sample(
        all_practical_tasks,
        min(settings.practical_count, len(all_practical_tasks))
    )

    # === СОЗДАНИЕ ПОПЫТКИ ТЕСТА ===
    attempt = ModuleTestAttempt(
        course_id=course_id,
        module_id=module_id,
        student_id=current_user.id,
        status="in_progress",
        score=0,
        is_passed=False,
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Сохраняем выбранные вопросы в попытку
    for question in selected_questions:
        db.add(
            ModuleTestAttemptQuestion(
                attempt_id=attempt.id,
                question_id=question.id,
            )
        )

    # Сохраняем выбранные практические задания в попытку
    for task in selected_practical_tasks:
        db.add(
            ModuleTestAttemptPractical(
                attempt_id=attempt.id,
                task_id=task.id,
            )
        )

    db.commit()

    return {
        "attempt_id": attempt.id,
        "course_id": course_id,
        "module_id": module_id,
        "pass_score": settings.pass_score,
        "status": attempt.status,
        "questions": [
            {
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "difficulty": question.difficulty,
                "explanation": question.explanation,
            }
            for question in selected_questions
        ],
        "practical_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "difficulty": task.difficulty,
                "starter_code": task.starter_code,
                "max_score": task.max_score,
            }
            for task in selected_practical_tasks
        ],
    }


@router.get("/courses/{course_id}/students-progress")
def get_course_students_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own course statistics"
        )

    modules = db.query(CourseModule).filter(
        CourseModule.course_id == course_id
    ).order_by(CourseModule.position).all()

    total_modules = len(modules)

    student_ids = [
        item.student_id
        for item in db.query(CourseModuleProgress.student_id).filter(
            CourseModuleProgress.course_id == course_id
        ).distinct().all()
    ]

    students = db.query(User).filter(
        User.id.in_(student_ids)
    ).all() if student_ids else []

    result = []

    for student in students:
        progress_records = db.query(CourseModuleProgress).filter(
            CourseModuleProgress.course_id == course_id,
            CourseModuleProgress.student_id == student.id,
        ).all()

        completed_modules = [
            item for item in progress_records
            if item.is_completed
        ]

        percent = round(
            (len(completed_modules) / total_modules) * 100
        ) if total_modules > 0 else 0

        last_attempt = db.query(ModuleTestAttempt).filter(
            ModuleTestAttempt.course_id == course_id,
            ModuleTestAttempt.student_id == student.id,
        ).order_by(ModuleTestAttempt.id.desc()).first()

        weak_concept_map = {}

        failed_attempts = db.query(ModuleTestAttempt).filter(
            ModuleTestAttempt.course_id == course_id,
            ModuleTestAttempt.student_id == student.id,
            ModuleTestAttempt.is_passed == False,
        ).all()

        for attempt in failed_attempts:
            wrong_answers = db.query(ModuleTestAttemptAnswer).filter(
                ModuleTestAttemptAnswer.attempt_id == attempt.id,
                ModuleTestAttemptAnswer.is_correct == False,
            ).all()

            wrong_question_ids = [
                answer.question_id
                for answer in wrong_answers
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
        )[:5]

        result.append({
            "student_id": student.id,
            "username": student.username,
            "email": student.email,
            "avatar_url": student.avatar_url,
            "completed_modules": len(completed_modules),
            "total_modules": total_modules,
            "progress_percent": percent,
            "last_attempt": {
                "id": last_attempt.id,
                "module_id": last_attempt.module_id,
                "score": last_attempt.score,
                "status": last_attempt.status,
                "is_passed": last_attempt.is_passed,
            } if last_attempt else None,
            "weak_concepts": weak_concepts,
        })

    return {
        "course_id": course.id,
        "course_title": course.title,
        "students_count": len(result),
        "students": result,
    }




@router.get("/module-test-attempts/{attempt_id}")
def get_module_test_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.query(ModuleTestAttempt).filter(
        ModuleTestAttempt.id == attempt_id
    ).first()

    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Module test attempt not found"
        )

    if current_user.role == "student" and attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own attempts"
        )

    if current_user.role == "teacher":
        course = db.query(Course).filter(
            Course.id == attempt.course_id
        ).first()

        if course is None or course.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can view only attempts from your own courses"
            )

    question_links = db.query(ModuleTestAttemptQuestion).filter(
        ModuleTestAttemptQuestion.attempt_id == attempt_id
    ).all()

    practical_links = db.query(ModuleTestAttemptPractical).filter(
        ModuleTestAttemptPractical.attempt_id == attempt_id
    ).all()

    question_ids = [link.question_id for link in question_links]
    task_ids = [link.task_id for link in practical_links]

    questions = []
    if question_ids:
        questions = db.query(QuestionBankItem).filter(
            QuestionBankItem.id.in_(question_ids)
        ).all()

    practical_tasks = []
    if task_ids:
        practical_tasks = db.query(CoursePracticalTask).filter(
            CoursePracticalTask.id.in_(task_ids)
        ).all()

    return {
        "attempt_id": attempt.id,
        "course_id": attempt.course_id,
        "module_id": attempt.module_id,
        "student_id": attempt.student_id,
        "based_on_attempt_id": attempt.based_on_attempt_id,
        "status": attempt.status,
        "score": attempt.score,
        "is_passed": attempt.is_passed,
        "questions": [
            {
                "id": question.id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "difficulty": question.difficulty,
                "explanation": question.explanation,
            }
            for question in questions
        ],
        "practical_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type,
                "difficulty": task.difficulty,
                "starter_code": task.starter_code,
                "max_score": task.max_score,
            }
            for task in practical_tasks
        ],
    }

@router.post(
    "/module-test-attempts/{attempt_id}/submit",
    response_model=ModuleTestAttemptSubmitResponse,
)
def submit_module_test_attempt(
    attempt_id: int,
    data: ModuleTestAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attempt = db.query(ModuleTestAttempt).filter(
        ModuleTestAttempt.id == attempt_id
    ).first()

    if attempt is None:
        raise HTTPException(
            status_code=404,
            detail="Module test attempt not found"
        )

    if current_user.role == "student" and attempt.student_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can submit only your own attempts"
        )

    settings = db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == attempt.module_id
    ).first()

    if settings is None:
        raise HTTPException(
            status_code=404,
            detail="Module test settings not found"
        )

    # очищаем старые ответы, если попытка отправляется повторно
    db.query(ModuleTestAttemptAnswer).filter(
        ModuleTestAttemptAnswer.attempt_id == attempt.id
    ).delete(synchronize_session=False)

    db.query(ModuleTestAttemptPracticalResult).filter(
        ModuleTestAttemptPracticalResult.attempt_id == attempt.id
    ).delete(synchronize_session=False)

    question_links = db.query(ModuleTestAttemptQuestion).filter(
        ModuleTestAttemptQuestion.attempt_id == attempt.id
    ).all()

    allowed_question_ids = {
        link.question_id
        for link in question_links
    }

    answer_map = {
        answer.question_id: answer.selected_answer
        for answer in data.question_answers
    }

    questions = []

    if allowed_question_ids:
        questions = db.query(QuestionBankItem).filter(
            QuestionBankItem.id.in_(allowed_question_ids)
        ).all()

    correct_count = 0
    wrong_question_ids = []

    for question in questions:
        selected_answer = answer_map.get(question.id)

        is_correct = False

        if question.question_type == "text":
            is_correct = (
                selected_answer is not None
                and question.correct_answer is not None
                and str(selected_answer).strip().lower()
                == str(question.correct_answer).strip().lower()
            )

        elif question.question_type == "single_choice":
            correct_option = db.query(QuestionBankOption).filter(
                QuestionBankOption.question_id == question.id,
                QuestionBankOption.is_correct == True,
            ).first()

            is_correct = (
                correct_option is not None
                and selected_answer is not None
                and str(selected_answer).strip() == str(correct_option.id)
            )

        elif question.question_type == "multiple_choice":
            correct_options = db.query(QuestionBankOption).filter(
                QuestionBankOption.question_id == question.id,
                QuestionBankOption.is_correct == True,
            ).all()

            correct_ids = {
                str(option.id)
                for option in correct_options
            }

            selected_ids = {
                item.strip()
                for item in str(selected_answer or "").split(",")
                if item.strip()
            }

            is_correct = selected_ids == correct_ids

        if is_correct:
            correct_count += 1
        else:
            wrong_question_ids.append(question.id)

        db.add(
            ModuleTestAttemptAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_answer=selected_answer,
                is_correct=is_correct,
            )
        )

    total_questions = len(questions)

    theory_score = round(
        (correct_count / total_questions) * 100
    ) if total_questions > 0 else 0

    practical_links = db.query(ModuleTestAttemptPractical).filter(
        ModuleTestAttemptPractical.attempt_id == attempt.id
    ).all()

    allowed_task_ids = {
        link.task_id
        for link in practical_links
    }

    practical_result_map = {
        result.task_id: result
        for result in data.practical_results
    }

    practical_scores = []

    for task_id in allowed_task_ids:
        result = practical_result_map.get(task_id)

        score = 0
        submitted_code = None

        if result is not None:
            score = max(0, min(100, int(result.score)))
            submitted_code = result.submitted_code

        practical_scores.append(score)

        db.add(
            ModuleTestAttemptPracticalResult(
                attempt_id=attempt.id,
                task_id=task_id,
                submitted_code=submitted_code,
                score=score,
                is_passed=score >= settings.pass_score,
            )
        )

    practical_score = round(
        sum(practical_scores) / len(practical_scores)
    ) if practical_scores else 0

    if total_questions > 0 and practical_scores:
        final_score = round(theory_score * 0.7 + practical_score * 0.3)
    elif total_questions > 0:
        final_score = theory_score
    elif practical_scores:
        final_score = practical_score
    else:
        final_score = 0

    is_passed = final_score >= settings.pass_score

    # реальные слабые концепты — только из ошибочных вопросов
    weak_concepts = []

    if wrong_question_ids:
        rows = (
            db.query(QuestionBankConcept, OntologyEntity)
            .join(
                OntologyEntity,
                OntologyEntity.id == QuestionBankConcept.entity_id
            )
            .filter(QuestionBankConcept.question_id.in_(wrong_question_ids))
            .all()
        )

        seen_concepts = set()

        for link, entity in rows:
            if entity.id not in seen_concepts:
                weak_concepts.append(
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.entity_type,
                    }
                )
                seen_concepts.add(entity.id)

    weak_entity_ids = [
        concept["id"]
        for concept in weak_concepts
    ]

    recommended_lectures = []

    if weak_entity_ids:
        rows = (
            db.query(LectureConcept, CourseLecture)
            .join(
                CourseLecture,
                CourseLecture.id == LectureConcept.lecture_id
            )
            .filter(
                LectureConcept.entity_id.in_(weak_entity_ids),
                CourseLecture.course_id == attempt.course_id,
            )
            .all()
        )

        seen_lectures = set()

        for link, lecture in rows:
            if lecture.id not in seen_lectures:
                recommended_lectures.append(
                    {
                        "id": lecture.id,
                        "module_id": lecture.module_id,
                        "title": lecture.title,
                        "position": lecture.position,
                    }
                )
                seen_lectures.add(lecture.id)

    recommended_materials = []

    if weak_entity_ids:
        recommendation_entity_ids = set(weak_entity_ids)
        frontier = set(weak_entity_ids)

        for _ in range(2):
            relations = db.query(OntologyGraphRelation).filter(
                OntologyGraphRelation.course_id == attempt.course_id,
                (
                    (OntologyGraphRelation.source_entity_id.in_(frontier)) |
                    (OntologyGraphRelation.target_entity_id.in_(frontier))
                )
            ).all()

            next_frontier = set()

            for relation in relations:
                next_frontier.add(relation.source_entity_id)
                next_frontier.add(relation.target_entity_id)

            next_frontier = next_frontier - recommendation_entity_ids

            recommendation_entity_ids.update(next_frontier)
            frontier = next_frontier

            if not frontier:
                break

        material_rows = (
            db.query(MaterialConcept, Material)
            .join(
                Material,
                Material.id == MaterialConcept.material_id
            )
            .filter(
                Material.course_id == attempt.course_id,
                Material.status == "approved",
                MaterialConcept.concept_id.in_(list(recommendation_entity_ids)),
            )
            .all()
        )

        seen_materials = set()

        for link, material in material_rows:
            if material.id not in seen_materials:
                recommended_materials.append(
                    {
                        "id": material.id,
                        "title": material.title,
                        "description": material.description or material.content,
                        "material_type": material.material_type,
                        "resource_type": material.resource_type,
                        "source_url": material.source_url,
                        "pdf_url": material.pdf_url,
                        "status": material.status,
                        "reason": "Материал связан со слабым или соседним концептом онтологии",
                    }
                )
                seen_materials.add(material.id)

    attempt.score = final_score
    attempt.is_passed = is_passed
    attempt.status = "passed" if is_passed else "failed"

    progress = db.query(CourseModuleProgress).filter(
        CourseModuleProgress.course_id == attempt.course_id,
        CourseModuleProgress.module_id == attempt.module_id,
        CourseModuleProgress.student_id == attempt.student_id,
    ).first()

    if progress is None:
        progress = CourseModuleProgress(
            course_id=attempt.course_id,
            module_id=attempt.module_id,
            student_id=attempt.student_id,
        )
        db.add(progress)

    progress.score = final_score
    progress.is_completed = is_passed
    progress.status = "completed" if is_passed else "failed"
    progress.completed_at = datetime.utcnow() if is_passed else None

    # если модуль пройден — открываем следующий по position
    if is_passed:
        current_module = db.query(CourseModule).filter(
            CourseModule.id == attempt.module_id,
            CourseModule.course_id == attempt.course_id,
        ).first()

        if current_module is not None:
            next_module = db.query(CourseModule).filter(
                CourseModule.course_id == attempt.course_id,
                CourseModule.position > current_module.position,
            ).order_by(CourseModule.position).first()

            if next_module is not None:
                next_progress = db.query(CourseModuleProgress).filter(
                    CourseModuleProgress.course_id == attempt.course_id,
                    CourseModuleProgress.module_id == next_module.id,
                    CourseModuleProgress.student_id == attempt.student_id,
                ).first()

                if next_progress is None:
                    next_progress = CourseModuleProgress(
                        course_id=attempt.course_id,
                        module_id=next_module.id,
                        student_id=attempt.student_id,
                        status="available",
                        is_completed=False,
                    )
                    db.add(next_progress)
                elif next_progress.status == "locked":
                    next_progress.status = "available"

    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "course_id": attempt.course_id,
        "module_id": attempt.module_id,
        "student_id": attempt.student_id,
        "status": attempt.status,
        "pass_score": settings.pass_score,

        "final_score": final_score,
        "is_passed": is_passed,
        "theory_score": theory_score,
        "practical_score": practical_score,
        "correct_count": correct_count,
        "total_questions": total_questions,

        "weak_concepts": weak_concepts,
        "recommended_lectures": recommended_lectures,
        "recommended_materials": recommended_materials,

        "message": (
            "Тест пройден. Модуль завершён."
            if is_passed
            else "Тест не пройден. Рекомендуем повторить материал."
        ),
    }



@router.get(
    "/courses/{course_id}/modules/progress",
    response_model=list[CourseModuleProgressResponse],
)
def get_course_modules_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student_id = current_user.id

    if current_user.role == "teacher":
        raise HTTPException(
            status_code=400,
            detail="Use student-specific progress endpoint for teacher analytics"
        )

    return db.query(CourseModuleProgress).filter(
        CourseModuleProgress.course_id == course_id,
        CourseModuleProgress.student_id == student_id,
    ).all()


@router.get(
    "/courses/{course_id}/students/{student_id}/modules/progress",
    response_model=list[CourseModuleProgressResponse],
)
def get_student_course_modules_progress(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own courses"
        )

    return db.query(CourseModuleProgress).filter(
        CourseModuleProgress.course_id == course_id,
        CourseModuleProgress.student_id == student_id,
    ).all()


@router.post(
    "/courses/{course_id}/modules/{module_id}/progress",
    response_model=CourseModuleProgressResponse,
)
def create_module_progress(
    course_id: int,
    module_id: int,
    data: CourseModuleProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    existing = db.query(CourseModuleProgress).filter(
        CourseModuleProgress.course_id == course_id,
        CourseModuleProgress.module_id == module_id,
        CourseModuleProgress.student_id == data.student_id,
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Module progress already exists"
        )

    progress = CourseModuleProgress(
        course_id=course_id,
        module_id=module_id,
        student_id=data.student_id,
        status=data.status,
        score=data.score,
        is_completed=data.is_completed,
        completed_at=datetime.utcnow() if data.is_completed else None,
    )

    db.add(progress)
    db.commit()
    db.refresh(progress)

    return progress


@router.put(
    "/courses/{course_id}/modules/{module_id}/progress/{student_id}",
    response_model=CourseModuleProgressResponse,
)
def update_module_progress(
    course_id: int,
    module_id: int,
    student_id: int,
    data: CourseModuleProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    progress = db.query(CourseModuleProgress).filter(
        CourseModuleProgress.course_id == course_id,
        CourseModuleProgress.module_id == module_id,
        CourseModuleProgress.student_id == student_id,
    ).first()

    if progress is None:
        progress = CourseModuleProgress(
            course_id=course_id,
            module_id=module_id,
            student_id=student_id,
        )
        db.add(progress)

    progress.status = data.status
    progress.score = data.score
    progress.is_completed = data.is_completed
    progress.completed_at = datetime.utcnow() if data.is_completed else None

    db.commit()
    db.refresh(progress)

    return progress



@router.get(
    "/courses/{course_id}/practical-bank",
    response_model=list[CoursePracticalTaskResponse],
)
def get_course_practical_bank(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own courses"
        )

    return db.query(CoursePracticalTask).filter(
        CoursePracticalTask.course_id == course_id
    ).order_by(CoursePracticalTask.id.desc()).all()


@router.post(
    "/courses/{course_id}/practical-bank",
    response_model=CoursePracticalTaskResponse,
)
def create_course_practical_task(
    course_id: int,
    data: CoursePracticalTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    task = CoursePracticalTask(
        course_id=course_id,
        title=data.title,
        description=data.description,
        task_type=data.task_type,
        difficulty=data.difficulty,
        starter_code=data.starter_code,
        tests_code=data.tests_code,
        max_score=data.max_score,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.put(
    "/courses/{course_id}/practical-bank/{task_id}",
    response_model=CoursePracticalTaskResponse,
)
def update_course_practical_task(
    course_id: int,
    task_id: int,
    data: CoursePracticalTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    task = db.query(CoursePracticalTask).filter(
        CoursePracticalTask.id == task_id,
        CoursePracticalTask.course_id == course_id,
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Practical task not found"
        )

    task.title = data.title
    task.description = data.description
    task.task_type = data.task_type
    task.difficulty = data.difficulty
    task.starter_code = data.starter_code
    task.tests_code = data.tests_code
    task.max_score = data.max_score

    db.commit()
    db.refresh(task)

    return task


@router.delete("/courses/{course_id}/practical-bank/{task_id}")
def delete_course_practical_task(
    course_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    task = db.query(CoursePracticalTask).filter(
        CoursePracticalTask.id == task_id,
        CoursePracticalTask.course_id == course_id,
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Practical task not found"
        )

    db.query(CoursePracticalConcept).filter(
        CoursePracticalConcept.task_id == task_id
    ).delete(synchronize_session=False)

    db.delete(task)
    db.commit()

    return {
        "message": "Practical task deleted"
    }

@router.get(
    "/practical-bank/{task_id}/concepts",
    response_model=list[CoursePracticalConceptResponse],
)
def get_practical_task_concepts(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(CoursePracticalTask).filter(
        CoursePracticalTask.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Practical task not found"
        )

    rows = (
        db.query(CoursePracticalConcept, OntologyEntity)
        .join(OntologyEntity, OntologyEntity.id == CoursePracticalConcept.entity_id)
        .filter(CoursePracticalConcept.task_id == task_id)
        .order_by(OntologyEntity.name)
        .all()
    )

    return [
        {
            "id": link.id,
            "task_id": link.task_id,
            "entity_id": link.entity_id,
            "entity_name": entity.name,
            "entity_type": entity.entity_type,
        }
        for link, entity in rows
    ]


@router.post(
    "/practical-bank/{task_id}/concepts",
    response_model=CoursePracticalConceptResponse,
)
def add_concept_to_practical_task(
    task_id: int,
    data: CoursePracticalConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    task = db.query(CoursePracticalTask).filter(
        CoursePracticalTask.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Practical task not found"
        )

    course = db.query(Course).filter(
        Course.id == task.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    entity = db.query(OntologyEntity).filter(
        OntologyEntity.id == data.entity_id,
        OntologyEntity.course_id == task.course_id,
    ).first()

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail="Ontology entity not found in this course"
        )

    existing = db.query(CoursePracticalConcept).filter(
        CoursePracticalConcept.task_id == task_id,
        CoursePracticalConcept.entity_id == data.entity_id,
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Concept already linked to this practical task"
        )

    link = CoursePracticalConcept(
        task_id=task_id,
        entity_id=data.entity_id,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return {
        "id": link.id,
        "task_id": link.task_id,
        "entity_id": link.entity_id,
        "entity_name": entity.name,
        "entity_type": entity.entity_type,
    }


@router.delete("/practical-bank/{task_id}/concepts/{entity_id}")
def remove_concept_from_practical_task(
    task_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    task = db.query(CoursePracticalTask).filter(
        CoursePracticalTask.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Practical task not found"
        )

    course = db.query(Course).filter(
        Course.id == task.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    link = db.query(CoursePracticalConcept).filter(
        CoursePracticalConcept.task_id == task_id,
        CoursePracticalConcept.entity_id == entity_id,
    ).first()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Practical concept link not found"
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Concept removed from practical task"
    }

@router.get(
    "/courses/{course_id}/question-bank",
    response_model=list[QuestionBankItemResponse],
)
def get_course_question_bank(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own courses"
        )

    return db.query(QuestionBankItem).filter(
        QuestionBankItem.course_id == course_id
    ).order_by(QuestionBankItem.id.desc()).all()


@router.post(
    "/courses/{course_id}/question-bank",
    response_model=QuestionBankItemResponse,
)
def create_course_question_bank_item(
    course_id: int,
    data: QuestionBankItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    item = QuestionBankItem(
        course_id=course_id,
        question_text=data.question_text,
        question_type=data.question_type,
        difficulty=data.difficulty,
        explanation=data.explanation,
        correct_answer=data.correct_answer,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@router.put(
    "/courses/{course_id}/question-bank/{question_id}",
    response_model=QuestionBankItemResponse,
)
def update_course_question_bank_item(
    course_id: int,
    question_id: int,
    data: QuestionBankItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    item = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id,
        QuestionBankItem.course_id == course_id,
    ).first()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    item.question_text = data.question_text
    item.question_type = data.question_type
    item.difficulty = data.difficulty
    item.explanation = data.explanation
    item.correct_answer = data.correct_answer

    db.commit()
    db.refresh(item)

    return item


@router.delete("/courses/{course_id}/question-bank/{question_id}")
def delete_course_question_bank_item(
    course_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    item = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id,
        QuestionBankItem.course_id == course_id,
    ).first()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    db.query(QuestionBankConcept).filter(
        QuestionBankConcept.question_id == question_id
    ).delete(synchronize_session=False)
    db.query(QuestionBankOption).filter(
        QuestionBankOption.question_id == question_id
    ).delete(synchronize_session=False)

    db.delete(item)
    db.commit()

    return {
        "message": "Question bank item deleted"
    }

@router.get(
    "/question-bank/{question_id}/concepts",
    response_model=list[QuestionBankConceptResponse],
)
def get_question_bank_concepts(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id
    ).first()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    rows = (
        db.query(QuestionBankConcept, OntologyEntity)
        .join(OntologyEntity, OntologyEntity.id == QuestionBankConcept.entity_id)
        .filter(QuestionBankConcept.question_id == question_id)
        .order_by(OntologyEntity.name)
        .all()
    )

    return [
        {
            "id": link.id,
            "question_id": link.question_id,
            "entity_id": link.entity_id,
            "entity_name": entity.name,
            "entity_type": entity.entity_type,
        }
        for link, entity in rows
    ]


@router.post(
    "/question-bank/{question_id}/concepts",
    response_model=QuestionBankConceptResponse,
)
def add_concept_to_question_bank_item(
    question_id: int,
    data: QuestionBankConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    item = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id
    ).first()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    course = db.query(Course).filter(
        Course.id == item.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    entity = db.query(OntologyEntity).filter(
        OntologyEntity.id == data.entity_id,
        OntologyEntity.course_id == item.course_id,
    ).first()

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail="Ontology entity not found in this course"
        )

    existing = db.query(QuestionBankConcept).filter(
        QuestionBankConcept.question_id == question_id,
        QuestionBankConcept.entity_id == data.entity_id,
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Concept already linked to this question"
        )

    link = QuestionBankConcept(
        question_id=question_id,
        entity_id=data.entity_id,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return {
        "id": link.id,
        "question_id": link.question_id,
        "entity_id": link.entity_id,
        "entity_name": entity.name,
        "entity_type": entity.entity_type,
    }


@router.delete("/question-bank/{question_id}/concepts/{entity_id}")
def remove_concept_from_question_bank_item(
    question_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    item = db.query(QuestionBankItem).filter(
        QuestionBankItem.id == question_id
    ).first()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Question bank item not found"
        )

    course = db.query(Course).filter(
        Course.id == item.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    link = db.query(QuestionBankConcept).filter(
        QuestionBankConcept.question_id == question_id,
        QuestionBankConcept.entity_id == entity_id,
    ).first()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Question concept link not found"
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Concept removed from question"
    }

@router.get(
    "/courses/{course_id}/modules/{module_id}/test-settings",
    response_model=ModuleTestSettingResponse,
)
def get_module_test_settings(
    course_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    setting = db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == module_id
    ).first()

    if setting is None:
        raise HTTPException(
            status_code=404,
            detail="Module test settings not found"
        )

    return setting


@router.post(
    "/courses/{course_id}/modules/{module_id}/test-settings",
    response_model=ModuleTestSettingResponse,
)
def create_module_test_settings(
    course_id: int,
    module_id: int,
    data: ModuleTestSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    existing = db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == module_id
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Test settings for this module already exist"
        )

    setting = ModuleTestSetting(
        module_id=module_id,
        pass_score=data.pass_score,
        question_count=data.question_count,
        practical_count=data.practical_count,
        beginner_count=data.beginner_count,
        intermediate_count=data.intermediate_count,
        advanced_count=data.advanced_count,
    )

    db.add(setting)
    db.commit()
    db.refresh(setting)

    return setting


@router.put(
    "/courses/{course_id}/modules/{module_id}/test-settings",
    response_model=ModuleTestSettingResponse,
)
def update_module_test_settings(
    course_id: int,
    module_id: int,
    data: ModuleTestSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    setting = db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == module_id
    ).first()

    if setting is None:
        setting = ModuleTestSetting(module_id=module_id)
        db.add(setting)

    setting.pass_score = data.pass_score
    setting.question_count = data.question_count
    setting.practical_count = data.practical_count
    setting.beginner_count = data.beginner_count
    setting.intermediate_count = data.intermediate_count
    setting.advanced_count = data.advanced_count

    db.commit()
    db.refresh(setting)

    return setting


@router.delete("/courses/{course_id}/modules/{module_id}/test-settings")
def delete_module_test_settings(
    course_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    setting = db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == module_id
    ).first()

    if setting is None:
        raise HTTPException(
            status_code=404,
            detail="Module test settings not found"
        )

    db.delete(setting)
    db.commit()

    return {
        "message": "Module test settings deleted"
    }


@router.get(
    "/lectures/{lecture_id}/concepts",
    response_model=list[LectureConceptResponse],
)
def get_lecture_concepts(
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Course lecture not found"
        )

    rows = (
        db.query(LectureConcept, OntologyEntity)
        .join(OntologyEntity, OntologyEntity.id == LectureConcept.entity_id)
        .filter(LectureConcept.lecture_id == lecture_id)
        .order_by(OntologyEntity.name)
        .all()
    )

    return [
        {
            "id": link.id,
            "lecture_id": link.lecture_id,
            "entity_id": link.entity_id,
            "entity_name": entity.name,
            "entity_type": entity.entity_type,
        }
        for link, entity in rows
    ]


@router.post(
    "/lectures/{lecture_id}/concepts",
    response_model=LectureConceptResponse,
)
def add_concept_to_lecture(
    lecture_id: int,
    data: LectureConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Course lecture not found"
        )

    course = db.query(Course).filter(
        Course.id == lecture.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    entity = db.query(OntologyEntity).filter(
        OntologyEntity.id == data.entity_id,
        OntologyEntity.course_id == lecture.course_id,
    ).first()

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail="Ontology entity not found in this course"
        )

    existing = db.query(LectureConcept).filter(
        LectureConcept.lecture_id == lecture_id,
        LectureConcept.entity_id == data.entity_id,
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Concept already linked to this lecture"
        )

    link = LectureConcept(
        lecture_id=lecture_id,
        entity_id=data.entity_id,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return {
        "id": link.id,
        "lecture_id": link.lecture_id,
        "entity_id": link.entity_id,
        "entity_name": entity.name,
        "entity_type": entity.entity_type,
    }


@router.delete("/lectures/{lecture_id}/concepts/{entity_id}")
def remove_concept_from_lecture(
    lecture_id: int,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id
    ).first()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Course lecture not found"
        )

    course = db.query(Course).filter(
        Course.id == lecture.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    link = db.query(LectureConcept).filter(
        LectureConcept.lecture_id == lecture_id,
        LectureConcept.entity_id == entity_id,
    ).first()

    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture concept link not found"
        )

    db.delete(link)
    db.commit()

    return {
        "message": "Concept removed from lecture"
    }




@router.get(
    "/courses/{course_id}/modules/{module_id}/lectures",
    response_model=list[CourseLectureResponse],
)
def get_module_lectures(
    course_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(status_code=404, detail="Course module not found")

    return db.query(CourseLecture).filter(
        CourseLecture.course_id == course_id,
        CourseLecture.module_id == module_id,
    ).order_by(CourseLecture.position).all()


@router.post(
    "/courses/{course_id}/modules/{module_id}/lectures",
    response_model=CourseLectureResponse,
)
def create_module_lecture(
    course_id: int,
    module_id: int,
    data: CourseLectureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own courses")

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id,
    ).first()

    if module is None:
        raise HTTPException(status_code=404, detail="Course module not found")

    lecture = CourseLecture(
        course_id=course_id,
        module_id=module_id,
        title=data.title,
        content=data.content,
        image_url=data.image_url,
        position=data.position,
        is_published=data.is_published,
    )

    db.add(lecture)
    db.commit()
    db.refresh(lecture)

    return lecture


@router.put(
    "/courses/{course_id}/modules/{module_id}/lectures/{lecture_id}",
    response_model=CourseLectureResponse,
)
def update_module_lecture(
    course_id: int,
    module_id: int,
    lecture_id: int,
    data: CourseLectureUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own courses")

    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id,
        CourseLecture.course_id == course_id,
        CourseLecture.module_id == module_id,
    ).first()

    if lecture is None:
        raise HTTPException(status_code=404, detail="Course lecture not found")

    lecture.title = data.title
    lecture.content = data.content
    lecture.image_url = data.image_url
    lecture.position = data.position
    lecture.is_published = data.is_published

    db.commit()
    db.refresh(lecture)

    return lecture


@router.delete("/courses/{course_id}/modules/{module_id}/lectures/{lecture_id}")
def delete_module_lecture(
    course_id: int,
    module_id: int,
    lecture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own courses")

    lecture = db.query(CourseLecture).filter(
        CourseLecture.id == lecture_id,
        CourseLecture.course_id == course_id,
        CourseLecture.module_id == module_id,
    ).first()

    if lecture is None:
        raise HTTPException(status_code=404, detail="Course lecture not found")
    db.query(LectureBlock).filter(
        LectureBlock.lecture_id == lecture_id
    ).delete(synchronize_session=False)


    db.delete(lecture)
    db.commit()

    return {"message": "Course lecture deleted"}




@router.post("/concepts", response_model=OntologyConceptResponse)
def create_concept(
    concept: OntologyConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    existing_concept = db.query(OntologyConcept).filter(
        OntologyConcept.name == concept.name
    ).first()

    if existing_concept is not None:
        raise HTTPException(
            status_code=400,
            detail="Concept with this name already exists",
        )

    new_concept = OntologyConcept(
        name=concept.name,
        description=concept.description,
        concept_type=concept.concept_type,
        difficulty_level=concept.difficulty_level,
    )

    db.add(new_concept)
    db.commit()
    db.refresh(new_concept)

    return new_concept


@router.get("/concepts", response_model=list[OntologyConceptResponse])
def get_concepts(db: Session = Depends(get_db)):
    return db.query(OntologyConcept).all()


@router.post("/relations", response_model=OntologyRelationResponse)
def create_relation(
    relation: OntologyRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    source = db.query(OntologyConcept).filter(
        OntologyConcept.id == relation.source_concept_id
    ).first()

    target = db.query(OntologyConcept).filter(
        OntologyConcept.id == relation.target_concept_id
    ).first()

    if source is None or target is None:
        raise HTTPException(
            status_code=404,
            detail="Source or target concept not found",
        )

    new_relation = OntologyRelation(
        source_concept_id=relation.source_concept_id,
        target_concept_id=relation.target_concept_id,
        relation_type=relation.relation_type,
    )

    db.add(new_relation)
    db.commit()
    db.refresh(new_relation)

    return new_relation


@router.get("/relations", response_model=list[OntologyRelationResponse])
def get_relations(db: Session = Depends(get_db)):
    return db.query(OntologyRelation).all()


@router.post("/question-concepts", response_model=QuestionConceptResponse)
def link_question_to_concept(
    link: QuestionConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    question = db.query(Question).filter(
        Question.id == link.question_id
    ).first()

    concept = db.query(OntologyConcept).filter(
        OntologyConcept.id == link.concept_id
    ).first()

    if question is None or concept is None:
        raise HTTPException(
            status_code=404,
            detail="Question or concept not found",
        )

    new_link = QuestionConcept(
        question_id=link.question_id,
        concept_id=link.concept_id,
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    return new_link


@router.get(
    "/questions/{question_id}/concepts",
    response_model=list[OntologyConceptResponse],
)
def get_question_concepts(
    question_id: int,
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(
        Question.id == question_id
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    links = db.query(QuestionConcept).filter(
        QuestionConcept.question_id == question_id
    ).all()

    concept_ids = [link.concept_id for link in links]

    if not concept_ids:
        return []

    return db.query(OntologyConcept).filter(
        OntologyConcept.id.in_(concept_ids)
    ).all()


@router.get("/questions/{question_id}/analysis")
def analyze_question_concepts(
    question_id: int,
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(
        Question.id == question_id
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    question_links = db.query(QuestionConcept).filter(
        QuestionConcept.question_id == question_id
    ).all()

    concept_ids = [link.concept_id for link in question_links]

    if len(concept_ids) == 0:
        return {
            "question_id": question_id,
            "question_text": question.question_text,
            "checked_concepts": [],
            "related_concepts": [],
            "relations": [],
        }

    concepts = db.query(OntologyConcept).filter(
        OntologyConcept.id.in_(concept_ids)
    ).all()

    related_relations = db.query(OntologyRelation).filter(
        OntologyRelation.source_concept_id.in_(concept_ids)
    ).all()

    related_concept_ids = [
        relation.target_concept_id for relation in related_relations
    ]

    related_concepts = db.query(OntologyConcept).filter(
        OntologyConcept.id.in_(related_concept_ids)
    ).all()

    return {
        "question_id": question_id,
        "question_text": question.question_text,
        "checked_concepts": [
            {
                "id": concept.id,
                "name": concept.name,
                "type": concept.concept_type,
                "difficulty_level": concept.difficulty_level,
            }
            for concept in concepts
        ],
        "related_concepts": [
            {
                "id": concept.id,
                "name": concept.name,
                "type": concept.concept_type,
                "difficulty_level": concept.difficulty_level,
            }
            for concept in related_concepts
        ],
        "relations": [
            {
                "source_concept_id": relation.source_concept_id,
                "target_concept_id": relation.target_concept_id,
                "relation_type": relation.relation_type,
            }
            for relation in related_relations
        ],
    }


@router.post("/material-concepts", response_model=MaterialConceptResponse)
def link_material_to_concept(
    link: MaterialConceptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    material = db.query(Material).filter(
        Material.id == link.material_id
    ).first()

    concept = db.query(OntologyConcept).filter(
        OntologyConcept.id == link.concept_id
    ).first()

    if material is None or concept is None:
        raise HTTPException(
            status_code=404,
            detail="Material or concept not found",
        )

    new_link = MaterialConcept(
        material_id=link.material_id,
        concept_id=link.concept_id,
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    return new_link


@router.get("/concepts/{concept_id}/materials")
def get_concept_materials(
    concept_id: int,
    db: Session = Depends(get_db),
):
    concept = db.query(OntologyConcept).filter(
        OntologyConcept.id == concept_id
    ).first()

    if concept is None:
        raise HTTPException(
            status_code=404,
            detail="Concept not found",
        )

    links = db.query(MaterialConcept).filter(
        MaterialConcept.concept_id == concept_id
    ).all()

    material_ids = [link.material_id for link in links]

    if len(material_ids) == 0:
        return []

    materials = db.query(Material).filter(
        Material.id.in_(material_ids)
    ).all()

    return [
        {
            "id": material.id,
            "topic_id": material.topic_id,
            "title": material.title,
            "content": material.content,
            "material_type": material.material_type,
            "source_url": material.source_url,
            "status": material.status,
        }
        for material in materials
    ]


@router.get("/graph")
def get_ontology_graph(
    course_id: int | None = None,
    db: Session = Depends(get_db),
):
    entities_query = db.query(OntologyEntity)

    if course_id is not None:
        entities_query = entities_query.filter(
            OntologyEntity.course_id == course_id
        )

    entities = entities_query.all()
    entity_ids = [entity.id for entity in entities]

    relations_query = db.query(OntologyGraphRelation)

    if course_id is not None:
        relations_query = relations_query.filter(
            OntologyGraphRelation.course_id == course_id
        )

    relations = relations_query.all()

    if course_id is not None:
        relations = [
            relation
            for relation in relations
            if relation.source_entity_id in entity_ids
            and relation.target_entity_id in entity_ids
        ]

    nodes = [
        {
            "id": entity.id,
            "label": entity.name,
            "type": entity.entity_type,
            "description": entity.description,
            "course_id": entity.course_id,
        }
        for entity in entities
    ]

    edges = [
        {
            "id": relation.id,
            "source": relation.source_entity_id,
            "target": relation.target_entity_id,
            "label": relation.relation_type,
            "course_id": relation.course_id,
        }
        for relation in relations
    ]

    return {
        "nodes": nodes,
        "edges": edges,
    }


@router.post("/entities", response_model=OntologyEntityResponse)
def create_ontology_entity(
    data: OntologyEntityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    if data.course_id is not None:
        course = db.query(Course).filter(
            Course.id == data.course_id
        ).first()

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found",
            )

    entity = OntologyEntity(
        name=data.name,
        entity_type=data.entity_type,
        description=data.description,
        course_id=data.course_id,
    )

    db.add(entity)
    db.commit()
    db.refresh(entity)

    return entity


@router.put("/entities/{entity_id}", response_model=OntologyEntityResponse)
def update_ontology_entity(
    entity_id: int,
    data: OntologyEntityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    entity = db.query(OntologyEntity).filter(
        OntologyEntity.id == entity_id
    ).first()

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail="Ontology entity not found",
        )

    if data.course_id is not None:
        course = db.query(Course).filter(
            Course.id == data.course_id
        ).first()

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found",
            )

    entity.name = data.name
    entity.entity_type = data.entity_type
    entity.description = data.description
    entity.course_id = data.course_id

    db.commit()
    db.refresh(entity)

    return entity


@router.delete("/entities/{entity_id}")
def delete_ontology_entity(
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    entity = db.query(OntologyEntity).filter(
        OntologyEntity.id == entity_id
    ).first()

    if entity is None:
        raise HTTPException(
            status_code=404,
            detail="Ontology entity not found",
        )

    db.query(OntologyGraphRelation).filter(
        (OntologyGraphRelation.source_entity_id == entity_id)
        | (OntologyGraphRelation.target_entity_id == entity_id)
    ).delete(synchronize_session=False)

    db.delete(entity)
    db.commit()

    return {
        "message": "Ontology entity deleted",
    }


@router.post("/graph-relations", response_model=OntologyGraphRelationResponse)
def create_ontology_graph_relation(
    data: OntologyGraphRelationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    source = db.query(OntologyEntity).filter(
        OntologyEntity.id == data.source_entity_id
    ).first()

    target = db.query(OntologyEntity).filter(
        OntologyEntity.id == data.target_entity_id
    ).first()

    if source is None or target is None:
        raise HTTPException(
            status_code=404,
            detail="Source or target entity not found",
        )

    if data.course_id is not None:
        course = db.query(Course).filter(
            Course.id == data.course_id
        ).first()

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found",
            )

    if data.course_id is not None:
        if source.course_id != data.course_id or target.course_id != data.course_id:
            raise HTTPException(
                status_code=400,
                detail="Both entities must belong to the selected course",
            )

    relation = OntologyGraphRelation(
        source_entity_id=data.source_entity_id,
        target_entity_id=data.target_entity_id,
        relation_type=data.relation_type,
        course_id=data.course_id,
    )

    db.add(relation)
    db.commit()
    db.refresh(relation)

    return relation


@router.delete("/graph-relations/{relation_id}")
def delete_ontology_graph_relation(
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    relation = db.query(OntologyGraphRelation).filter(
        OntologyGraphRelation.id == relation_id
    ).first()

    if relation is None:
        raise HTTPException(
            status_code=404,
            detail="Ontology graph relation not found",
        )

    db.delete(relation)
    db.commit()

    return {
        "message": "Ontology graph relation deleted",
    }


@router.post("/courses", response_model=CourseResponse)
def create_course_from_ontology(
    data: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = Course(
        title=data.title,
        description=data.description,
        created_by=current_user.id,
        status="draft",
    )

    db.add(course)
    db.flush()

    root_entity = OntologyEntity(
        name=data.root_entity_name,
        entity_type=data.root_entity_type,
        course_id=course.id,
    )

    db.add(root_entity)
    db.flush()

    course.root_entity_id = root_entity.id

    db.commit()

    db.refresh(course)

    return course_to_response(course, db)


@router.get("/courses", response_model=list[CourseResponse])
def get_ontology_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "teacher":
        courses = db.query(Course).filter(
            Course.created_by == current_user.id
        ).order_by(Course.id.desc()).all()

    elif current_user.role == "student":
        course_links = db.query(CourseStudent).filter(
            CourseStudent.student_id == current_user.id,
            CourseStudent.status == "active",
        ).all()

        course_ids = [
            link.course_id
            for link in course_links
        ]

        if not course_ids:
            return []

        courses = db.query(Course).filter(
            Course.id.in_(course_ids),
            Course.status == "published",
        ).order_by(Course.id.desc()).all()

    else:
        courses = db.query(Course).order_by(Course.id.desc()).all()

    return [
        course_to_response(course, db)
        for course in courses
    ]

@router.post("/courses/{course_id}/publish", response_model=CourseResponse)
def publish_ontology_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can publish only your own courses"
        )

    modules_count = db.query(CourseModule).filter(
        CourseModule.course_id == course_id
    ).count()

    if modules_count == 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot publish course without modules"
        )

    course.status = "published"

    db.commit()
    db.refresh(course)

    return course_to_response(course, db)

@router.post("/courses/{course_id}/unpublish", response_model=CourseResponse)
def unpublish_ontology_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can unpublish only your own courses"
        )

    course.status = "draft"

    db.commit()
    db.refresh(course)

    return course_to_response(course, db)


@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_ontology_course(
    course_id: int,
    data: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    course.title = data.title
    course.description = data.description

    db.commit()
    db.refresh(course)

    return course_to_response(course, db)


@router.delete("/courses/{course_id}")
def delete_ontology_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own courses"
        )
    
    # Отвязываем root_entity от курса, чтобы избежать внешнего ключа
    course.root_entity_id = None
    db.flush()
    
    # 1. Удаляем связи графа курса
    db.query(OntologyGraphRelation).filter(
        OntologyGraphRelation.course_id == course_id
    ).delete(synchronize_session=False)

    # 2. Получаем entity_ids курса
    entity_ids = [
        entity.id
        for entity in db.query(OntologyEntity).filter(
            OntologyEntity.course_id == course_id
        ).all()
    ]

    # 3. Удаляем MaterialConcept по entity_ids
    if entity_ids:
        db.query(MaterialConcept).filter(
            MaterialConcept.concept_id.in_(entity_ids)
        ).delete(synchronize_session=False)

    # 4. Удаляем Material и MaterialConcept по material_ids
    material_ids = [
        material.id
        for material in db.query(Material).filter(
            Material.course_id == course_id
        ).all()
    ]

    if material_ids:
        db.query(MaterialConcept).filter(
            MaterialConcept.material_id.in_(material_ids)
        ).delete(synchronize_session=False)

    db.query(Material).filter(
        Material.course_id == course_id
    ).delete(synchronize_session=False)

    # 5. Удаляем профили автопоиска и кандидатов курса
    search_profile_ids = [
        profile.id
        for profile in db.query(MaterialSearchProfile).filter(
            MaterialSearchProfile.course_id == course_id
        ).all()
    ]

    if search_profile_ids:
        db.query(ExternalMaterialCandidate).filter(
            ExternalMaterialCandidate.search_profile_id.in_(search_profile_ids)
        ).delete(synchronize_session=False)

    db.query(MaterialSearchProfile).filter(
        MaterialSearchProfile.course_id == course_id
    ).delete(synchronize_session=False)

    # 6. Временно закомментировано - сущности онтологии курса
    # db.query(OntologyEntity).filter(
    #     OntologyEntity.course_id == course_id
    # ).delete(synchronize_session=False)

    # 7. Временно закомментировано - типы сущностей курса
    # db.query(OntologyEntityType).filter(
    #     OntologyEntityType.course_id == course_id
    # ).delete(synchronize_session=False)

    # 8. Удаляем прогресс модулей курса
    db.query(CourseModuleProgress).filter(
        CourseModuleProgress.course_id == course_id
    ).delete(synchronize_session=False)

    # 9. Удаляем попытки модульных тестов и связанные с ними вопросы и практики
    attempt_ids = [
        attempt.id
        for attempt in db.query(ModuleTestAttempt).filter(
            ModuleTestAttempt.course_id == course_id
        ).all()
    ]

    if attempt_ids:
        db.query(ModuleTestAttemptQuestion).filter(
            ModuleTestAttemptQuestion.attempt_id.in_(attempt_ids)
        ).delete(synchronize_session=False)

        db.query(ModuleTestAttemptPractical).filter(
            ModuleTestAttemptPractical.attempt_id.in_(attempt_ids)
        ).delete(synchronize_session=False)

    db.query(ModuleTestAttempt).filter(
        ModuleTestAttempt.course_id == course_id
    ).delete(synchronize_session=False)

    # 10. Получаем модули курса для каскадного удаления связанных данных
    module_ids = [
        module.id
        for module in db.query(CourseModule).filter(
            CourseModule.course_id == course_id
        ).all()
    ]

    if module_ids:
        # Удаляем концепты тестов модулей
        db.query(ModuleTestConcept).filter(
            ModuleTestConcept.module_id.in_(module_ids)
        ).delete(synchronize_session=False)

        # Удаляем настройки тестов модулей
        db.query(ModuleTestSetting).filter(
            ModuleTestSetting.module_id.in_(module_ids)
        ).delete(synchronize_session=False)

    # 11. Получаем лекции курса
    lecture_ids = [
        lecture.id
        for lecture in db.query(CourseLecture).filter(
            CourseLecture.course_id == course_id
        ).all()
    ]

    if lecture_ids:
        db.query(LectureConcept).filter(
            LectureConcept.lecture_id.in_(lecture_ids)
        ).delete(synchronize_session=False)
        db.query(LectureBlock).filter(
            LectureBlock.lecture_id.in_(lecture_ids)
        ).delete(synchronize_session=False)

    db.query(CourseLecture).filter(
        CourseLecture.course_id == course_id
    ).delete(synchronize_session=False)

    # 12. Практические задания и их концепты
    practical_task_ids = [
        task.id
        for task in db.query(CoursePracticalTask).filter(
            CoursePracticalTask.course_id == course_id
        ).all()
    ]

    if practical_task_ids:
        db.query(CoursePracticalConcept).filter(
            CoursePracticalConcept.task_id.in_(practical_task_ids)
        ).delete(synchronize_session=False)

    db.query(CoursePracticalTask).filter(
        CoursePracticalTask.course_id == course_id
    ).delete(synchronize_session=False)

    # 13. Вопросы банка и их концепты
    question_ids = [
        item.id
        for item in db.query(QuestionBankItem).filter(
            QuestionBankItem.course_id == course_id
        ).all()
    ]

    if question_ids:
        db.query(QuestionBankConcept).filter(
            QuestionBankConcept.question_id.in_(question_ids)
        ).delete(synchronize_session=False)

        db.query(QuestionBankOption).filter(
            QuestionBankOption.question_id.in_(question_ids)
        ).delete(synchronize_session=False)

    db.query(QuestionBankItem).filter(
        QuestionBankItem.course_id == course_id
    ).delete(synchronize_session=False)

    # 14. Удаляем сами модули
    db.query(CourseModule).filter(
        CourseModule.course_id == course_id
    ).delete(synchronize_session=False)

    # 15. Удаляем студентов курса
    db.query(CourseStudent).filter(
        CourseStudent.course_id == course_id
    ).delete(synchronize_session=False)

    # удаляем сущности онтологии в самом конце
    db.query(OntologyGraphRelation).filter(
        OntologyGraphRelation.course_id == course_id
    ).delete(synchronize_session=False)

    db.query(OntologyEntity).filter(
        OntologyEntity.course_id == course_id
    ).delete(synchronize_session=False)

    db.query(OntologyEntityType).filter(
        OntologyEntityType.course_id == course_id
    ).delete(synchronize_session=False)

    # 16. Удаляем сам курс
    db.delete(course)
    db.commit()

    return {
        "message": "Course and related ontology data deleted"
    }


@router.get("/courses/{course_id}/students", response_model=list[CourseStudentResponse])
def get_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own courses"
        )

    rows = (
        db.query(CourseStudent, User)
        .join(User, User.id == CourseStudent.student_id)
        .filter(CourseStudent.course_id == course_id)
        .order_by(User.username)
        .all()
    )

    return [
        {
            "id": link.id,
            "course_id": link.course_id,
            "student_id": link.student_id,
            "status": link.status,
            "username": user.username,
            "email": getattr(user, "email", None),
        }
        for link, user in rows
    ]


@router.post("/courses/{course_id}/students/by-username", response_model=CourseStudentResponse)
def add_student_to_course_by_username(
    course_id: int,
    data: CourseStudentAddByUsername,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    student = db.query(User).filter(
        User.username == data.username,
        User.role == "student"
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student with this username not found"
        )

    existing = db.query(CourseStudent).filter(
        CourseStudent.course_id == course_id,
        CourseStudent.student_id == student.id
    ).first()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Student already added to this course"
        )

    link = CourseStudent(
        course_id=course_id,
        student_id=student.id,
        status="active"
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


@router.post("/courses/{course_id}/students", response_model=CourseStudentResponse)
def add_student_to_course(
    course_id: int,
    data: CourseStudentAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own courses")

    student = db.query(User).filter(
        User.id == data.student_id,
        User.role == "student"
    ).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(CourseStudent).filter(
        CourseStudent.course_id == course_id,
        CourseStudent.student_id == data.student_id
    ).first()

    if existing is not None:
        raise HTTPException(status_code=400, detail="Student already added to this course")

    link = CourseStudent(
        course_id=course_id,
        student_id=data.student_id,
        status="active"
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


@router.delete("/courses/{course_id}/students/{student_id}")
def remove_student_from_course(
    course_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can edit only your own courses")

    link = db.query(CourseStudent).filter(
        CourseStudent.course_id == course_id,
        CourseStudent.student_id == student_id
    ).first()

    if link is None:
        raise HTTPException(status_code=404, detail="Student is not linked to this course")

    db.delete(link)
    db.commit()

    return {"message": "Student removed from course"}

@router.get("/courses/{course_id}/modules", response_model=list[CourseModuleResponse])
def get_course_modules(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can view only your own courses"
        )

    return db.query(CourseModule).filter(
        CourseModule.course_id == course_id
    ).order_by(CourseModule.position).all()


@router.post("/courses/{course_id}/modules", response_model=CourseModuleResponse)
def create_course_module(
    course_id: int,
    data: CourseModuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    module = CourseModule(
        course_id=course_id,
        title=data.title,
        description=data.description,
        position=data.position,
        is_published=data.is_published,
    )

    db.add(module)
    db.commit()
    db.refresh(module)

    return module


@router.put("/courses/{course_id}/modules/{module_id}", response_model=CourseModuleResponse)
def update_course_module(
    course_id: int,
    module_id: int,
    data: CourseModuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    module.title = data.title
    module.description = data.description
    module.position = data.position
    module.is_published = data.is_published

    db.commit()
    db.refresh(module)

    return module


@router.delete("/courses/{course_id}/modules/{module_id}")
def delete_course_module(
    course_id: int,
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    module = db.query(CourseModule).filter(
        CourseModule.id == module_id,
        CourseModule.course_id == course_id
    ).first()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Course module not found"
        )

    # 1. Удаляем попытки тестов этого модуля
    attempt_ids = [
        attempt.id
        for attempt in db.query(ModuleTestAttempt).filter(
            ModuleTestAttempt.module_id == module_id
        ).all()
    ]

    if attempt_ids:
        db.query(ModuleTestAttemptAnswer).filter(
            ModuleTestAttemptAnswer.attempt_id.in_(attempt_ids)
        ).delete(synchronize_session=False)

        db.query(ModuleTestAttemptQuestion).filter(
            ModuleTestAttemptQuestion.attempt_id.in_(attempt_ids)
        ).delete(synchronize_session=False)

        db.query(ModuleTestAttemptPractical).filter(
            ModuleTestAttemptPractical.attempt_id.in_(attempt_ids)
        ).delete(synchronize_session=False)

    db.query(ModuleTestAttempt).filter(
        ModuleTestAttempt.module_id == module_id
    ).delete(synchronize_session=False)

    # 2. Удаляем прогресс по модулю
    db.query(CourseModuleProgress).filter(
        CourseModuleProgress.module_id == module_id
    ).delete(synchronize_session=False)

    # 3. Удаляем настройки и концепты теста модуля
    db.query(ModuleTestConcept).filter(
        ModuleTestConcept.module_id == module_id
    ).delete(synchronize_session=False)

    db.query(ModuleTestSetting).filter(
        ModuleTestSetting.module_id == module_id
    ).delete(synchronize_session=False)

    # 4. Удаляем лекции модуля и всё, что с ними связано
    lecture_ids = [
        lecture.id
        for lecture in db.query(CourseLecture).filter(
            CourseLecture.module_id == module_id
        ).all()
    ]

    if lecture_ids:
        db.query(LectureConcept).filter(
            LectureConcept.lecture_id.in_(lecture_ids)
        ).delete(synchronize_session=False)

        db.query(LectureBlock).filter(
            LectureBlock.lecture_id.in_(lecture_ids)
        ).delete(synchronize_session=False)

        db.query(CourseLecture).filter(
            CourseLecture.id.in_(lecture_ids)
        ).delete(synchronize_session=False)

    # 5. Удаляем сам модуль
    db.delete(module)
    db.commit()

    return {
        "message": "Course module deleted"
    }


@router.post("/courses/{course_id}/materials")
def create_course_material(
    course_id: int,
    data: CourseMaterialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    course = db.query(Course).filter(Course.id == course_id).first()

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "teacher" and course.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can edit only your own courses"
        )

    concept = db.query(OntologyEntity).filter(
        OntologyEntity.id == data.concept_id,
        OntologyEntity.course_id == course_id,
    ).first()

    if concept is None:
        raise HTTPException(status_code=404, detail="Concept not found in course")

    material = Material(
        course_id=course_id,
        topic_id=None,
        title=data.title,
        content=data.description or "",
        description=data.description,
        material_type="manual",
        resource_type=data.resource_type,
        source_url=data.source_url,
        pdf_url=None,
        status="approved",
    )

    db.add(material)
    db.flush()

    db.add(
        MaterialConcept(
            material_id=material.id,
            concept_id=concept.id,
        )
    )

    db.commit()
    db.refresh(material)

    return {
        "id": material.id,
        "title": material.title,
        "description": material.description,
        "source_url": material.source_url,
        "resource_type": material.resource_type,
        "concept": {
            "id": concept.id,
            "name": concept.name,
            "type": concept.entity_type,
        },
    }


@router.get("/graph-svg")
def get_ontology_graph_svg(
    course_id: int | None = None,
    db: Session = Depends(get_db),
):
    graph_data = get_ontology_graph(course_id=course_id, db=db)

    dot = pydot.Dot(
        graph_type="digraph",
        rankdir="LR",
        bgcolor="white",
        fontname="Arial",
    )

    dot.set_node_defaults(
        shape="box",
        style="rounded,filled",
        fontname="Arial",
        fontsize="11",
        fillcolor="#f3f4f6",
        color="#94a3b8",
    )

    dot.set_edge_defaults(
        fontname="Arial",
        fontsize="9",
        color="#64748b",
        arrowsize="0.7",
    )

    type_colors = {
        "Architecture": "#fff7ed",
        "Method": "#f0fdf4",
        "Dataset": "#eff6ff",
        "Metric": "#fff7ed",
        "Loss": "#faf5ff",
        "Task": "#fff7ed",
        "Concept": "#fff7ed",
        "MainConcept": "#9f1239",
    }

    for node in graph_data["nodes"]:
        node_id = str(node["id"])
        label = node.get("label", node_id)
        node_type = node.get("type", "Unknown")

        fillcolor = type_colors.get(node_type, "#f3f4f6")
        fontcolor = "white" if node_type == "MainConcept" else "#111827"

        dot.add_node(
            pydot.Node(
                node_id,
                label=f"{label}\\n{node_type}",
                fillcolor=fillcolor,
                fontcolor=fontcolor,
                color="#9f1239" if node_type == "MainConcept" else "#94a3b8",
                penwidth="2",
            )
        )

    for edge in graph_data["edges"]:
        dot.add_edge(
            pydot.Edge(
                str(edge["source"]),
                str(edge["target"]),
                label=edge.get("label", ""),
            )
        )

    svg = dot.create_svg(prog="dot", encoding="utf8")

    return Response(
        content=svg,
        media_type="image/svg+xml",
    )


# ---------- Исправленные эндпоинты для Entity Types ----------
@router.get("/entity-types", response_model=list[OntologyEntityTypeResponse])
def get_ontology_entity_types(
    course_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(OntologyEntityType)

    if course_id is not None:
        query = query.filter(OntologyEntityType.course_id == course_id)

    return query.order_by(OntologyEntityType.id).all()


@router.post("/entity-types", response_model=OntologyEntityTypeResponse)
def create_ontology_entity_type(
    data: OntologyEntityTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    # Проверяем существование курса, если указан course_id
    if data.course_id is not None:
        course = db.query(Course).filter(
            Course.id == data.course_id
        ).first()
        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found"
            )

    # Проверка на дубликат с учётом course_id
    existing_type = db.query(OntologyEntityType).filter(
        OntologyEntityType.name == data.name,
        OntologyEntityType.course_id == data.course_id,
    ).first()
    if existing_type is not None:
        raise HTTPException(
            status_code=400,
            detail="Entity type with this name already exists in this course"
        )

    entity_type = OntologyEntityType(
        name=data.name,
        color=data.color,
        course_id=data.course_id,
    )
    db.add(entity_type)
    db.commit()
    db.refresh(entity_type)
    return entity_type


@router.put("/entity-types/{type_id}", response_model=OntologyEntityTypeResponse)
def update_ontology_entity_type(
    type_id: int,
    data: OntologyEntityTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    entity_type = db.query(OntologyEntityType).filter(
        OntologyEntityType.id == type_id
    ).first()
    if entity_type is None:
        raise HTTPException(
            status_code=404,
            detail="Entity type not found"
        )

    # Проверяем курс, если передан
    if data.course_id is not None:
        course = db.query(Course).filter(
            Course.id == data.course_id
        ).first()
        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found"
            )

    # Проверка на дубликат имени в рамках одного курса (исключая текущий)
    duplicate = db.query(OntologyEntityType).filter(
        OntologyEntityType.name == data.name,
        OntologyEntityType.course_id == data.course_id,
        OntologyEntityType.id != type_id,
    ).first()
    if duplicate is not None:
        raise HTTPException(
            status_code=400,
            detail="Entity type with this name already exists in this course"
        )

    entity_type.name = data.name
    entity_type.color = data.color
    entity_type.course_id = data.course_id

    db.commit()
    db.refresh(entity_type)
    return entity_type


@router.delete("/entity-types/{type_id}")
def delete_ontology_entity_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher_or_admin),
):
    entity_type = db.query(OntologyEntityType).filter(
        OntologyEntityType.id == type_id
    ).first()
    if entity_type is None:
        raise HTTPException(
            status_code=404,
            detail="Entity type not found",
        )

    # Проверка использования сущности в данном курсе
    used_count = db.query(OntologyEntity).filter(
        OntologyEntity.entity_type == entity_type.name,
        OntologyEntity.course_id == entity_type.course_id,
    ).count()
    if used_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete entity type because it is used by ontology entities",
        )

    db.delete(entity_type)
    db.commit()
    return {"message": "Ontology entity type deleted"}