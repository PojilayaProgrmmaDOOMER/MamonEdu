from pydantic import BaseModel


class StudyGroupCreate(BaseModel):
    name: str


class StudyGroupResponse(BaseModel):
    id: int
    name: str
    teacher_id: int

    class Config:
        from_attributes = True


class AddStudentToGroupRequest(BaseModel):
    student_id: int