from datetime import date

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Task, User


router = APIRouter()


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.assigned_user_id == current_user.id).all()
    stats = {
        "total": len(tasks),
        "todo": sum(1 for task in tasks if task.status == "todo"),
        "in_progress": sum(1 for task in tasks if task.status == "in_progress"),
        "done": sum(1 for task in tasks if task.status == "done"),
        "overdue": sum(1 for task in tasks if task.status != "done" and task.due_date < date.today()),
    }
    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "current_user": current_user, "stats": stats, "tasks": tasks},
    )
