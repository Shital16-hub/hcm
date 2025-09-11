from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"
    status: Literal["pending", "in_progress", "completed"] = "pending"
    due_date: Optional[datetime] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class TaskManagerState(BaseModel):
    messages: List[dict]
    tasks: List[Task] = []
    current_task_id: Optional[str] = None
    last_action: Optional[str] = None
    user_intent: Optional[str] = None