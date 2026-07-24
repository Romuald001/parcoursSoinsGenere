from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Appointment(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    label: str
    date: datetime
    location: str | None = None