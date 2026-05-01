from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from auth import get_current_user
from database import get_db
from models import Task, User


router = APIRouter()


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = date.today()
    tasks = (
        db.query(Task)
        .options(selectinload(Task.project), selectinload(Task.assigned_user))
        .filter(Task.assigned_user_id == current_user.id)
        .all()
    )
    recent_tasks = [
        {
            "title": task.title,
            "project_name": task.project.name if task.project else "No project",
            "assigned_username": task.assigned_user.username if task.assigned_user else "Unassigned",
            "due_date": task.due_date,
            "status": task.status,
            "is_overdue": task.status != "done" and task.due_date < today,
        }
        for task in tasks[:10]
    ]
    total_count = len(tasks)
    todo_count = sum(1 for task in tasks if task.status == "todo")
    in_progress_count = sum(1 for task in tasks if task.status == "in_progress")
    done_count = sum(1 for task in tasks if task.status == "done")
    overdue_count = sum(1 for task in tasks if task.status != "done" and task.due_date < today)
    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "total_count": total_count,
            "todo_count": todo_count,
            "in_progress_count": in_progress_count,
            "done_count": done_count,
            "overdue_count": overdue_count,
            "recent_tasks": recent_tasks,
            "today": today,
        },
    )
