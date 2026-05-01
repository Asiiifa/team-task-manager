from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from auth import get_current_user, require_admin
from database import get_db
from models import Project, ProjectMember, Task, User


router = APIRouter(prefix="/projects")


@router.get("")
def projects_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        projects = db.query(Project).order_by(Project.created_at.desc()).all()
        users = db.query(User).order_by(User.username).all()
    else:
        projects = (
            db.query(Project)
            .join(ProjectMember)
            .filter(ProjectMember.user_id == current_user.id)
            .order_by(Project.created_at.desc())
            .all()
        )
        users = []
    return request.app.state.templates.TemplateResponse(
        "projects.html",
        {"request": request, "current_user": current_user, "projects": projects, "users": users},
    )


@router.post("")
def create_project(
    name: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    project = Project(name=name.strip(), description=description.strip(), owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    db.add(ProjectMember(project_id=project.id, user_id=current_user.id))
    db.commit()
    return RedirectResponse("/projects", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{project_id}")
def project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if not project:
        return RedirectResponse("/projects", status_code=status.HTTP_303_SEE_OTHER)
    if current_user.role != "admin" and not _is_member(db, project_id, current_user.id):
        return RedirectResponse("/projects", status_code=status.HTTP_303_SEE_OTHER)

    users = db.query(User).order_by(User.username).all() if current_user.role == "admin" else []
    return request.app.state.templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "current_user": current_user, "project": project, "users": users},
    )


@router.post("/{project_id}/members")
def add_member(
    project_id: int,
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.get(Project, project_id) and db.get(User, user_id):
        exists = (
            db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
            .first()
        )
        if not exists:
            db.add(ProjectMember(project_id=project_id, user_id=user_id))
            db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{project_id}/tasks")
def create_task_for_project(
    project_id: int,
    title: str = Form(...),
    description: str = Form(""),
    due_date: str = Form(...),
    assigned_user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    from datetime import date

    if db.get(Project, project_id) and _is_member(db, project_id, assigned_user_id):
        task = Task(
            title=title.strip(),
            description=description.strip(),
            due_date=date.fromisoformat(due_date),
            status="todo",
            project_id=project_id,
            assigned_user_id=assigned_user_id,
            created_by_id=current_user.id,
        )
        db.add(task)
        db.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=status.HTTP_303_SEE_OTHER)


def _is_member(db: Session, project_id: int, user_id: int) -> bool:
    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
        is not None
    )
