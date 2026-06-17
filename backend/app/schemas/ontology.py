from pydantic import BaseModel


class OntologyConceptCreate(BaseModel):
    name: str
    description: str | None = None
    concept_type: str
    difficulty_level: str


class OntologyConceptResponse(BaseModel):
    id: int
    name: str
    description: str | None
    concept_type: str
    difficulty_level: str

    class Config:
        from_attributes = True


class OntologyRelationCreate(BaseModel):
    source_concept_id: int
    target_concept_id: int
    relation_type: str


class OntologyRelationResponse(BaseModel):
    id: int
    source_concept_id: int
    target_concept_id: int
    relation_type: str

    class Config:
        from_attributes = True


class QuestionConceptCreate(BaseModel):
    question_id: int
    concept_id: int


class QuestionConceptResponse(BaseModel):
    id: int
    question_id: int
    concept_id: int

    class Config:
        from_attributes = True

class MaterialConceptCreate(BaseModel):
    material_id: int
    concept_id: int


class MaterialConceptResponse(BaseModel):
    id: int
    material_id: int
    concept_id: int

    class Config:
        from_attributes = True

class OntologyEntityCreate(BaseModel):
    name: str
    entity_type: str
    description: str | None = None
    course_id: int | None = None


class OntologyEntityUpdate(BaseModel):
    name: str
    entity_type: str
    description: str | None = None
    course_id: int | None = None

class OntologyEntityResponse(BaseModel):
    id: int
    name: str
    entity_type: str
    description: str | None = None
    course_id: int | None = None

    class Config:
        from_attributes = True



class OntologyGraphRelationCreate(BaseModel):
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    course_id: int | None = None


class OntologyGraphRelationResponse(BaseModel):
    id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    course_id: int | None = None

    class Config:
        from_attributes = True


class OntologyEntityTypeCreate(BaseModel):
    name: str
    color: str = "#94a3b8"
    course_id: int | None = None


class OntologyEntityTypeUpdate(BaseModel):
    name: str
    color: str = "#94a3b8"
    course_id: int | None = None



class OntologyEntityTypeResponse(BaseModel):
    id: int
    name: str
    color: str
    course_id: int | None = None

    class Config:
        from_attributes = True


class CourseCreate(BaseModel):
    title: str
    description: str | None = None

    root_entity_name: str
    root_entity_type: str = "Concept"


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    root_entity_id: int
    created_by: int
    status: str
    root_entity_name: str | None = None
    root_entity_type: str | None = None
    cover_url: str | None = None

    class Config:
        from_attributes = True

class CourseUpdate(BaseModel):
    title: str
    description: str | None = None


class CourseUpdate(BaseModel):
    title: str
    description: str | None = None


class CourseStudentAdd(BaseModel):
    student_id: int


class CourseStudentResponse(BaseModel):
    id: int
    course_id: int
    student_id: int
    status: str
    username: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True

class CourseStudentAddByUsername(BaseModel):
    username: str


class CourseModuleCreate(BaseModel):
    title: str
    description: str | None = None
    position: int = 1
    is_published: bool = False


class CourseModuleUpdate(BaseModel):
    title: str
    description: str | None = None
    position: int = 1
    is_published: bool = False


class CourseModuleResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None = None
    position: int
    is_published: bool

    class Config:
        from_attributes = True

class CourseLectureCreate(BaseModel):
    title: str
    content: str | None = None
    image_url: str | None = None
    position: int = 1
    is_published: bool = False


class CourseLectureUpdate(BaseModel):
    title: str
    content: str | None = None
    image_url: str | None = None
    position: int = 1
    is_published: bool = False


class CourseLectureResponse(BaseModel):
    id: int
    course_id: int
    module_id: int
    title: str
    content: str | None = None
    image_url: str | None = None
    position: int
    is_published: bool

    class Config:
        from_attributes = True


class LectureConceptCreate(BaseModel):
    entity_id: int


class LectureConceptResponse(BaseModel):
    id: int
    lecture_id: int
    entity_id: int
    entity_name: str | None = None
    entity_type: str | None = None

    class Config:
        from_attributes = True


class ModuleTestSettingCreate(BaseModel):
    pass_score: int = 70
    question_count: int = 10
    practical_count: int = 0
    beginner_count: int = 4
    intermediate_count: int = 4
    advanced_count: int = 2


class ModuleTestSettingUpdate(BaseModel):
    pass_score: int = 70
    question_count: int = 10
    practical_count: int = 0
    beginner_count: int = 4
    intermediate_count: int = 4
    advanced_count: int = 2


class ModuleTestSettingResponse(BaseModel):
    id: int
    module_id: int
    pass_score: int
    question_count: int
    practical_count: int
    beginner_count: int
    intermediate_count: int
    advanced_count: int

    class Config:
        from_attributes = True


