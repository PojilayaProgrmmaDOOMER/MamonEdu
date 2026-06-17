from pydantic import BaseModel


class PracticalTaskCreate(BaseModel):
    topic_id: int
    title: str
    description: str
    starter_code: str | None = None
    expected_function_name: str = "segment"
    evaluation_type: str = "iou"
    test_code: str | None = None
    max_score: float = 100

class PracticalTaskResponse(BaseModel):
    id: int
    topic_id: int
    title: str
    description: str
    starter_code: str | None
    expected_function_name: str
    evaluation_type: str
    test_code: str | None = None
    max_score: float
    class Config:
        from_attributes = True


class CodeSubmissionCreate(BaseModel):
    submitted_code: str


class CodeSubmissionResponse(BaseModel):
    id: int
    practical_task_id: int
    score: float
    evaluation_result: str | None
    status: str

    class Config:
        from_attributes = True

class PracticalTaskConceptCreate(BaseModel):
    practical_task_id: int
    concept_id: int

class WeakConceptResponse(BaseModel):
    id: int
    name: str
    difficulty_level: str


class RecommendedMaterialResponse(BaseModel):
    id: int
    title: str
    material_type: str
    source_url: str | None = None


class PracticalEvaluationResponse(BaseModel):
    id: int
    practical_task_id: int
    score: float
    evaluation_result: str
    status: str

    weak_concepts: list[WeakConceptResponse]
    recommended_materials: list[RecommendedMaterialResponse]