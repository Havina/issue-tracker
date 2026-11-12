from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Issue
from app.schemas import IssueCreate, IssueResponse, IssueUpdate

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Issue Tracker API"}


@app.post("/issues", response_model=IssueResponse, status_code=201)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
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


@app.patch("/issues/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
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
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.get(Issue, issue_id)

    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(issue)
    db.commit()
