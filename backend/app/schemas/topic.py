from pydantic import BaseModel


class TopicCreate(BaseModel):
    title: str
    description: str
    difficulty_level: str


class TopicUpdate(BaseModel):
    title: str
    description: str
    difficulty_level: str


class TopicResponse(BaseModel):
    id: int
    title: str
    description: str
    difficulty_level: str

    class Config:
        from_attributes = True