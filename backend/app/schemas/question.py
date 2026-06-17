from pydantic import BaseModel


class QuestionCreate(BaseModel):
    test_id: int
    question_text: str
    question_type: str
    difficulty_level: str
    weight: int
    explanation: str | None = None


class QuestionResponse(BaseModel):
    id: int
    test_id: int
    question_text: str
    question_type: str
    difficulty_level: str
    weight: int
    explanation: str | None
    is_active: bool

    class Config:
        from_attributes = True