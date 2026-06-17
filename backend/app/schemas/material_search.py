from pydantic import BaseModel


class MaterialSearchProfileCreate(BaseModel):
    name: str
    keywords: str
    source: str = "arxiv"
    required_keywords: str | None = None
    excluded_keywords: str | None = None
    course_id: int | None = None
    max_results: int = 10

class MaterialSearchProfileResponse(BaseModel):
    id: int
    teacher_id: int
    name: str
    keywords: str
    source: str
    is_active: bool
    required_keywords: str | None = None
    excluded_keywords: str | None = None
    course_id: int | None = None
    max_results: int
    class Config:
        from_attributes = True


class ExternalMaterialCandidateResponse(BaseModel):
    id: int
    search_profile_id: int
    title: str
    authors: str | None = None
    abstract: str | None = None
    source_url: str | None = None
    source: str
    status: str

    class Config:
        from_attributes = True

class ApproveMaterialCandidateRequest(BaseModel):
    topic_id: int | None = None
    course_id: int | None = None
    concept_id: int | None = None