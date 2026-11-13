from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


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


class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: IssueStatus | None = None
    priority: IssuePriority | None = None


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: IssueStatus
    priority: IssuePriority
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
