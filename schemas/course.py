from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from schemas.enrollment import EnrollmentBrief


class CourseBase(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=2000)


class CourseCreate(CourseBase):
    """For creating a new course."""
    pass


class CourseUpdate(BaseModel):
    """Fields allowed to be updated on a course."""
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=2000)


class CourseResponse(BaseModel):
    """Standard course response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class CourseWithUsers(CourseResponse):
    """Course response with enrolled users list."""
    enrollments: list[EnrollmentBrief] = []
