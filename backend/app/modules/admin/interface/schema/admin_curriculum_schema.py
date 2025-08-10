from typing import List, Optional
from pydantic import BaseModel, Field


class AdminListCurriculumsQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    items_per_page: int = Field(default=10, ge=1, le=100)
    owner_id: Optional[str] = None


class AdminUpdateCurriculumVisibilityBody(BaseModel):
    visibility: str = Field(..., pattern="^(PUBLIC|PRIVATE)$")


class AdminCurriculumItem(BaseModel):
    curriculum_id: str
    owner_id: str
    title: str
    visibility: str


class AdminGetCurriculumResponse(AdminCurriculumItem):
    pass


class AdminGetCurriculumsPageResponse(BaseModel):
    curriculums: List[AdminCurriculumItem]
    total_count: int
    page: int
    items_per_page: int
