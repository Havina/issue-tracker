import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Issue, User
from app.schemas import (
    IssueCreate,
    IssueResponse, 
    IssueUpdate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

app = FastAPI()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    username = payload.get("sub")

    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = db.scalar(
        select(User).where(User.username == username)
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return user



@app.get("/")
def read_root():
    return {"message": "Issue Tracker API"}


@app.post("/issues", response_model=IssueResponse, status_code=201)
def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        priority=issue.priority.value,
    )

    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    return db_issue


@app.get("/issues", response_model=list[IssueResponse])
def get_issues(db: Session = Depends(get_db)):
    return db.query(Issue).all()


@app.get("/issues/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.get(Issue, issue_id)

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    return issue


@app.get("/users/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


@app.patch("/issues/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    update_data = issue_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value

        setattr(issue, field, value)

    db.commit()
    db.refresh(issue)

    return issue


@app.delete("/issues/{issue_id}", status_code=204)
def delete_issue(
    issue_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    issue = db.get(Issue, issue_id)

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(issue)
    db.commit()


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_username = db.scalar(
        select(User).where(User.username == user.username)
    )

    if existing_username is not None:
        raise HTTPException(
            status_code=409,
            detail="Username already registered",
        )

    existing_email = db.scalar(
        select(User).where(User.email == user.email)
    )

    if existing_email is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.scalar(
        select(User).where(User.username == user.username)
    )

    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    access_token = create_access_token(db_user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
