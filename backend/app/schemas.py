from enum import Enum

from pydantic import BaseModel


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

