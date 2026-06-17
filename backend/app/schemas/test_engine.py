from pydantic import BaseModel


class TestStartResponseOption(BaseModel):
    id: int
    option_text: str

    class Config:
        from_attributes = True


class TestStartResponseQuestion(BaseModel):
    id: int
    question_text: str
    question_type: str
    difficulty_level: str
    weight: int
    options: list[TestStartResponseOption]


class TestStartResponse(BaseModel):
    attempt_id: int
    test_id: int
    questions: list[TestStartResponseQuestion]


class SubmittedAnswer(BaseModel):
    question_id: int
    selected_option_ids: list[int]


class TestSubmitRequest(BaseModel):
    answers: list[SubmittedAnswer]


class TestSubmitResponse(BaseModel):
    attempt_id: int
    score: float
    is_passed: bool
    correct_answers: int
    total_questions: int
    total_weight: int
    earned_weight: int
    beginner_score: float
    intermediate_score: float
    advanced_score: float
    review_score: float
    weak_concepts: list[dict]
    recommended_concepts: list[dict]
    recommended_materials: list[dict]