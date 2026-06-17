from pydantic import BaseModel


class TestCreate(BaseModel):
    topic_id: int
    title: str
    description: str | None = None
    difficulty_level: str


class TestResponse(BaseModel):
    id: int
    topic_id: int
    title: str
    description: str | None
    difficulty_level: str

    class Config:
        from_attributes = True