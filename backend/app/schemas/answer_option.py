from pydantic import BaseModel


class AnswerOptionCreate(BaseModel):
    question_id: int
    option_text: str
    is_correct: bool = False


class AnswerOptionResponse(BaseModel):
    id: int
    question_id: int
    option_text: str
    is_correct: bool

    class Config:
        from_attributes = True