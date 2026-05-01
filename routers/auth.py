from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import authenticate_user, clear_auth_cookie, create_access_token, get_password_hash, set_auth_cookie
from database import get_db
from models import User


router = APIRouter()


def render_auth_template(request: Request, template_name: str, context: dict | None = None, status_code: int = 200):
    template_context = {"request": request, "current_user": None}
    if context:
        template_context.update(context)

    try:
        return request.app.state.templates.TemplateResponse(
            request=request,
            name=template_name,
            context=template_context,
            status_code=status_code,
        )
    except TypeError:
        return request.app.state.templates.TemplateResponse(
            template_name,
            template_context,
            status_code=status_code,
        )


@router.get("/signup")
def signup_page(request: Request):
    return render_auth_template(request, "signup.html", {"error": None, "form": None})


@router.post("/signup")
def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("member"),
    db: Session = Depends(get_db),
):
    role = "admin" if role == "admin" else "member"
    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        hashed_password=get_password_hash(password),
        role=role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_auth_template(
            request,
            "signup.html",
            {
                "error": "Username or email already exists.",
                "form": {"username": username, "email": email, "role": role},
            },
            status_code=400,
        )
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    set_auth_cookie(response, token)
    return response


@router.get("/login")
def login_page(request: Request):
    return render_auth_template(request, "login.html", {"error": None, "username_or_email": ""})


@router.post("/login")
def login(
    request: Request,
    username_or_email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, username_or_email.strip(), password)
    if not user:
        return render_auth_template(
            request,
            "login.html",
            {
                "error": "Invalid username/email or password.",
                "username_or_email": username_or_email,
            },
            status_code=400,
        )
    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    set_auth_cookie(response, token)
    return response


@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_auth_cookie(response)
    return response
