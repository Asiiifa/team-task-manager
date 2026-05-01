from datetime import date

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import get_current_user, require_admin
from database import get_db
from models import Project, ProjectMember, Task, User


router = APIRouter(prefix="/tasks")
VALID_STATUSES = {"todo", "in_progress", "done"}


@router.get("")
def tasks_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        tasks = db.query(Task).order_by(Task.due_date.asc()).all()
        projects = db.query(Project).order_by(Project.name).all()
        users = db.query(User).order_by(User.username).all()
    else:
        tasks = (
            db.query(Task)
            .filter(Task.assigned_user_id == current_user.id)
            .order_by(Task.due_date.asc())
            .all()
        )
        projects = []
        users = []
    return request.app.state.templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "current_user": current_user,
            "tasks": tasks,
            "projects": projects,
            "users": users,
            "today": date.today(),
        },
    )


@router.post("")
def create_task(
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(...),
    project_id: int = Form(...),
    assigned_user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.get(Project, project_id) and _is_member(db, project_id, assigned_user_id):
        db.add(
            Task(
                title=title.strip(),
                description=description.strip(),
                due_date=date.fromisoformat(due_date),
                status="todo",
                project_id=project_id,
                assigned_user_id=assigned_user_id,
                created_by_id=current_user.id,
            )
        )
        db.commit()
    return RedirectResponse("/tasks", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{task_id}/status")
def update_task_status(
    task_id: int,
    status_value: str = Form(..., alias="status"),
    next_url: str = Form("/tasks"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if task and status_value in VALID_STATUSES:
        if current_user.role == "admin" or task.assigned_user_id == current_user.id:
            task.status = status_value
            db.commit()
    if not next_url.startswith("/"):
        next_url = "/tasks"
    return RedirectResponse(next_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{task_id}/delete")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    task = db.get(Task, task_id)
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse("/tasks", status_code=status.HTTP_303_SEE_OTHER)


def _is_member(db: Session, project_id: int, user_id: int) -> bool:
    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
        is not None
    )
