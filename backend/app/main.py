from fastapi import FastAPI

from app.schemas import IssueCreate

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Issue Tracker API"}


@app.post("/issues")
def create_issue(issue: IssueCreate):
    return issue

