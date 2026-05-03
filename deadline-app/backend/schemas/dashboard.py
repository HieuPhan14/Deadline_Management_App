from pydantic import BaseModel
from typing import Optional
from datetime import date
from uuid import UUID

class StaffSummary(BaseModel):
    id: UUID
    short_name: str 
    full_name: Optional[str]
    pending_count: int 
    overdue_count: int 

class TaskSummary(BaseModel):
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
    red_urgent: list[TaskSummary]
    red: list[TaskSummary]
    yellow: list[TaskSummary]
    green: list[TaskSummary]
    overdue: list[TaskSummary]
    summary: dict