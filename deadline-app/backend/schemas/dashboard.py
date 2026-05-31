from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date
from uuid import UUID


class TaskCreate(BaseModel):
    content: str
    deadline: Optional[date] = None
    staff_names: list[str] = []
    source: str = "document"


class TaskUpdate(BaseModel):
    content: Optional[str] = None
    deadline: Optional[date] = None
    staff_names: Optional[list[str]] = None


class StaffSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    short_name: str
    full_name: Optional[str]
    pending_count: int
    overdue_count: int


class TaskSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    content: str
    deadline: Optional[date]
    days_remaining: Optional[int]
    urgency: str
    status: str
    is_recurring: bool
    source: str
    staff_names: list[str]


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    red_urgent: list[TaskSummary]
    red: list[TaskSummary]
    yellow: list[TaskSummary]
    green: list[TaskSummary]
    overdue: list[TaskSummary]
    summary: dict
