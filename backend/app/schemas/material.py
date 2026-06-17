from pydantic import BaseModel


class MaterialCreate(BaseModel):
    topic_id: int
    title: str
    content: str
    material_type: str
    source_url: str | None = None


class MaterialUpdate(BaseModel):
    title: str
    content: str
    material_type: str
    source_url: str | None = None


class MaterialResponse(BaseModel):
    id: int
    topic_id: int
    title: str
    content: str
    material_type: str
    source_url: str | None
    status: str

    class Config:
        from_attributes = True

class MaterialConceptLinkCreate(BaseModel):
    concept_id: int