from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class IssuePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class IssueStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class IssueCreate(BaseModel):
    title: str
    description: str | None = None
    priority: IssuePriority = IssuePriority.medium


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: IssueStatus
    priority: IssuePriority
    created_at: datetime
    updated_at: datetime