class QuestionBankItemCreate(BaseModel):
    question_text: str
    question_type: str = "single_choice"
    difficulty: str = "beginner"
    explanation: str | None = None
    correct_answer: str | None = None


class QuestionBankItemUpdate(BaseModel):
    question_text: str
    question_type: str = "single_choice"
    difficulty: str = "beginner"
    explanation: str | None = None
    correct_answer: str | None = None


class QuestionBankItemResponse(BaseModel):
    id: int
    course_id: int
    question_text: str
    question_type: str
    difficulty: str
    explanation: str | None = None
    correct_answer: str | None = None

    class Config:
        from_attributes = True


class QuestionBankConceptCreate(BaseModel):
    entity_id: int


class QuestionBankConceptResponse(BaseModel):
    id: int
    question_id: int
    entity_id: int
    entity_name: str | None = None
    entity_type: str | None = None

    class Config:
        from_attributes = True


class CoursePracticalTaskCreate(BaseModel):
    title: str
    description: str | None = None
    task_type: str = "code"
    difficulty: str = "beginner"
    starter_code: str | None = None
    tests_code: str | None = None
    max_score: int = 100


class CoursePracticalTaskUpdate(BaseModel):
    title: str
    description: str | None = None
    task_type: str = "code"
    difficulty: str = "beginner"
    starter_code: str | None = None
    tests_code: str | None = None
    max_score: int = 100


class CoursePracticalTaskResponse(BaseModel):
    id: int
    course_id: int
    title: str
    description: str | None = None
    task_type: str
    difficulty: str
    starter_code: str | None = None
    tests_code: str | None = None
    max_score: int

    class Config:
        from_attributes = True


class CoursePracticalConceptCreate(BaseModel):
    entity_id: int


class CoursePracticalConceptResponse(BaseModel):
    id: int
    task_id: int
    entity_id: int
    entity_name: str | None = None
    entity_type: str | None = None

    class Config:
        from_attributes = True

class CourseModuleProgressCreate(BaseModel):
    student_id: int
    status: str = "available"
    score: int | None = None
    is_completed: bool = False


class CourseModuleProgressUpdate(BaseModel):
    status: str = "available"
    score: int | None = None
    is_completed: bool = False


class CourseModuleProgressResponse(BaseModel):
    id: int
    course_id: int
    module_id: int
    student_id: int
    status: str
    score: int | None = None
    is_completed: bool

    class Config:
        from_attributes = True

class ModuleTestConceptCreate(BaseModel):
    entity_id: int


class ModuleTestConceptResponse(BaseModel):
    id: int
    module_id: int
    entity_id: int
    entity_name: str | None = None
    entity_type: str | None = None

    class Config:
        from_attributes = True

class ModuleTestQuestionAnswerSubmit(BaseModel):
    question_id: int
    selected_answer: str | None = None


class ModuleTestPracticalResultSubmit(BaseModel):
    task_id: int
    submitted_code: str | None = None
    score: int = 0


class ModuleTestAttemptSubmit(BaseModel):
    question_answers: list[ModuleTestQuestionAnswerSubmit] = []
    practical_results: list[ModuleTestPracticalResultSubmit] = []


class ModuleTestAttemptSubmitResponse(BaseModel):
    attempt_id: int
    course_id: int
    module_id: int
    student_id: int
    theory_score: int
    practical_score: int
    final_score: int
    pass_score: int
    is_passed: bool
    status: str
    weak_concepts: list[dict] = []
    recommended_lectures: list[dict] = []
    recommended_materials: list[dict] = []


class QuestionBankOptionCreate(BaseModel):
    option_text: str
    is_correct: bool = False
    position: int = 1


class QuestionBankOptionUpdate(BaseModel):
    option_text: str
    is_correct: bool = False
    position: int = 1


class QuestionBankOptionResponse(BaseModel):
    id: int
    question_id: int
    option_text: str
    is_correct: bool
    position: int

    class Config:
        from_attributes = True

class LectureBlockCreate(BaseModel):
    block_type: str = "text"
    content: str | None = None
    image_url: str | None = None
    position: int = 1


class LectureBlockUpdate(BaseModel):
    block_type: str = "text"
    content: str | None = None
    image_url: str | None = None
    position: int = 1


class LectureBlockResponse(BaseModel):
    id: int
    lecture_id: int
    block_type: str
    content: str | None = None
    image_url: str | None = None
    position: int

    class Config:
        from_attributes = True

class CourseMaterialCreate(BaseModel):
    title: str
    description: str | None = None
    source_url: str
    resource_type: str = "article"
    concept_id: int