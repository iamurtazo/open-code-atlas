from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EnrollmentBrief(BaseModel):
    """Lightweight enrollment info for nested responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    course_id: int
    enrolled_at: datetime
